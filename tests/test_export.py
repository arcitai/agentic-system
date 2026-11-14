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
spec = importlib.util.spec_from_file_location("export", ROOT / "scripts/export.py")
export = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export)
import reconcile  # noqa: E402

FIXTURES = ROOT / "tests/fixtures/notion-2026-11-05"


def fixture(name, kind):
    return (FIXTURES / f"{name}.{kind}.txt").read_text(encoding="utf-8")


def hints(text):
    out = {}
    for label, link in re.findall(r"\[([^\]]+)\]\((?![a-z]+:)([^)\s]+)\)", text):
        out.setdefault(link, set()).add(label)
    return out


class RealRenderingTests(unittest.TestCase):
    """The real 5 Nov 2026 Notion Skills API renderings export to the reviewed portable bytes."""

    def check(self, name, bundled, previous, version, updated, list_indent=True):
        expected = fixture(name, "portable")
        title = re.search(r"^# (.+)$", expected, re.M)[1]
        out, unresolved = export.portable_skill(fixture(name, "notion"), name, version, updated, title, bundled, hints(previous), list_indent)
        self.assertEqual(unresolved, [])
        self.assertEqual(out, expected)
        self.assertEqual(reconcile.normalize_skill(out), reconcile.normalize_skill(fixture(name, "notion")))

    def test_released_reference_with_line_breaks(self):
        text = fixture("factory-review", "portable")
        self.check("factory-review", {"SKILL.md"}, text, "0.1.18", "2026-10-17")

    def test_authoring_edition_with_filename_links_and_anchors(self):
        bundled = {"SKILL.md"} | {f"references/{n}.md" for n in ("adoption", "ci-delivery", "context", "engineering", "github", "method-migration", "setup", "workspace")}
        self.check("factory-foundation", bundled, fixture("factory-foundation", "portable"), "0.1.31", "2026-10-30")

    def test_newer_original_exports_its_change_with_previous_link_texts(self):
        bundled = {"SKILL.md", "references/policy.md", "references/t3.md"}
        self.check("factory-agent-ops", bundled, fixture("factory-agent-ops", "previous"), "0.1.32", "2026-11-03", list_indent=False)

    def test_newer_original_keeps_the_previous_indented_list_style(self):
        self.check("factory-entry", {"SKILL.md"}, fixture("factory-entry", "previous"), "0.1.32", "2026-11-03", list_indent=True)

    def test_unknown_link_text_is_reported_not_guessed(self):
        notion = fixture("factory-agent-ops", "notion")
        out, unresolved = export.portable_skill(notion, "factory-agent-ops", "0.1.32", "2026-11-03", "Factory Agent Ops",
                                                {"SKILL.md", "references/policy.md", "references/t3.md"}, {})
        self.assertTrue(unresolved)  # reported for editorial confirmation
        # lossless fallback: the prose stays and the target becomes a working bare link inside the parenthesis
        self.assertIn("the upkeep policy ([references/policy.md#persistent-choices](references/policy.md#persistent-choices))", out)
        self.assertEqual(reconcile.normalize_skill(out), reconcile.normalize_skill(notion))

    def test_authored_heading_replaces_the_legacy_export_title(self):
        notion = "---\nname: agentic-entry\ndescription: Explain the framework.\n---\n\n# Agentic System Entry\n\nUse the current framework.\n"
        out, unresolved = export.portable_skill(notion, "agentic-entry", "0.2.0", "2026-11-13",
                                                "Agentic Systems Entry", {"SKILL.md"})
        self.assertEqual(unresolved, [])
        self.assertEqual(re.findall(r"^# .+$", out, re.M), ["# Agentic System Entry"])
        self.assertEqual(reconcile.normalize_skill(out), reconcile.normalize_skill(notion))


class ExportCommandTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".agentic-system-task"))
        subprocess.run(["git", "init", "-q"], cwd=self.root, check=True)

    def tearDown(self):
        self.temporary.cleanup()

    def snapshot(self, key, files, version="0.1.40", revision="rev-new"):
        folder = Path(self.temporary.name) / "snap"
        folder.mkdir(exist_ok=True)
        (folder / "snapshot.json").write_text(json.dumps({"format": 1, "errors": [], "artifacts": {
            key: {"revision": revision, "version": version, "lastEdited": "2026-11-05T10:00:00.000Z", "readAt": "t", "files": files}}}))
        return folder

    def test_git_owned_released_reference_is_refused(self):
        snap = self.snapshot("skill/factory-security", {"SKILL.md": fixture("factory-review", "notion")})
        with self.assertRaises(ValueError):
            export.export(self.root, snap, "skill/factory-security")

    def test_retired_notion_skill_cannot_be_recreated_from_a_stale_snapshot(self):
        snap = self.snapshot("skill/factory-agent-ops", {"SKILL.md": fixture("factory-agent-ops", "notion")})
        with self.assertRaisesRegex(ValueError, "retired or renamed"):
            export.export(self.root, snap, "skill/factory-agent-ops")
        self.assertFalse((self.root / "agent-ops/agentic-agent-ops").exists())

    def test_export_writes_only_its_bundle_records_the_binding_and_removes_stale_files(self):
        stale = self.root / "evaluation/agentic-evaluate/references/old.md"
        stale.parent.mkdir()
        stale.write_text("x")
        notion = "---\nname: |-\n  agentic-evaluate\ndescription: |-\n  Compare.\nnotion_page_id: x\n---\n\nNotion authoring edition · 0.1.40\n\nBody line one<br />line two.\n"
        snap = self.snapshot("skill/factory-evaluate", {"SKILL.md": notion, "references/new.bin": {"base64": "AAEC"}})
        before = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file() and "evaluation/agentic-evaluate" not in p.as_posix() and p.name != "sources.json"}
        result = export.export(self.root, snap, "skill/factory-evaluate")
        self.assertEqual(result["removed"], ["references/old.md"])
        self.assertEqual((self.root / "evaluation/agentic-evaluate/references/new.bin").read_bytes(), b"\x00\x01\x02")
        skill = (self.root / "evaluation/agentic-evaluate/SKILL.md").read_text()
        self.assertIn('version: "0.1.40"', skill)
        self.assertIn('updated: "2026-11-05"', skill)
        self.assertIn("Body line one\nline two.", skill)
        self.assertNotIn("Notion authoring edition", skill)
        binding = {i["key"]: i for i in json.loads((self.root / "docs/sources.json").read_text())["artifacts"]}["skill/factory-evaluate"]["binding"]
        self.assertEqual((binding["revision"], binding["version"]), ("rev-new", "0.1.40"))
        after = {p: p.read_bytes() for p in before}
        self.assertEqual(before, after)

    def test_unsafe_snapshot_paths_are_refused_before_any_write(self):
        notion = "---\nname: |-\n  agentic-evaluate\ndescription: |-\n  Compare.\nnotion_page_id: x\n---\n\nText.\n"
        for bad in ("../escape.md", "/abs.md", "references/../../x.md", "a\\b.md"):
            with self.subTest(bad):
                before = (self.root / "docs/sources.json").read_bytes()
                with self.assertRaises(ValueError):
                    export.export(self.root, self.snapshot("skill/factory-evaluate", {"SKILL.md": notion, bad: "x"}), "skill/factory-evaluate")
                self.assertFalse((self.root.parent / "escape.md").exists())
                self.assertEqual((self.root / "docs/sources.json").read_bytes(), before)

    def test_first_export_needs_only_its_own_bundle(self):
        manifest = self.root / "docs/sources.json"
        data = json.loads(manifest.read_text())
        data["artifacts"].append({"key": "skill/factory-new", "kind": "skill", "owner": "notion", "label": "export",
                                  "path": "entry/agentic-system-new", "notion": "00000000-0000-0000-0000-000000000000", "public": True})
        manifest.write_text(json.dumps(data))
        notion = "---\nname: |-\n  agentic-system-new\ndescription: |-\n  New.\nnotion_page_id: x\n---\n\nNotion authoring edition · 0.1.40\n\nText.\n"
        result = export.export(self.root, self.snapshot("skill/factory-new", {"SKILL.md": notion}), "skill/factory-new", "Agentic Systems New")
        self.assertEqual(result["files"], ["SKILL.md"])
        self.assertEqual(reconcile.load_manifest(self.root)[2], [])
        self.assertIn("# Agentic Systems New", (self.root / "entry/agentic-system-new/SKILL.md").read_text())


if __name__ == "__main__":
    unittest.main()
