import http.client
import http.server
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import threading
import unittest
from unittest.mock import patch
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("publish", ROOT / "scripts/publish.py")
publish = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publish)
import reconcile  # noqa: E402

# A disposable Git fixture includes a second released reference so whole-set
# readback/race tests remain meaningful when production ships only one domain method.
_SOURCE_ROOT = ROOT
_FIXTURE = tempfile.TemporaryDirectory(prefix="publisher-contract-")
ROOT = Path(_FIXTURE.name) / "repo"
shutil.copytree(_SOURCE_ROOT, ROOT, ignore=shutil.ignore_patterns(".git", "__pycache__", ".agentic-system-task"))
manifest = ROOT / reconcile.MANIFEST
data = json.loads(manifest.read_text())
original = next(i for i in data["artifacts"] if i["key"] == "skill/factory-security")
original.pop("cutover", None)  # Tests explicitly add the exception when it is relevant.
second = {**original, "key": "skill/publisher-second", "path": "defence/publisher-second",
          "notion": "00000000-0000-0000-0000-000000000002"}
second.pop("cutover", None)
shutil.copytree(ROOT / original["path"], ROOT / second["path"])
skill = ROOT / second["path"] / "SKILL.md"
skill.write_text(skill.read_text().replace("name: agentic-security", "name: publisher-second"))
data["artifacts"].append(second)
manifest.write_text(json.dumps(data))
# An earlier release of the second reference carried a file that the tagged release retires.
RETIRED, RETIRED_TEXT = "references/retired.md", "Guidance the next release retires.\n"
(ROOT / second["path"] / "references").mkdir()
(ROOT / second["path"] / RETIRED).write_text(RETIRED_TEXT)
for args in (["init", "-q"], ["add", "-A"], ["commit", "-qm", "earlier release"], ["rm", "-q", f"{second['path']}/{RETIRED}"],
             ["commit", "-qm", "publisher fixture"], ["tag", "v" + (ROOT / "VERSION").read_text().strip()]):
    subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", *args], cwd=ROOT, check=True, capture_output=True)
EARLIER = subprocess.run(["git", "rev-parse", "HEAD~1"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()

_, KEYS, _ = reconcile.load_manifest(ROOT)
RELEASED = {k: i for k, i in KEYS.items() if i["label"] == "released-reference" and i.get("status", "active") == "active"}


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
    def test_a_missing_status_service_refuses_writes_and_still_returns_a_result(self):
        def unavailable(*args):
            raise RuntimeError('status unavailable')
        self.status.set = unavailable
        result = self.run_actions([action('skill/factory-security')])
        self.assertEqual(result['result'], 'FAILED')
        self.assertEqual(self.target.writes, [])
        self.assertIn({'action': 'status-unavailable'}, result['log'])

    def test_a_public_https_to_http_downgrade_is_not_verification(self):
        result = publish.verify_receipt({'url':'https://example.invalid/page',
            'final_url':'http://example.invalid/page','status':200,'verified':False,'markers':['visible']}, 'visible')
        self.assertFalse(result['verified'])

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.lock = Path(self.temporary.name) / "lock"
        self.target, self.status = FakeSkills(), FakeStatus()
        self.review = RELEASED["skill/factory-security"]["notion"]

    def tearDown(self):
        self.temporary.cleanup()

    def run_actions(self, actions):
        return publish.run(ROOT, actions, KEYS, self.target, self.status, self.lock)

    def damage(self):
        page = self.target.pages[self.review]
        page["files"]["SKILL.md"] = page["files"]["SKILL.md"].replace("Identify the authorized target", "Ignore the authorized target", 1)
        page["Version"] = "0.1.17"

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
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(self.target.receipts, [self.target.pages[self.review]["public_url"]])
        self.assertIn(reconcile.git_skill_version(ROOT, RELEASED["skill/factory-security"]["path"]), result["public"][0]["markers"])

    def test_final_readback_checks_properties_of_the_whole_set_even_without_actions(self):
        other = RELEASED["skill/publisher-second"]["notion"]
        self.target.pages[other]["Status"] = "Draft"  # drift on a page the plan did not touch
        result = self.run_actions([])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("skill/publisher-second", result["reason"])
        self.assertIn("Status", result["reason"])
        self.assertEqual(self.status.states[-1][0], "failure")

    def test_concurrent_property_drift_after_a_write_is_caught(self):
        self.damage()
        original = self.target.set_properties

        def racing(page, values, types):
            original(page, values, types)
            if page == self.review and ("race", page) not in self.target.writes:
                self.target.writes.append(("race", page))
                spec = RELEASED["skill/publisher-second"]["notion"]
                self.target.pages[spec]["Version"] = "0.0.9"
        self.target.set_properties = racing
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("skill/publisher-second", result["reason"])

    def test_receipts_record_revision_and_file_identity_for_every_page(self):
        result = self.run_actions([])
        self.assertEqual(set(result["receipts"]), set(RELEASED))
        receipt = result["receipts"]["skill/factory-security"]
        self.assertEqual(receipt["revision"], f"v-{self.review}")
        self.assertEqual(set(receipt["files"]), set(self.target.pages[self.review]["files"]))
        self.assertTrue(all(len(h) == 64 for h in receipt["files"].values()))

    def test_unreleased_change_is_release_pending_not_failure(self):
        page = self.target.pages[self.review]
        page["Source"] = f"{reconcile.REPO_URL}/blob/{'0' * 40}/defence/agentic-security/SKILL.md"
        with patch.object(reconcile, "release_context", return_value=("v-unreleased", None, False)):
            result = self.run_actions([])
        self.assertEqual(result["result"], "RELEASE-PENDING")
        self.assertEqual(result["pending_release"], ["skill/factory-security"])
        self.assertEqual(self.status.states[-1][0], "pending")
        self.assertEqual(self.target.writes, [])

    def test_forged_or_wrong_sources_are_never_a_successful_readback(self):
        pin = reconcile.git(ROOT, "log", "-1", "--format=%H", "--", "defence/agentic-security").strip()
        good = self.target.pages[self.review]["Source"]
        for source in (good.replace("arcitai/agentic-system", "attacker/fork"), good.replace("agentic-security", "agentic-other"),
                       f"javascript:alert(1)//x/blob/{pin}/"):
            with self.subTest(source):
                self.target.pages[self.review]["Source"], self.status.states = source, []
                result = self.run_actions([])
                self.assertNotIn(result["result"], ("NO-OP", "PUBLISHED"))
                self.assertNotEqual(self.status.states[-1][0], "success")

    def test_a_page_that_is_not_a_released_reference_copy_is_never_written(self):
        for status in ("Authoring edition", "Draft", None):
            with self.subTest(status):
                self.target.writes = []
                self.damage()
                self.target.pages[self.review]["Status"] = status
                result = self.run_actions([action("skill/factory-security")])
                self.assertEqual(result["result"], "FAILED")
                self.assertIn("not a released-reference copy", result["reason"])
                self.assertEqual(self.target.writes, [])

    def test_a_cutover_record_allows_taking_over_a_page(self):
        self.damage()
        self.target.pages[self.review]["Status"] = "Authoring edition"
        keys = {k: dict(v) for k, v in KEYS.items()}
        keys["skill/factory-security"]["cutover"] = "https://github.com/arcitai/agentic-system/issues/122#decision"
        result = publish.run(ROOT, [action("skill/factory-security")], keys, self.target, self.status, self.lock)
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(self.target.pages[self.review]["Status"], "Released reference")

    def test_stale_manual_plan_cannot_publish_a_retired_reference(self):
        keys = {k: dict(v) for k, v in KEYS.items()}
        keys["skill/factory-security"]["status"] = "retired"
        result = publish.run(ROOT, [action("skill/factory-security")], keys, self.target, self.status, self.lock)
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("only active Git-owned", result["reason"])
        self.assertEqual(self.target.writes, [])

    def test_a_newer_notion_copy_is_never_downgraded(self):
        self.damage()
        self.target.pages[self.review]["Version"] = "9.9.9"
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("refusing a downgrade", result["reason"])
        self.assertEqual(self.target.writes, [])

    def test_an_older_checkout_never_moves_a_newer_source_pin_back(self):
        head = reconcile.git(ROOT, "rev-parse", "HEAD").strip()
        tree = reconcile.git(ROOT, "rev-parse", "HEAD^{tree}").strip()
        future = subprocess.run(["git", "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                                 "commit-tree", tree, "-p", head], cwd=ROOT, input=b"Later identical skill\n",
                                capture_output=True, check=True).stdout.decode().strip()
        item = KEYS["skill/factory-security"]
        newer_source = f"{reconcile.REPO_URL}/blob/{future}/{item['path']}/SKILL.md"
        self.target.pages[self.review]["Source"] = newer_source
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("refusing to move it back", result["reason"])
        self.assertEqual(self.target.pages[self.review]["Source"], newer_source)
        self.assertEqual(self.target.writes, [])

    def test_an_import_does_not_overwrite_a_concurrent_property_edit(self):
        self.damage()
        upload = self.target.upload
        def edited_after_import(page, name, files):
            upload(page, name, files)
            self.target.pages[page]["Source"] = "https://example.invalid/owner-correction"
        self.target.upload = edited_after_import
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("preserving the concurrent edit", result["reason"])
        self.assertEqual(self.target.pages[self.review]["Source"], "https://example.invalid/owner-correction")
        self.assertFalse(any(operation == "properties" for operation, _ in self.target.writes))

    def test_an_unavailable_source_commit_is_not_silently_repinned(self):
        item = KEYS['skill/factory-security']
        source = f"{reconcile.REPO_URL}/blob/{'f' * 40}/{item['path']}/SKILL.md"
        self.target.pages[self.review]['Source'] = source
        result = self.run_actions([action('skill/factory-security')])
        self.assertEqual(result['result'], 'FAILED')
        self.assertIn('fetch full history', result['reason'])
        self.assertEqual(self.target.pages[self.review]['Source'], source)
        self.assertEqual(self.target.writes, [])

    def test_damaged_copy_is_restored_body_and_properties(self):
        self.damage()
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(self.target.writes, [("upload", self.review), ("properties", self.review)])
        self.assertIn("Identify the authorized target", self.target.pages[self.review]["files"]["SKILL.md"])
        self.assertIn("Pinned released reference", self.target.pages[self.review]["files"]["SKILL.md"])
        self.assertEqual(self.target.pages[self.review]["Version"], reconcile.git_skill_version(ROOT, RELEASED["skill/factory-security"]["path"]))

    def test_changed_property_content_with_equal_body_updates_only_properties(self):
        self.target.pages[self.review]["Source"] = "edited by hand"
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(self.target.writes, [("properties", self.review)])

    def test_repeat_delivery_writes_nothing(self):
        self.damage()
        self.run_actions([action("skill/factory-security")])
        writes = list(self.target.writes)
        self.assertEqual(self.run_actions([action("skill/factory-security")])["result"], "PUBLISHED")
        self.assertEqual(self.target.writes, writes)

    def test_uncertain_upload_that_was_applied_is_read_back_not_repeated(self):
        self.damage()
        self.target.failures[("upload", self.review)] = ["applied"]
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual([w for w in self.target.writes if w[0] == "upload"], [("upload", self.review)])
        self.assertIn("upload-confirmed-after-uncertain-write", [e["action"] for e in result["log"]])

    def test_lost_upload_is_retried_once_with_the_same_identity(self):
        self.damage()
        self.target.failures[("upload", self.review)] = ["lost"]
        self.assertEqual(self.run_actions([action("skill/factory-security")])["result"], "PUBLISHED")

    def test_partial_failure_stays_visible_and_a_later_run_completes(self):
        self.damage()
        self.target.failures[("properties", self.review)] = ["lost", "lost"]
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(self.status.states[-1][0], "failure")
        self.assertIn("Identify the authorized target", self.target.pages[self.review]["files"]["SKILL.md"])  # applied part kept
        self.assertEqual(self.run_actions([action("skill/factory-security")])["result"], "PUBLISHED")
        self.assertEqual(self.status.states[-1][0], "success")

    def test_expired_access_stops_with_a_failure_receipt(self):
        self.damage()
        self.target.failures[("upload", self.review)] = ["access"]
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED-ACCESS")
        self.assertEqual(self.status.states[-1][0], "failure")
        self.assertFalse(self.lock.exists())

    def test_final_readback_covers_every_released_reference(self):
        other = RELEASED["skill/publisher-second"]["notion"]
        page = self.target.pages[other]
        page["files"]["SKILL.md"] += "\nInjected.\n"
        result = self.run_actions([])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("skill/publisher-second", result["reason"])

    def test_concurrent_run_is_refused(self):
        self.lock.write_text("held")
        self.assertEqual(self.run_actions([])["result"], "BUSY")
        self.assertEqual(self.status.states, [])

    def test_notion_owned_originals_are_never_planned(self):
        self.assertTrue(all(KEYS[a["key"]]["owner"] == "git" for a in [action(k) for k in RELEASED]))
        with tempfile.TemporaryDirectory() as temporary:
            snap = {"format": 1, "errors": [], "artifacts": {"skill/factory-foundation": {"revision": "x", "version": "9.9.9", "files": {"SKILL.md": "---\nname: x\n---\nchanged"}}}}
            (Path(temporary) / "snapshot.json").write_text(json.dumps(snap))
            actions = reconcile.plan(ROOT, KEYS, temporary)
            self.assertNotIn("skill/factory-foundation", [a["key"] for a in actions])
            self.assertTrue(all(KEYS[a["key"]]["owner"] == "git" for a in actions))

    def test_a_notion_owned_action_is_refused_before_any_write(self):
        item = KEYS["skill/factory-foundation"]
        result = self.run_actions([{**action("skill/factory-security"), "key": "skill/factory-foundation", "page": item["notion"]}])
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(self.target.writes, [])

    def test_release_plan_restores_a_released_reference_but_never_a_notion_original(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary) / "repo"
            shutil.copytree(ROOT, repo, ignore=shutil.ignore_patterns(".git", "__pycache__", ".agentic-system-task"))
            for command in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "release"], ["tag", "v" + (repo / "VERSION").read_text().strip()]):
                subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *command], cwd=repo, check=True, capture_output=True)
            target = FakeSkills()
            artifacts = {}
            for key, item in KEYS.items():
                if item["kind"] == "skill" and item.get("path") and item.get("status", "active") == "active":
                    files = {k: v.decode() for k, v in reconcile.bundle_files(repo, item["path"]).items()}
                    artifacts[key] = {"revision": (item.get("binding") or {}).get("revision", "x"), "version": reconcile.git_skill_version(repo, item["path"]), "files": files}
                    if item["label"] == "released-reference":
                        head = reconcile.git(repo, "rev-parse", "HEAD").strip()
                        page = target.pages[item["notion"]]
                        artifacts[key].update(files=page["files"], version=page["Version"], status=page["Status"],
                                              source=f"{reconcile.REPO_URL}/blob/{head}/{item['path']}/SKILL.md")
            artifacts["skill/factory-foundation"]["files"]["SKILL.md"] += "\nNewer canonical rule.\n"
            artifacts["skill/factory-foundation"]["revision"] = "newer"
            artifacts["skill/factory-security"]["status"] = "Draft"
            (Path(temporary) / "snapshot.json").write_text(json.dumps({"format": 1, "errors": [], "artifacts": artifacts}))
            _, keys, _ = reconcile.load_manifest(repo)
            plan = reconcile.plan(repo, keys, temporary)
        self.assertEqual([a["key"] for a in plan], ["skill/factory-security"])

    def test_matching_properties_are_not_rewritten_with_a_restored_body(self):
        page = self.target.pages[self.review]
        page["files"]["SKILL.md"] = page["files"]["SKILL.md"].replace("Identify the authorized target", "Ignore the authorized target", 1)
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "PUBLISHED")
        self.assertEqual(self.target.writes, [("upload", self.review)])

    def test_only_the_differing_property_is_written(self):
        self.target.pages[self.review]["Source"] = "edited by hand"
        sent = []
        original = self.target.set_properties
        self.target.set_properties = lambda page, values, types: (sent.append(dict(values)), original(page, values, types))
        self.assertEqual(self.run_actions([action("skill/factory-security")])["result"], "PUBLISHED")
        self.assertEqual([sorted(v) for v in sent], [["Source"]])

    def concurrent_edit_during(self, operation, edit, mode):
        """The write's outcome is unknown and, before the readback, somebody else edits the same page."""
        original = getattr(self.target, operation)
        calls = []

        def racing(page, *args):
            calls.append(page)
            if len(calls) == 1:
                edit(self.target.pages[page])
                raise publish.UncertainWrite(f"timeout {mode} apply")
            original(page, *args)
        setattr(self.target, operation, racing)
        return calls

    def test_an_uncertain_upload_does_not_overwrite_a_concurrent_edit(self):
        self.damage()

        def edit(page):
            page["files"]["SKILL.md"] += "\nA correction someone saved while the upload was in flight.\n"
        calls = self.concurrent_edit_during("upload", edit, "before")
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("neither the intended result nor the state read before the write", result["reason"])
        self.assertEqual(len(calls), 1)  # no retry over the other edit
        self.assertEqual(self.target.writes, [])
        self.assertIn("A correction someone saved", self.target.pages[self.review]["files"]["SKILL.md"])
        self.assertEqual(self.status.states[-1][0], "failure")

    def test_an_uncertain_property_write_does_not_overwrite_a_concurrent_takeover(self):
        self.target.pages[self.review]["Source"] = "edited by hand"
        calls = self.concurrent_edit_during("set_properties", lambda page: page.update(Source="pinned by the owner meanwhile"), "before")
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.target.pages[self.review]["Source"], "pinned by the owner meanwhile")

    def test_an_unreadable_page_after_an_uncertain_upload_is_not_retried_blindly(self):
        self.damage()
        calls = self.concurrent_edit_during("upload", lambda page: None, "before")
        self.target.failures[("read", self.review)] = [None, "lost"]
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.target.writes, [])

    def test_an_attachment_git_never_released_is_not_deleted_by_the_packet_upload(self):
        self.damage()
        self.target.pages[self.review]["files"]["references/field-notes.md"] = "Attached on the Notion page.\n"
        result = self.run_actions([action("skill/factory-security")])
        self.assertEqual(result["result"], "FAILED")
        self.assertIn("references/field-notes.md", result["reason"])
        self.assertIn("would delete it", result["reason"])
        self.assertEqual(self.target.writes, [])
        self.assertIn("references/field-notes.md", self.target.pages[self.review]["files"])

    def test_a_file_retired_by_the_release_is_removed_only_if_the_pinned_release_holds_it(self):
        item = RELEASED["skill/publisher-second"]
        for text, expected in ((RETIRED_TEXT, "PUBLISHED"), (RETIRED_TEXT + "Edited on the Notion page.\n", "FAILED")):
            with self.subTest(expected):
                self.target, self.status = FakeSkills(), FakeStatus()
                page = self.target.pages[item["notion"]]
                page["files"][RETIRED] = text
                page["Source"] = f"{reconcile.REPO_URL}/blob/{EARLIER}/{item['path']}/SKILL.md"
                result = self.run_actions([action("skill/publisher-second")])
                self.assertEqual(result["result"], expected)
                self.assertEqual(RETIRED in page["files"], expected == "FAILED")
                self.assertEqual(self.target.writes, [("upload", item["notion"]), ("properties", item["notion"])] if expected == "PUBLISHED" else [])

    def test_live_mode_without_dedicated_connection_reports_missing_setup(self):
        env = {k: v for k, v in os.environ.items() if not k.startswith("AGENTIC_SYSTEMS_PUBLIC_DOCS_")}
        env["AGENTIC_SYSTEMS_NOTION_TOKEN"] = "must-not-be-used"
        with tempfile.TemporaryDirectory() as temporary:
            (Path(temporary) / "snapshot.json").write_text(json.dumps({"format": 1, "errors": [], "artifacts": {}}))
            result = subprocess.run([sys.executable, str(ROOT / "scripts/publish.py"), "--snapshot", temporary, "--live"], cwd=ROOT, env=env,
                                    capture_output=True, text=True)
        self.assertEqual(result.returncode, 3)
        self.assertIn("not configured: AGENTIC_SYSTEMS_PUBLIC_DOCS_TOKEN", result.stdout)
        self.assertNotIn("must-not-be-used", result.stdout + result.stderr)


class Redirecting(http.server.BaseHTTPRequestHandler):
    """A loopback API that answers every request with a redirect to another host, which records what reaches it."""
    elsewhere, reached = None, []

    def answer(self):
        self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if self.server.server_port == self.elsewhere:
            self.reached.append((self.command, self.headers.get("Authorization")))
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"{}")
        else:
            self.send_response(302)
            self.send_header("Location", f"http://127.0.0.1:{self.elsewhere}/collected")
            self.send_header("Content-Length", "0")
            self.end_headers()
    do_GET = do_POST = do_PATCH = answer

    def log_message(self, *args):
        pass


class TransportTests(unittest.TestCase):
    """The real client classes against injected or loopback transports; no Notion or GitHub request is made."""

    def test_a_redirected_api_request_does_not_carry_the_connection_to_the_new_host(self):
        servers = [http.server.HTTPServer(("127.0.0.1", 0), Redirecting) for _ in range(2)]
        Redirecting.elsewhere, Redirecting.reached = servers[1].server_port, []
        for server in servers:
            threading.Thread(target=server.serve_forever, daemon=True).start()
            self.addCleanup(server.server_close)
            self.addCleanup(server.shutdown)
        api = f"http://127.0.0.1:{servers[0].server_port}/v1"
        with patch.object(publish.notion_snapshot, "API", api), patch.object(publish.NotionSkills, "API", api):
            with self.assertRaises(urllib.error.HTTPError) as raised:
                publish.notion_snapshot.Reader("connection-secret").get("/ai/skills/p")
            self.assertEqual(raised.exception.code, 302)
            raised.exception.close()
            with self.assertRaises(publish.UncertainWrite) as uncertain:
                publish.NotionSkills("connection-secret").upload("p", "agentic-x", {"SKILL.md": b"x"})
            self.assertIn("HTTP 302", str(uncertain.exception))
        self.assertEqual(Redirecting.reached, [])

    def test_a_connection_lost_after_the_request_was_sent_is_an_uncertain_write(self):
        def reset(request, timeout=None):
            raise ConnectionResetError("Connection reset by peer")

        def cut(request, timeout=None):
            raise http.client.RemoteDisconnected("Remote end closed connection without response")

        def empty(request, timeout=None):
            return io.BytesIO(b"")
        for opener in (reset, cut, empty):
            with self.subTest(opener.__name__), self.assertRaises(publish.UncertainWrite):
                publish.NotionSkills("token", opener).upload("p", "agentic-x", {"SKILL.md": b"x"})

    def page(self, members):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
            for name, data in members:
                info = tarfile.TarInfo(name)
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
        signed = "https://files.example/skill.tar.gz?X-Amz-Signature=SIGNED-SECRET"
        replies = {"/pages/p": {"properties": {"Version": {"type": "rich_text", "rich_text": [{"plain_text": "1.0.0"}]}}, "public_url": None},
                   "/ai/skills/p": {"version_id": "opaque/version+id==", "url": signed}}
        seen = []

        def opener(request, timeout=None):
            seen.append((request.full_url, request.get_header("Authorization")))
            if request.full_url == signed:
                return io.BytesIO(buffer.getvalue())
            return io.BytesIO(json.dumps(replies[request.full_url.split("/v1", 1)[1]]).encode())
        return publish.NotionSkills("token", opener), seen, signed

    def test_readback_keeps_the_opaque_revision_and_sends_the_connection_only_to_the_api(self):
        target, seen, signed = self.page([("agentic-x/SKILL.md", b"body")])
        state = target.read("p", "agentic-x")
        self.assertEqual((state["revision"], state["files"], state["Version"]), ("opaque/version+id==", {"SKILL.md": "body"}, "1.0.0"))
        self.assertEqual([auth for url, auth in seen if url != signed], ["Bearer token", "Bearer token"])
        self.assertEqual([auth for url, auth in seen if url == signed], [None])

    def test_a_retained_earlier_folder_stops_the_run_as_a_conflict_not_an_uncertain_write(self):
        target, _, _ = self.page([("agentic-x/SKILL.md", b"new"), ("factory-x/references/earlier.md", b"kept")])
        with self.assertRaises(RuntimeError) as raised:
            target.read("p", "agentic-x")
        self.assertIn("factory-x/references/earlier.md", str(raised.exception))
        self.assertNotIn("SIGNED-SECRET", str(raised.exception))

    def test_an_unreachable_public_page_is_unverified_not_a_crash(self):
        def reset(request, timeout=None):
            raise ConnectionResetError("Connection reset by peer")
        with patch.object(publish.urllib.request, "urlopen", reset):
            receipt = publish.NotionSkills("token").public_receipt("https://example.invalid/page", ["agentic-x"])
        self.assertFalse(receipt["verified"])
        self.assertTrue(receipt["reason"])


if __name__ == "__main__":
    unittest.main()
