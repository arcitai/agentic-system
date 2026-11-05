import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("reconcile", ROOT / "scripts/reconcile.py")
reconcile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reconcile)


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()


def notion_rendering(text, version, preamble):
    """Render a Git skill the way the Notion Skills API returns it (observed 5 Nov 2026)."""
    lines = text.split("\n")
    end = lines.index("---", 1)
    meta = dict(line.split(": ", 1) for line in lines[1:end] if ": " in line and not line.startswith("  "))
    body = "\n".join(lines[end + 1:])
    body = re.sub(r"^# .*$", preamble, body, count=1, flags=re.M)
    body = re.sub(r"\[([^\]]+)\]\((?![a-z]+:)([^)\s]+)\)",
                  lambda m: f"`{m[1]}`" if m[1].endswith(".md") else f"{m[1]} (`{m[2]}`)", body)
    body = re.sub(r"(?<=[^\n])\n(?=[^\n-])", "<br />", body)
    return (f"---\nname: |-\n  {meta['name']}\ndescription: |-\n  {meta['description']}\nnotion_page_id: x\n---\n"
            + body)


class Repo:
    """A disposable Git copy of this checkout's tracked and new files."""

    def __init__(self, temporary):
        self.root = Path(temporary) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".factory-task", "dist"))
        git(self.root, "init", "-q")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "add", "-A")
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

    def impact(self, base, head="HEAD"):
        _, keys, errors = reconcile.load_manifest(self.root)
        return errors, reconcile.impact(self.root, keys, base, git(self.root, "rev-parse", head))


class ManifestTests(unittest.TestCase):
    def test_current_manifest_maps_every_skill_once(self):
        data, keys, errors = reconcile.load_manifest(ROOT)
        self.assertEqual(errors, [])
        skills = {p.parent.relative_to(ROOT).as_posix() for g in reconcile.GROUPS for p in (ROOT / g).glob("*/SKILL.md")}
        self.assertEqual(skills, {i["path"] for i in keys.values() if i["kind"] == "skill" and i.get("path")})

    def write_manifest(self, root, mutate):
        path = root / reconcile.MANIFEST
        data = json.loads(path.read_text())
        mutate(data["artifacts"])
        path.write_text(json.dumps(data))
        return reconcile.load_manifest(root)[2]

    def test_invalid_manifests_are_rejected(self):
        cases = {
            "duplicate key": lambda a: a.append(dict(a[-1])),
            "git cannot own an authoring edition": lambda a: a[-1].update(label="authoring-edition"),
            "private path": lambda a: a.append({"key": "doc/private", "kind": "doc", "owner": "git", "label": "main-working", "path": ".factory-task/x"}),
            "notion page id required": lambda a: a.append({"key": "guide/x", "kind": "page", "owner": "notion", "label": "authoring-edition"}),
            "skill without entry": lambda a: a.remove(next(i for i in a if i["key"] == "skill/factory-review")),
        }
        for name, mutate in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                shutil.copytree(ROOT, root / "r", ignore=shutil.ignore_patterns(".git", "__pycache__", ".factory-task"))
                self.assertTrue(self.write_manifest(root / "r", mutate), name)


class ImpactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.repo = Repo(self.temporary.name)
        self.repo.test = self
        self.base = git(self.repo.root, "rev-parse", "HEAD")

    def tearDown(self):
        self.temporary.cleanup()

    def levels(self, items):
        return {(i.get("key"), i["level"]) for i in items}

    def test_unchanged_source_is_a_visible_no_op(self):
        self.repo.commit("empty")
        errors, items = self.repo.impact(self.base)
        self.assertEqual((errors, items), ([], []))
        result = {"result": "NO-OP", "items": [], "head": "h", "base": "b", "canonical": "NOT RUN"}
        self.assertIn("NO-OP", reconcile.report(result))

    def test_git_owned_change_needs_propagation(self):
        self.repo.edit("docs/qualification.md", "#", "# ", )
        self.repo.commit("doc")
        self.assertEqual(self.levels(self.repo.impact(self.base)[1]), {("doc/qualification", "CHANGE")})

    def test_export_edit_without_new_binding_is_a_conflict_with_the_newer_original(self):
        self.repo.edit("agent-ops/factory-agent-ops/SKILL.md", "Start from the owner's", "Start from the agent's")
        self.repo.commit("export edit")
        self.assertEqual(self.levels(self.repo.impact(self.base)[1]), {("skill/factory-agent-ops", "CONFLICT")})

    def test_deliberate_export_with_new_binding_is_a_change(self):
        self.repo.edit("agent-ops/factory-agent-ops/SKILL.md", 'version: "0.1.29"', 'version: "0.1.32"')
        self.repo.edit("agent-ops/factory-agent-ops/SKILL.md", "Start from the owner's", "Start from the agent's")
        self.repo.commit("export 0.1.32")
        self.assertEqual(self.levels(self.repo.impact(self.base)[1]), {("skill/factory-agent-ops", "CHANGE")})

    def test_declaration_export_needs_its_canonical_hash(self):
        self.repo.edit("factory.yaml", "status: candidate", "status: adopted")
        self.repo.commit("decl")
        self.assertEqual(self.levels(self.repo.impact(self.base)[1]), {("declaration/factory-lab", "CONFLICT")})

    def test_released_reference_is_immutable_for_its_version(self):
        self.repo.edit("adlc/factory-review/SKILL.md", "Use a context separate", "Use a context apart")
        self.repo.commit("rr")
        self.assertEqual(self.levels(self.repo.impact(self.base)[1]), {("skill/factory-review", "CONFLICT")})

    def test_rename_without_manifest_update_fails_and_with_status_passes(self):
        git(self.repo.root, "mv", "adlc/factory-spec", "adlc/factory-brief-spec")
        self.repo.commit("rename")
        errors, _ = self.repo.impact(self.base)
        self.assertTrue(any("factory-spec" in e for e in errors))
        manifest = self.repo.root / reconcile.MANIFEST
        data = json.loads(manifest.read_text())
        old = next(i for i in data["artifacts"] if i["key"] == "skill/factory-spec")
        old.update(status="renamed", renamed_to="skill/factory-brief-spec")
        data["artifacts"].append({**old, "key": "skill/factory-brief-spec", "path": "adlc/factory-brief-spec", "status": "active"})
        data["artifacts"][-1].pop("renamed_to")
        manifest.write_text(json.dumps(data))
        self.repo.commit("manifest")
        errors, items = self.repo.impact(self.base)
        self.assertEqual(errors, [])
        self.assertIn(("skill/factory-spec", "CHANGE"), self.levels(items))

    def test_retirement_keeps_the_key(self):
        shutil.rmtree(self.repo.root / "adlc/factory-security")
        manifest = self.repo.root / reconcile.MANIFEST
        data = json.loads(manifest.read_text())
        next(i for i in data["artifacts"] if i["key"] == "skill/factory-security")["status"] = "retired"
        manifest.write_text(json.dumps(data))
        self.repo.commit("retire")
        errors, items = self.repo.impact(self.base)
        self.assertEqual(errors, [])
        self.assertIn(("skill/factory-security", "CHANGE"), self.levels(items))
        self.assertNotIn("CONFLICT", {i["level"] for i in items})

    def test_unowned_and_private_paths_are_reported(self):
        (self.repo.root / "notes.md").write_text("x")
        (self.repo.root / "docs/.claude").mkdir()
        (self.repo.root / "docs/.claude/leak.md").write_text("x")
        self.repo.commit("stray")
        items = self.repo.impact(self.base)[1]
        self.assertIn((None, "ATTENTION"), self.levels(items))
        self.assertIn("CONFLICT", {i["level"] for i in items if i["path"] == "docs/.claude/leak.md"})


class CanonicalTests(unittest.TestCase):
    def snapshot(self, temporary, mutate=lambda s: None):
        _, keys, _ = reconcile.load_manifest(ROOT)
        artifacts = {}
        for key, item in keys.items():
            if item["kind"] == "skill" and item.get("path"):
                folder = ROOT / item["path"]
                version = reconcile.git_skill_version(ROOT, item["path"])
                files = {p.relative_to(folder).as_posix(): p.read_text(encoding="utf-8") for p in folder.rglob("*") if p.is_file()}
                files["SKILL.md"] = notion_rendering(files["SKILL.md"], version, f"Notion authoring edition · {version}")
                artifacts[key] = {"revision": "r-" + key, "version": version, "readAt": "t", "files": files}
        decl = (ROOT / "factory.yaml").read_text()
        artifacts["declaration/factory-lab"] = {"revision": "t", "sha256": re.search(r"SHA-256 [^:]*: ([0-9a-f]{64})", decl)[1]}
        snap = {"format": 1, "artifacts": artifacts}
        mutate(snap)
        folder = Path(temporary) / "snap"
        folder.mkdir()
        (folder / "snapshot.json").write_text(json.dumps(snap))
        return {i["key"]: i for i in reconcile.compare(ROOT, keys, folder)}

    def test_notion_rendering_of_the_same_instructions_is_in_sync(self):
        with tempfile.TemporaryDirectory() as temporary:
            items = self.snapshot(temporary)
        self.assertEqual({k: v["level"] for k, v in items.items() if v["level"] != "IN-SYNC"},
                         {"skill/factory-brief": "ATTENTION"})

    def test_one_changed_sentence_is_detected(self):
        def change(s):
            f = s["artifacts"]["skill/factory-review"]["files"]
            f["SKILL.md"] = f["SKILL.md"].replace("A different model name alone", "Any model name", 1)
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(self.snapshot(temporary, change)["skill/factory-review"]["level"], "ATTENTION")

    def test_newer_canonical_is_pending_export_and_older_canonical_is_a_conflict(self):
        def newer(s):
            a = s["artifacts"]["skill/factory-agent-ops"]
            a["version"] = "9.9.9"
            a["files"]["SKILL.md"] += "\nNew canonical rule.\n"

        def older(s):
            a = s["artifacts"]["skill/factory-agent-ops"]
            a["version"] = "0.0.1"
            a["files"]["SKILL.md"] += "\nOld text.\n"
        with tempfile.TemporaryDirectory() as temporary:
            item = self.snapshot(temporary, newer)["skill/factory-agent-ops"]
            self.assertEqual(item["level"], "ATTENTION")
            self.assertIn("never overwrite Notion from Git", item["reason"])
        with tempfile.TemporaryDirectory() as temporary:
            self.assertEqual(self.snapshot(temporary, older)["skill/factory-agent-ops"]["level"], "CONFLICT")

    def test_reference_bytes_and_unreadable_artifacts_are_reported(self):
        def mutate(s):
            s["artifacts"]["skill/factory-foundation"]["files"]["references/setup.md"] += " "
            del s["artifacts"]["skill/factory-evaluate"]
            s["artifacts"]["declaration/factory-lab"]["sha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            items = self.snapshot(temporary, mutate)
        self.assertIn("references/setup.md: bytes differ", items["skill/factory-foundation"]["differences"])
        self.assertEqual(items["skill/factory-evaluate"]["level"], "ATTENTION")
        self.assertEqual(items["declaration/factory-lab"]["level"], "ATTENTION")


class WorkflowTests(unittest.TestCase):
    def test_ci_runs_the_visible_reconciliation(self):
        # The documentation promises this step; fail until the workflow really runs it on PRs and main.
        workflow = (ROOT / ".github/workflows/check.yml").read_text(encoding="utf-8")
        self.assertIn("python3 scripts/reconcile.py --base", workflow)
        self.assertIn("fetch-depth: 0", workflow)

    def test_publisher_workflow_is_inactive_without_the_dedicated_connection(self):
        workflow = (ROOT / ".github/workflows/docs-publish.yml").read_text(encoding="utf-8")
        self.assertIn("vars.FACTORY_DOCS_PUBLISH == 'enabled'", workflow)
        self.assertIn("environment: factory-public-docs", workflow)
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertNotIn("FACTORY_NOTION_TOKEN", workflow)


class ProjectionTests(unittest.TestCase):
    def test_projections_are_git_owned_facts_only(self):
        rows = reconcile.projections(ROOT)
        keys = [r["key"] for r in rows]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertFalse([k for k in keys if k.startswith(("guide/", "declaration/"))])
        self.assertIn(rows[0]["label"], ("released", "main-working"))
        self.assertTrue(all(len(r["hash"]) == 64 for r in rows))


if __name__ == "__main__":
    unittest.main()
