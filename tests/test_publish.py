import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("publish", ROOT / "scripts/publish.py")
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)
import reconcile  # noqa: E402

_, KEYS, _ = reconcile.load_manifest(ROOT)
RELEASED = {k: i for k, i in KEYS.items() if i["label"] == "released-reference"}


class FakeSkills:
    """Notion Skills pages of the released references, with failures injected per (operation, key)."""

    def __init__(self, public="content"):
        self.pages, self.failures, self.public, self.writes, self.receipts = {}, {}, public, [], []
        for key, item in RELEASED.items():
            version = reconcile.git_skill_version(ROOT, item["path"])
            files = publish.desired_files(ROOT, item, version)
            pin = reconcile.git(ROOT, "log", "-1", "--format=%H", "--", item["path"]).strip()
            self.pages[item["notion"]] = {"files": {k: v.decode() for k, v in files.items()}, "Version": version, "Status": "Released reference",
                                          "Source": f"{reconcile.REPO_URL}/blob/{pin}/{item['path']}/SKILL.md",
                                          "public_url": f"https://example.invalid/{key}"}

    def _fail(self, operation, page, apply):
        modes = self.failures.get((operation, page)) or [None]
        mode = modes.pop(0)
        if mode == "access":
            raise publish.AccessError("HTTP 401 (expired)")
        if mode == "lost":
            raise publish.UncertainWrite("timeout before apply")
        apply()
        if mode == "applied":
            raise publish.UncertainWrite("timeout after apply")

    def read(self, page, name):
        self._fail("read", page, lambda: None)
        state = self.pages[page]
        return {**{k: v for k, v in state.items() if k != "files"}, "files": dict(state["files"]), "revision": f"v-{page}",
                "types": {"Version": "rich_text", "Status": "select", "Source": "rich_text"}}

    def upload(self, page, name, files):
        def apply():
            self.pages[page]["files"] = {k: v.decode() for k, v in files.items()}
            self.writes.append(("upload", page))
        self._fail("upload", page, apply)

    def set_properties(self, page, values, types):
        def apply():
            self.pages[page].update(values)
            self.writes.append(("properties", page))
        self._fail("properties", page, apply)

    def public_receipt(self, url, markers):
        """Anonymous responses as a site can return them; only real content may verify."""
        self.receipts.append(url)
        page = next(p for p in self.pages.values() if p["public_url"] == url)
        responses = {"content": (200, url, page["files"]["SKILL.md"] + " " + page["Version"]),
                     "login": (200, url, "<html><title>Log in</title>Continue with email</html>"),
                     "shell": (200, url, "<html><div id=\"notion-app\"></div><script src=app.js></script></html>"),
                     "redirect": (200, "https://www.notion.so/login", page["files"]["SKILL.md"]),
                     "forbidden": (403, url, "")}
        status, final, body = responses[self.public]
        return publish.verify_receipt({"url": url, "markers": markers, "verified": False, "status": status, "final_url": final}, body)


class FakeStatus:
    def __init__(self):
        self.states = []

    def set(self, state, description):
        self.states.append((state, description))


def action(key, **change):
    item = RELEASED[key]
    pin = reconcile.git(ROOT, "log", "-1", "--format=%H", "--", item["path"]).strip()
    return {"key": key, "page": item["notion"], "path": item["path"], "version": reconcile.git_skill_version(ROOT, item["path"]),
            "status": "Released reference", "source": f"{reconcile.REPO_URL}/blob/{pin}/{item['path']}/SKILL.md", **change}


class PublishTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.lock = Path(self.temporary.name) / "lock"
        self.target, self.status = FakeSkills(), FakeStatus()
        self.review = RELEASED["skill/factory-review"]["notion"]

    def tearDown(self):
        self.temporary.cleanup()

    def run_actions(self, actions):
        return publish.run(ROOT, actions, KEYS, self.target, self.status, self.lock)

    def damage(self):
        page = self.target.pages[self.review]
        page["files"]["SKILL.md"] = page["files"]["SKILL.md"].replace("Use a context separate", "Use any context", 1)
        page["Status"] = "Draft"

    def test_no_op_is_success_only_after_readback_and_anonymous_access(self):
        result = self.run_actions([])
        self.assertEqual(result["result"], "NO-OP")
        self.assertEqual(self.status.states[0][0], "pending")
        self.assertEqual(self.status.states[-1][0], "success")
        self.assertEqual(self.target.writes, [])

    def test_http_200_without_the_expected_public_content_is_never_success(self):
        for response in ("forbidden", "login", "shell", "redirect"):
            with self.subTest(response):
                self.target.public, self.status.states = response, []
                result = self.run_actions([])
                self.assertEqual(result["result"], "PUBLIC-READBACK-PENDING")
                self.assertEqual(self.status.states[-1][0], "pending")
                self.assertIn("public browser readback pending", self.status.states[-1][1])
                checklist = result["browser_checklist"]
                self.assertEqual(len(checklist), len(RELEASED))
                self.assertTrue(all(c["url"] and len(c["markers"]) == 3 and not c["verified"] for c in checklist))

    def test_public_receipt_covers_the_changed_pages_with_their_content(self):
        self.damage()
        result = self.run_actions([action("skill/factory-review")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(self.target.receipts, [self.target.pages[self.review]["public_url"]])
        self.assertIn("0.1.18", result["public"][0]["markers"])

    def test_final_readback_checks_properties_of_the_whole_set_even_without_actions(self):
        other = RELEASED["skill/factory-spec"]["notion"]
        self.target.pages[other]["Status"] = "Draft"  # drift on a page the plan did not touch
        result = self.run_actions([])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("skill/factory-spec", result["reason"])
        self.assertIn("Status", result["reason"])
        self.assertEqual(self.status.states[-1][0], "failure")

    def test_concurrent_property_drift_after_a_write_is_caught(self):
        self.damage()
        original = self.target.set_properties

        def racing(page, values, types):
            original(page, values, types)
            if page == self.review and ("race", page) not in self.target.writes:
                self.target.writes.append(("race", page))
                spec = RELEASED["skill/factory-spec"]["notion"]
                self.target.pages[spec]["Version"] = "0.0.9"
        self.target.set_properties = racing
        result = self.run_actions([action("skill/factory-review")])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("skill/factory-spec", result["reason"])

    def test_receipts_record_revision_and_file_identity_for_every_page(self):
        result = self.run_actions([])
        self.assertEqual(set(result["receipts"]), set(RELEASED))
        receipt = result["receipts"]["skill/factory-review"]
        self.assertEqual(receipt["revision"], f"v-{self.review}")
        self.assertEqual(set(receipt["files"]), set(self.target.pages[self.review]["files"]))
        self.assertTrue(all(len(h) == 64 for h in receipt["files"].values()))

    def test_unreleased_change_is_release_pending_not_failure(self):
        page = self.target.pages[self.review]
        page["Source"] = f"{reconcile.REPO_URL}/blob/{'0' * 40}/adlc/factory-review/SKILL.md"
        result = self.run_actions([])
        self.assertEqual(result["result"], "RELEASE-PENDING")
        self.assertEqual(result["pending_release"], ["skill/factory-review"])
        self.assertEqual(self.status.states[-1][0], "pending")
        self.assertEqual(self.target.writes, [])

    def test_a_newer_notion_copy_is_never_downgraded(self):
        self.damage()
        self.target.pages[self.review]["Version"] = "9.9.9"
        result = self.run_actions([action("skill/factory-review")])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("refusing a downgrade", result["reason"])
        self.assertEqual(self.target.writes, [])

    def test_damaged_copy_is_restored_body_and_properties(self):
        self.damage()
        result = self.run_actions([action("skill/factory-review")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(self.target.writes, [("upload", self.review), ("properties", self.review)])
        self.assertIn("Use a context separate", self.target.pages[self.review]["files"]["SKILL.md"])
        self.assertIn("Pinned released reference", self.target.pages[self.review]["files"]["SKILL.md"])
        self.assertEqual(self.target.pages[self.review]["Status"], "Released reference")

    def test_changed_property_content_with_equal_body_updates_only_properties(self):
        self.target.pages[self.review]["Source"] = "edited by hand"
        result = self.run_actions([action("skill/factory-review")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(self.target.writes, [("properties", self.review)])

    def test_repeat_delivery_writes_nothing(self):
        self.damage()
        self.run_actions([action("skill/factory-review")])
        writes = list(self.target.writes)
        self.assertEqual(self.run_actions([action("skill/factory-review")])["result"], "PUBLISHED")
        self.assertEqual(self.target.writes, writes)

    def test_uncertain_upload_that_was_applied_is_read_back_not_repeated(self):
        self.damage()
        self.target.failures[("upload", self.review)] = ["applied"]
        result = self.run_actions([action("skill/factory-review")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual([w for w in self.target.writes if w[0] == "upload"], [("upload", self.review)])
        self.assertIn("upload-confirmed-after-uncertain-write", [e["action"] for e in result["log"]])

    def test_lost_upload_is_retried_once_with_the_same_identity(self):
        self.damage()
        self.target.failures[("upload", self.review)] = ["lost"]
        self.assertEqual(self.run_actions([action("skill/factory-review")])["result"], "PUBLISHED")

    def test_partial_failure_stays_visible_and_a_later_run_completes(self):
        self.damage()
        self.target.failures[("properties", self.review)] = ["lost", "lost"]
        result = self.run_actions([action("skill/factory-review")])
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(self.status.states[-1][0], "failure")
        self.assertIn("Use a context separate", self.target.pages[self.review]["files"]["SKILL.md"])  # applied part kept
        self.assertEqual(self.run_actions([action("skill/factory-review")])["result"], "PUBLISHED")
        self.assertEqual(self.status.states[-1][0], "success")

    def test_expired_access_stops_with_a_failure_receipt(self):
        self.damage()
        self.target.failures[("upload", self.review)] = ["access"]
        result = self.run_actions([action("skill/factory-review")])
        self.assertEqual(result["result"], "FAILED-ACCESS")
        self.assertEqual(self.status.states[-1][0], "failure")
        self.assertFalse(self.lock.exists())

    def test_final_readback_covers_every_released_reference(self):
        other = RELEASED["skill/factory-spec"]["notion"]
        page = self.target.pages[other]
        page["files"]["SKILL.md"] += "\nInjected.\n"
        result = self.run_actions([])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("skill/factory-spec", result["reason"])

    def test_concurrent_run_is_refused(self):
        self.lock.write_text("held")
        self.assertEqual(self.run_actions([])["result"], "BUSY")
        self.assertEqual(self.status.states, [])

    def test_notion_owned_originals_are_never_planned(self):
        self.assertTrue(all(KEYS[a["key"]]["owner"] == "git" for a in [action(k) for k in RELEASED]))
        with tempfile.TemporaryDirectory() as temporary:
            snap = {"format": 1, "errors": [], "artifacts": {"skill/factory-agent-ops": {"revision": "x", "version": "9.9.9", "files": {"SKILL.md": "---\nname: x\n---\nchanged"}}}}
            (Path(temporary) / "snapshot.json").write_text(json.dumps(snap))
            self.assertEqual(reconcile.plan(ROOT, KEYS, temporary), [])

    def test_a_notion_owned_action_is_refused_before_any_write(self):
        item = KEYS["skill/factory-agent-ops"]
        result = self.run_actions([{**action("skill/factory-review"), "key": "skill/factory-agent-ops", "page": item["notion"]}])
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(self.target.writes, [])

    def test_release_plan_restores_a_released_reference_but_never_a_notion_original(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", ".factory-task"))
            for command in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "release"], ["tag", "v" + (repo / "VERSION").read_text().strip()]):
                subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *command], cwd=repo, check=True, capture_output=True)
            target = FakeSkills()
            artifacts = {}
            for key, item in KEYS.items():
                if item["kind"] == "skill" and item.get("path"):
                    files = {k: v.decode() for k, v in reconcile.bundle_files(repo, item["path"]).items()}
                    artifacts[key] = {"revision": (item.get("binding") or {}).get("revision", "x"), "version": reconcile.git_skill_version(repo, item["path"]), "files": files}
                    if item["label"] == "released-reference":
                        head = reconcile.git(repo, "rev-parse", "HEAD").strip()
                        page = target.pages[item["notion"]]
                        artifacts[key].update(files=page["files"], version=page["Version"], status=page["Status"],
                                              source=f"{reconcile.REPO_URL}/blob/{head}/{item['path']}/SKILL.md")
            artifacts["skill/factory-agent-ops"]["files"]["SKILL.md"] += "\nNewer canonical rule.\n"
            artifacts["skill/factory-agent-ops"]["revision"] = "newer"
            artifacts["skill/factory-review"]["status"] = "Draft"
            (Path(temporary) / "snapshot.json").write_text(json.dumps({"format": 1, "errors": [], "artifacts": artifacts}))
            _, keys, _ = reconcile.load_manifest(repo)
            plan = reconcile.plan(repo, keys, temporary)
        self.assertEqual([a["key"] for a in plan], ["skill/factory-review"])

    def test_live_mode_without_dedicated_connection_reports_missing_setup(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("FACTORY_PUBLIC_DOCS_")}
        env["FACTORY_NOTION_TOKEN"] = "must-not-be-used"
        with tempfile.TemporaryDirectory() as temporary:
            (Path(temporary) / "snapshot.json").write_text(json.dumps({"format": 1, "errors": [], "artifacts": {}}))
            result = subprocess.run([sys.executable, str(ROOT / "scripts/publish.py"), "--snapshot", temporary, "--live"], cwd=ROOT, env=env,
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn("not configured: FACTORY_PUBLIC_DOCS_TOKEN", result.stdout)
        self.assertNotIn("must-not-be-used", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
