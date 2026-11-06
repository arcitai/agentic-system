import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("reconcile", ROOT / "scripts/reconcile.py")
reconcile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reconcile)


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()


def notion_rendering(text, version, preamble):
    """Render a portable skill the way the Notion Skills API returned the 5 Nov 2026 fixtures."""
    lines = text.split("\n")
    end = lines.index("---", 1)
    meta = dict(line.split(": ", 1) for line in lines[1:end] if ": " in line and not line.startswith("  "))
    body = "\n".join(lines[end + 1:])
    body = re.sub(r"^# .*$", preamble, body, count=1, flags=re.M)

    def link(match):
        label, target = match[1], match[2]
        if label == target or label.endswith(".md"):
            return f"`{label}`"
        return f"{label} (`{target}`)"
    body = re.sub(r"\[([^\]]+)\]\((?![a-z]+:)([^)\s]+)\)", link, body)
    body = re.sub(r"(?<=[^\n])\n(?=[^\n-])", "<br />", body)
    return (f"---\nname: |-\n  {meta['name']}\ndescription: |-\n  {meta['description']}\nnotion_page_id: x\n---\n" + body)


class Repo:
    """A disposable Git copy of this checkout."""

    def __init__(self, temporary, test):
        self.root, self.test = Path(temporary) / "repo", test
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".agentic-system-task", "dist"))
        git(self.root, "init", "-q")
        self.commit("base")

    def commit(self, message):
        git(self.root, "add", "-A")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", message)
        return git(self.root, "rev-parse", "HEAD")

    def edit(self, path, old, new):
        target = self.root / path
        text = target.read_text(encoding="utf-8")
        self.test.assertIn(old, text)
        target.write_text(text.replace(old, new, 1), encoding="utf-8")

    def manifest(self, mutate):
        path = self.root / reconcile.MANIFEST
        data = json.loads(path.read_text())
        mutate({i["key"]: i for i in data["artifacts"]}, data["artifacts"])
        path.write_text(json.dumps(data, indent=2))

    def impact(self, base):
        _, keys, errors = reconcile.load_manifest(self.root)
        return errors, reconcile.impact(self.root, keys, base, git(self.root, "rev-parse", "HEAD"))


# A synthetic handoff on a Notion-owned artifact. Tests inject it into their own manifest copy so they
# never depend on which real pending rows docs/sources.json carries.
SYNTHETIC_PENDING = {
    "id": "synthetic-handoff-fixture",
    "action": "replace",
    "holder": "Synthetic canonical writer",
    "before": "Synthetic status sentence before the handoff.",
    "after": "Synthetic status sentence after the handoff.",
}


def with_synthetic_pending(keys, artifact="guide/home"):
    """Give `artifact` exactly the synthetic handoff, replacing any real rows it carries."""
    keys[artifact]["pending"] = [dict(SYNTHETIC_PENDING)]


def levels(items):
    return {(i.get("key"), i["level"]) for i in items}

def current_metadata(path, field):
    return re.search(r'^  ' + field + r': "([^"]+)"$', (ROOT / path).read_text(), re.M)[1]


class ManifestTests(unittest.TestCase):
    def test_current_manifest_maps_every_skill_once(self):
        _, keys, errors = reconcile.load_manifest(ROOT)
        self.assertEqual(errors, [])
        skills = {p.parent.relative_to(ROOT).as_posix() for g in reconcile.GROUPS for p in (ROOT / g).glob("*/SKILL.md")}
        self.assertEqual(skills, {i["path"] for i in keys.values() if i["kind"] == "skill" and i.get("path")})
        exports = [i for i in keys.values() if i["kind"] == "skill" and i["label"] == "export"]
        self.assertTrue(exports and all(i.get("binding", {}).get("revision") for i in exports))

    def test_invalid_manifests_are_rejected(self):
        cases = {
            "duplicate key": lambda k, a: a.append(dict(a[-1])),
            "git cannot own an authoring edition": lambda k, a: k["doc/readme"].update(label="authoring-edition"),
            "private path": lambda k, a: a.append({"key": "doc/private", "kind": "doc", "owner": "git", "label": "main-working", "path": ".agentic-system-task/x"}),
            "escaping path": lambda k, a: a.append({"key": "doc/up", "kind": "doc", "owner": "git", "label": "main-working", "path": "../x"}),
            "notion page id required": lambda k, a: a.append({"key": "guide/x", "kind": "page", "owner": "notion", "label": "authoring-edition"}),
            "skill without entry": lambda k, a: a.remove(k["skill/factory-review"]),
            "binding on a released reference": lambda k, a: k["skill/factory-review"].update(binding={"revision": "r", "version": "1"}),
            "pending without holder": lambda k, a: k["guide/home"].update(pending=[{n: v for n, v in SYNTHETIC_PENDING.items() if n != "holder"}]),
            "pending on a Git-owned artifact": lambda k, a: k["doc/readme"].update(pending=[{"id": "x", "after": "y", "holder": "z"}]),
            "missing kind": lambda k, a: k["doc/vision"].pop("kind"),
            "released-reference page id reused": lambda k, a: k["skill/factory-spec"].update(notion=k["skill/factory-review"]["notion"]),
            "empty cutover record": lambda k, a: k["skill/factory-spec"].update(cutover=""),
        }
        for name, mutate in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary) / "r"
                shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".agentic-system-task"))
                data = json.loads((root / reconcile.MANIFEST).read_text())
                mutate({i["key"]: i for i in data["artifacts"]}, data["artifacts"])
                (root / reconcile.MANIFEST).write_text(json.dumps(data))
                self.assertTrue(reconcile.load_manifest(root)[2], name)

    def test_synthetic_pending_fixture_is_valid_on_a_notion_owned_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "r"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".agentic-system-task"))
            data = json.loads((root / reconcile.MANIFEST).read_text())
            with_synthetic_pending({i["key"]: i for i in data["artifacts"]})
            (root / reconcile.MANIFEST).write_text(json.dumps(data))
            self.assertEqual(reconcile.load_manifest(root)[2], [])


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Repo(self.temporary.name, self)
        self.base = git(self.repo.root, "rev-parse", "HEAD")

    def tearDown(self):
        self.temporary.cleanup()

    def test_unchanged_git_side_without_canonical_is_never_a_no_op(self):
        self.repo.manifest(lambda k, a: with_synthetic_pending(k))
        self.base = self.repo.commit("synthetic pending")
        self.repo.commit("empty")
        result = reconcile.run(self.repo.root, self.base)
        self.assertNotEqual(result["result"], "NO-OP")
        self.assertIn("NOT RUN", result["canonical"])
        self.assertTrue([i for i in result["items"] if i.get("pending") == SYNTHETIC_PENDING["id"]])
        self.repo.manifest(lambda k, a: [i.pop("pending", None) for i in a])
        self.repo.commit("no pending")
        self.assertEqual(reconcile.run(self.repo.root)["result"], "UNVERIFIED (Git side: NO-OP)")

    def test_git_owned_change_is_reported(self):
        self.repo.edit("docs/qualification.md", "#", "# ")
        self.repo.commit("doc")
        self.assertEqual(levels(self.repo.impact(self.base)[1]), {("doc/qualification", "CHANGE")})

    def test_export_edit_without_new_binding_is_a_conflict_with_the_newer_original(self):
        self.repo.edit("agent-ops/agentic-agent-ops/SKILL.md", "Start from the owner's", "Start from the agent's")
        self.repo.commit("export edit")
        self.assertEqual(levels(self.repo.impact(self.base)[1]), {("skill/factory-agent-ops", "CONFLICT")})

    def test_metadata_bump_does_not_disguise_a_git_edit_of_an_export(self):
        self.repo.edit("agent-ops/agentic-entry/SKILL.md", f'version: "{current_metadata("agent-ops/agentic-entry/SKILL.md", "version")}"', 'version: "9.9.9"')
        self.repo.edit("agent-ops/agentic-entry/SKILL.md", f'updated: "{current_metadata("agent-ops/agentic-entry/SKILL.md", "updated")}"', 'updated: "2099-01-01"')
        self.repo.edit("agent-ops/agentic-entry/SKILL.md", "You are the owner's own AI agent.", "You are an AI agent.")
        self.repo.commit("edit with bump")
        self.assertEqual(levels(self.repo.impact(self.base)[1]), {("skill/factory-entry", "CONFLICT")})

    def test_updated_date_alone_does_not_release_a_new_reference_version(self):
        self.repo.edit("adlc/agentic-review/SKILL.md", f'updated: "{current_metadata("adlc/agentic-review/SKILL.md", "updated")}"', 'updated: "2099-01-01"')
        self.repo.edit("adlc/agentic-review/SKILL.md", "Use a context separate", "Use a context apart")
        self.repo.commit("in-place edit")
        self.assertEqual(levels(self.repo.impact(self.base)[1]), {("skill/factory-review", "CONFLICT")})

    def test_ownership_change_needs_an_owner_decision(self):
        self.repo.manifest(lambda k, a: k["skill/factory-evaluate"].update(owner="git", label="main-working", binding=None) or k["skill/factory-evaluate"].pop("binding"))
        self.repo.commit("cutover")
        items = self.repo.impact(self.base)[1]
        self.assertIn("ownership change", next(i for i in items if i.get("key") == "skill/factory-evaluate" and "ownership" in i["reason"])["reason"])

    def test_deliberate_export_with_new_manifest_binding_is_a_change(self):
        self.repo.edit("agent-ops/agentic-agent-ops/SKILL.md", "Start from the owner's", "Start from the agent's")
        self.repo.manifest(lambda k, a: k["skill/factory-agent-ops"]["binding"].update(revision="new-revision"))
        self.repo.commit("export")
        self.assertIn(("skill/factory-agent-ops", "CHANGE"), levels(self.repo.impact(self.base)[1]))

    def test_declaration_export_needs_its_canonical_hash(self):
        self.repo.edit("system.yaml", "status: candidate", "status: adopted")
        self.repo.commit("decl")
        self.assertEqual(levels(self.repo.impact(self.base)[1]), {("declaration/factory-lab", "CONFLICT")})

    def test_released_reference_is_immutable_for_its_version(self):
        self.repo.edit("adlc/agentic-review/SKILL.md", "Use a context separate", "Use a context apart")
        self.repo.commit("rr")
        self.assertEqual(levels(self.repo.impact(self.base)[1]), {("skill/factory-review", "CONFLICT")})
        self.repo.edit("adlc/agentic-review/SKILL.md", f'version: "{current_metadata("adlc/agentic-review/SKILL.md", "version")}"', 'version: "9.9.9"')
        self.repo.commit("rr version")
        self.assertEqual(levels(self.repo.impact(self.base)[1]), {("skill/factory-review", "CHANGE")})

    def test_rename_without_manifest_update_fails_and_with_status_passes(self):
        git(self.repo.root, "mv", "adlc/agentic-spec", "adlc/agentic-specify")
        self.repo.commit("rename")
        self.assertTrue(any("agentic-spec" in e for e in self.repo.impact(self.base)[0]))

        def rename(k, a):
            old = k["skill/factory-spec"]
            a.append({**old, "key": "skill/factory-specify", "path": "adlc/agentic-specify"})
            old.update(status="renamed", renamed_to="skill/factory-specify")
        self.repo.manifest(rename)
        self.repo.commit("manifest")
        errors, items = self.repo.impact(self.base)
        self.assertEqual(errors, [])
        self.assertIn(("skill/factory-spec", "CHANGE"), levels(items))

    def test_retirement_keeps_the_key(self):
        shutil.rmtree(self.repo.root / "adlc/agentic-security")
        self.repo.manifest(lambda k, a: k["skill/factory-security"].update(status="retired"))
        self.repo.commit("retire")
        errors, items = self.repo.impact(self.base)
        self.assertEqual(errors, [])
        self.assertIn(("skill/factory-security", "CHANGE"), levels(items))
        self.assertNotIn("CONFLICT", {i["level"] for i in items})

    def test_manifest_errors_with_a_base_do_not_crash(self):
        self.repo.manifest(lambda k, a: k["skill/factory-entry"].pop("kind"))
        self.repo.edit("agent-ops/agentic-entry/SKILL.md", "You are the owner's own AI agent.", "You are an AI agent.")  # owned by the invalid entry
        self.repo.commit("broken manifest")
        result = reconcile.run(self.repo.root, self.base)
        self.assertEqual(result["result"], "CONFLICT")
        self.assertTrue(any("kind" in i["reason"] for i in result["items"]))

    def test_a_pin_on_a_non_ancestor_commit_is_not_kept(self):
        _, keys, _ = reconcile.load_manifest(self.repo.root)
        item = keys["skill/factory-review"]
        git(self.repo.root, "switch", "-q", "-c", "side")
        side = self.repo.commit("side branch, same bundle")
        git(self.repo.root, "switch", "-q", "-")
        self.repo.commit("main moves on")
        source = f"{reconcile.REPO_URL}/blob/{side}/{item['path']}/SKILL.md"
        self.assertIsNone(reconcile.released_pin(self.repo.root, item, source))
        base_pin = f"{reconcile.REPO_URL}/blob/{self.base}/{item['path']}/SKILL.md"
        self.assertEqual(reconcile.released_pin(self.repo.root, item, base_pin), base_pin)

    def test_an_ancestor_pin_whose_bundle_changed_is_not_kept(self):
        _, keys, _ = reconcile.load_manifest(self.repo.root)
        item = keys["skill/factory-review"]
        self.repo.edit("adlc/agentic-review/SKILL.md", f'version: "{current_metadata("adlc/agentic-review/SKILL.md", "version")}"', 'version: "9.9.9"')
        self.repo.commit("unreleased version bump")
        base_pin = f"{reconcile.REPO_URL}/blob/{self.base}/{item['path']}/SKILL.md"
        self.assertIsNone(reconcile.released_pin(self.repo.root, item, base_pin))  # ancestor, but the bundle changed
        git(self.repo.root, "tag", "v" + (self.repo.root / "VERSION").read_text().strip())
        head = git(self.repo.root, "rev-parse", "HEAD")
        self.assertEqual(reconcile.released_pin(self.repo.root, item, base_pin), f"{reconcile.REPO_URL}/blob/{head}/{item['path']}/SKILL.md")

    def test_moving_a_notion_original_to_git_needs_a_cutover_record(self):
        def flip(k, a):
            k["skill/factory-evaluate"].update(owner="git", label="released-reference")
            k["skill/factory-evaluate"].pop("binding")
        self.repo.manifest(flip)
        self.repo.commit("flip")
        items = self.repo.impact(self.base)[1]
        self.assertEqual(next(i for i in items if "ownership" in i.get("reason", ""))["level"], "CONFLICT")
        self.repo.manifest(lambda k, a: k["skill/factory-evaluate"].update(cutover="https://github.com/arcitai/agentic-systems/issues/122#decision"))
        self.repo.commit("cutover record")
        items = self.repo.impact(self.base)[1]
        self.assertEqual(next(i for i in items if "ownership" in i.get("reason", ""))["level"], "ATTENTION")

    def test_retiring_or_deleting_a_notion_key_cannot_move_its_original_to_git(self):
        for mode in ("retire", "delete"):
            with self.subTest(mode):
                repo = Repo(Path(self.temporary.name) / mode, self)
                base = git(repo.root, "rev-parse", "HEAD")

                def move(k, a):
                    old = k["skill/factory-evaluate"]
                    a.append({**{x: y for x, y in old.items() if x != "binding"}, "key": "skill/factory-evaluate-ref",
                              "owner": "git", "label": "released-reference"})
                    if mode == "retire":
                        old["status"] = "retired"
                    else:
                        a.remove(old)
                repo.manifest(move)
                repo.commit(mode)
                _, keys, errors = reconcile.load_manifest(repo.root)
                items = reconcile.impact(repo.root, keys, base, git(repo.root, "rev-parse", "HEAD"))
                self.assertIn(("skill/factory-evaluate-ref", "CONFLICT"), levels(items))
                if mode == "retire":
                    self.assertTrue(any("page id is also used" in e for e in errors))

    def test_pointing_a_released_reference_at_another_page_is_a_conflict(self):
        self.repo.manifest(lambda k, a: k["skill/factory-review"].update(notion="00000000-0000-0000-0000-000000000001"))
        self.repo.commit("repoint")
        self.assertIn(("skill/factory-review", "CONFLICT"), levels(self.repo.impact(self.base)[1]))

    def test_a_shallow_clone_says_pin_ancestry_is_unverifiable(self):
        self.repo.commit("second")
        shallow = Path(self.temporary.name) / "shallow"
        git(Path(self.temporary.name), "clone", "-q", "--depth", "1", f"file://{self.repo.root}", str(shallow))
        result = reconcile.run(shallow)
        self.assertTrue(any("shallow clone" in i["reason"] and i["level"] == "ATTENTION" for i in result["items"]))
        self.assertNotIn("shallow clone", " ".join(i["reason"] for i in reconcile.run(self.repo.root)["items"]))

    def test_unowned_and_private_paths_are_reported(self):
        (self.repo.root / "notes.md").write_text("x")
        (self.repo.root / "docs/.claude").mkdir()
        (self.repo.root / "docs/.claude/leak.md").write_text("x")
        self.repo.commit("stray")
        items = self.repo.impact(self.base)[1]
        self.assertIn((None, "ATTENTION"), levels(items))
        self.assertIn("CONFLICT", {i["level"] for i in items if i["path"] == "docs/.claude/leak.md"})


class CanonicalTests(unittest.TestCase):
    """Compare the working tree with a synthetic canonical snapshot that renders it the Notion way."""

    def snapshot(self, mutate=lambda s: None, synthetic_pending=False):
        _, keys, _ = reconcile.load_manifest(ROOT)
        if synthetic_pending:
            with_synthetic_pending(keys)
        artifacts = {}
        for key, item in keys.items():
            if item["kind"] == "skill" and item.get("path"):
                folder = ROOT / item["path"]
                version = reconcile.git_skill_version(ROOT, item["path"])
                files = {p.relative_to(folder).as_posix(): p.read_text(encoding="utf-8") for p in folder.rglob("*") if p.is_file()}
                files["SKILL.md"] = notion_rendering(files["SKILL.md"], version, f"Notion authoring edition · {version}")
                artifacts[key] = {"revision": (item.get("binding") or {}).get("revision", "r-" + key), "version": version, "readAt": "t", "files": files}
                if item["label"] == "released-reference":
                    pin = git(ROOT, "log", "-1", "--format=%H", "--", item["path"])
                    artifacts[key].update(status=reconcile.RELEASED_STATUS, source=f"{reconcile.REPO_URL}/blob/{pin}/{item['path']}/SKILL.md")
            elif item["kind"] == "page" and item.get("status", "active") == "active":
                artifacts[key] = {"revision": "t", "text": "\n".join(p.get("before", "") for p in item.get("pending", []))}
        decl = (ROOT / "system.yaml").read_text()
        artifacts["declaration/factory-lab"] = {"revision": "t", "sha256": re.search(r"SHA-256 [^:]*: ([0-9a-f]{64})", decl)[1]}
        snap = {"format": 1, "artifacts": artifacts, "errors": []}
        mutate(snap)
        with tempfile.TemporaryDirectory() as temporary:
            (Path(temporary) / "snapshot.json").write_text(json.dumps(snap))
            items = reconcile.compare(ROOT, keys, temporary)
        return {i["key"]: i for i in items if "pending" not in i}, [i for i in items if "pending" in i], items

    def test_notion_rendering_of_the_same_sources_is_in_sync(self):
        main, _, _ = self.snapshot()
        self.assertEqual({k: v["level"] for k, v in main.items() if v["level"] != "IN-SYNC"}, {})

    def test_one_changed_sentence_is_detected(self):
        def change(s):
            f = s["artifacts"]["skill/factory-foundation"]["files"]
            f["SKILL.md"] = f["SKILL.md"].replace("Assessment is read-only.", "Assessment may write.", 1)
        self.assertEqual(self.snapshot(change)[0]["skill/factory-foundation"]["level"], "CONFLICT")

    def test_a_changed_link_target_is_detected(self):
        def change(s):
            f = s["artifacts"]["skill/factory-agent-ops"]["files"]
            self.assertIn("(`references/t3.md`)", f["SKILL.md"])
            f["SKILL.md"] = f["SKILL.md"].replace("(`references/t3.md`)", "(`references/policy.md`)", 1)
        self.assertEqual(self.snapshot(change)[0]["skill/factory-agent-ops"]["level"], "CONFLICT")

    def test_newer_canonical_revision_is_pending_export_never_overwritten(self):
        def newer(s):
            a = s["artifacts"]["skill/factory-agent-ops"]
            a.update(revision="newer", version="9.9.9")
            a["files"]["SKILL.md"] += "\nNew canonical rule.\n"
        item = self.snapshot(newer)[0]["skill/factory-agent-ops"]
        self.assertEqual(item["level"], "ATTENTION")
        self.assertIn("never overwrite Notion from Git", item["reason"])

    def test_declaration_body_is_hashed_not_just_its_header_claim(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "r"
            shutil.copytree(ROOT, root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".agentic-system-task"))
            decl = root / "system.yaml"
            text = decl.read_text()
            canonical = re.search(r"SHA-256 [^:]*: ([0-9a-f]{64})", text)[1]
            _, keys, _ = reconcile.load_manifest(root)
            snap = Path(temporary) / "snap"
            snap.mkdir()
            (snap / "snapshot.json").write_text(json.dumps({"format": 1, "errors": [], "artifacts": {"declaration/factory-lab": {"revision": "t", "sha256": canonical}}}))
            level = lambda: next(i for i in reconcile.compare(root, keys, snap) if i["key"] == "declaration/factory-lab")["level"]
            self.assertEqual(level(), "IN-SYNC")
            decl.write_text(text.replace("status: candidate", "status: candidate\nmalicious: true"))
            self.assertEqual(level(), "CONFLICT")  # header unchanged, body edited
            for injected in ("approval: automatic\n" + text, text.replace("# Edit the original", "approval: automatic\n# Edit the original", 1)):
                decl.write_text(injected)
                self.assertEqual(level(), "CONFLICT")  # a YAML key in the header block is never in sync
            body = text.split("\n\n", 1)[1] + "extra: 1\n"
            new = hashlib.sha256(body.encode()).hexdigest()
            decl.write_text(text.split("\n\n", 1)[0].replace(canonical, new) + "\n\n" + body)
            self.assertEqual(level(), "ATTENTION")  # self-consistent export, canonical differs: export pending

    def test_version_disagreement_with_equal_body_is_not_in_sync(self):
        for revision in ("same", "new"):
            with self.subTest(revision):
                def bump(s):
                    a = s["artifacts"]["skill/factory-entry"]
                    a["version"] = "0.1.40"
                    if revision == "new":
                        a["revision"] = "another"
                item = self.snapshot(bump)[0]["skill/factory-entry"]
                self.assertEqual(item["level"], "ATTENTION")
                self.assertIn("versions disagree", item["reason"])

    def test_newer_notion_copy_of_a_released_reference_is_never_planned_down(self):
        def newer(s):
            s["artifacts"]["skill/factory-review"]["version"] = "9.9.9"
        item = self.snapshot(newer)[0]["skill/factory-review"]
        self.assertTrue(item.get("downgrade"))
        self.assertIn("refusing a downgrade", item["reason"])

    def test_reference_bytes_unreadable_artifacts_and_declaration_drift_are_reported(self):
        def mutate(s):
            s["artifacts"]["skill/factory-foundation"]["files"]["references/setup.md"] += " "
            del s["artifacts"]["skill/factory-evaluate"]
            s["artifacts"]["declaration/factory-lab"]["sha256"] = "0" * 64
            s["errors"].append("skill/factory-x: HTTP 401")
        main, _, items = self.snapshot(mutate)
        self.assertIn("references/setup.md: bytes differ", main["skill/factory-foundation"]["differences"])
        self.assertEqual(main["skill/factory-evaluate"]["level"], "ATTENTION")
        self.assertEqual(main["declaration/factory-lab"]["level"], "ATTENTION")
        self.assertTrue([i for i in items if "unreadable canonical source" in i["reason"]])

    def test_released_reference_drift_is_planned_only_with_a_valid_pin(self):
        def drift(s):
            s["artifacts"]["skill/factory-review"]["status"] = "Draft"
        main, _, _ = self.snapshot(drift)
        self.assertEqual(main["skill/factory-review"]["level"], "ATTENTION")
        self.assertIn("Status: 'Draft' -> 'Released reference'", main["skill/factory-review"]["drift"])

        def body(s):
            f = s["artifacts"]["skill/factory-review"]
            f["files"]["SKILL.md"] = f["files"]["SKILL.md"].replace("Use a context separate", "Use any context", 1)
            f["source"] = f"{reconcile.REPO_URL}/blob/{'0' * 40}/adlc/agentic-review/SKILL.md"
        with patch.object(reconcile, "release_context", return_value=("v-unreleased", None, False)):
            main, _, _ = self.snapshot(body)
        self.assertIn("awaits its release tag", main["skill/factory-review"]["reason"])

        def foreign(s):
            s["artifacts"]["skill/factory-review"]["source"] = "https://example.com/blob/" + "a" * 40 + "/x"
        with patch.object(reconcile, "release_context", return_value=("v-unreleased", None, False)):
            self.assertIn("invalid or foreign Source pin", self.snapshot(foreign)[0]["skill/factory-review"]["reason"])

    def test_only_an_exact_ancestor_pin_of_this_repository_and_skill_is_valid(self):
        item = reconcile.load_manifest(ROOT)[1]["skill/factory-review"]
        pin = git(ROOT, "log", "-1", "--format=%H", "--", item["path"])
        good = f"{reconcile.REPO_URL}/blob/{pin}/{item['path']}/SKILL.md"
        self.assertEqual(reconcile.released_pin(ROOT, item, good), good)
        bad = {"fork": good.replace("arcitai/agentic-systems", "attacker/fork"),
               "wrong skill": good.replace("agentic-review", "agentic-spec"),
               "non-URL": f"javascript:alert(1)//x/blob/{pin}/",
               "unknown commit": good.replace(pin, "0" * 40),
               "suffix": good + "?x"}
        for name, source in bad.items():
            with self.subTest(name):
                self.assertNotEqual(reconcile.released_pin(ROOT, item, source), source)

        def forged(s):
            s["artifacts"]["skill/factory-review"]["source"] = bad["fork"]
        self.assertNotEqual(self.snapshot(forged)[0]["skill/factory-review"]["level"], "IN-SYNC")

    def test_pending_handoffs_report_pending_applied_and_stale(self):
        fixture = SYNTHETIC_PENDING["id"]
        _, pending, _ = self.snapshot(synthetic_pending=True)
        self.assertIn("pending for", next(p for p in pending if p["pending"] == fixture)["reason"])

        def applied(s):
            s["artifacts"]["guide/home"]["text"] = SYNTHETIC_PENDING["after"]
        _, pending, _ = self.snapshot(applied, synthetic_pending=True)
        self.assertIn("is applied", next(p for p in pending if p["pending"] == fixture)["reason"])

        def stale(s):
            s["artifacts"]["guide/home"]["text"] = "Someone rewrote the status paragraph."
        _, pending, _ = self.snapshot(stale, synthetic_pending=True)
        self.assertIn("re-prepare", next(p for p in pending if p["pending"] == fixture)["reason"])


class DocsTests(unittest.TestCase):
    def test_docs_do_not_claim_coverage_the_publisher_does_not_check(self):
        text = (ROOT / "docs/system-definition.md").read_text(encoding="utf-8")
        self.assertNotIn("Success requires all of it", text)
        self.assertIn("covers only the released-reference pages", text)
        self.assertIn("does not read back", text)
        self.assertIn("not operational", text)


class WorkflowTests(unittest.TestCase):
    def test_ci_runs_the_visible_reconciliation(self):
        workflow = (ROOT / ".github/workflows/check.yml").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/reconcile.py --base", workflow)
        self.assertIn("fetch-depth: 0", workflow)
        # each main push has its own concurrency group and is never cancelled or replaced
        self.assertIn("group: method-checks-${{ github.event_name == 'pull_request' && github.ref || github.sha }}", workflow)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", workflow)

    def test_propagation_workflow_is_inactive_without_the_dedicated_connection(self):
        workflow = (ROOT / ".github/workflows/docs-publish.yml").read_text(encoding="utf-8")
        self.assertIn("vars.AGENTIC_SYSTEMS_DOCS_PUBLISH == 'enabled'", workflow)
        self.assertIn("environment: agentic-system-public-docs", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("statuses: write", workflow)
        publish_step = workflow.split("Propagate released references and read back", 1)[1].split("- uses:", 1)[0]
        self.assertIn("shell: bash", publish_step)  # pipefail, so tee cannot hide a failed or pending publish
        self.assertIn("refs/heads/main", workflow)
        self.assertIn("startsWith(github.ref, 'refs/tags/v')", workflow)
        self.assertIn("head_branch == 'main'", workflow)
        self.assertIn('git merge-base --is-ancestor "$AGENTIC_SYSTEMS_DOCS_SHA" origin/main', workflow)
        self.assertNotIn("AGENTIC_SYSTEMS_NOTION_TOKEN", workflow)
        self.assertNotIn("contents: write", workflow)


if __name__ == "__main__":
    unittest.main()
