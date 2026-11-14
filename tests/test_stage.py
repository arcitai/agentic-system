import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("stage", ROOT / "scripts/stage.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StageTests(unittest.TestCase):
    def source_fixture(self, root):
        source = root / "source"
        shutil.copytree(ROOT / "entry", source / "entry")
        shutil.copy2(ROOT / "LICENSE", source / "LICENSE")
        shutil.copy2(ROOT / "VERSION", source / "VERSION")
        return source

    def full_source_fixture(self, root):
        source = self.source_fixture(root)
        for group in module.BUNDLES:
            if not (source / group).exists():
                shutil.copytree(ROOT / group, source / group)
        return source

    def test_all_set_has_every_canonical_skill_once_and_stays_portable(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "all"
            manifest = module.stage(module.ALL, target)
            self.assertEqual(manifest["bundle"], module.ALL)
            self.assertEqual(json.loads((target / "manifest.json").read_text()), manifest)
            sources = [p.parent for group in module.BUNDLES
                       for p in (ROOT / group).glob("*/SKILL.md")]
            self.assertIn("agentic-entry", {p.name for p in sources})
            staged = sorted(p.name for p in (target / "skills").iterdir())
            self.assertEqual(staged, sorted(p.name for p in sources))
            actual = {p.relative_to(target).as_posix() for p in target.rglob("*")
                      if p.is_file() and p.name != "manifest.json"}
            self.assertEqual(actual, set(manifest["files"]))
            for name, digest in manifest["files"].items():
                self.assertEqual(hashlib.sha256((target / name).read_bytes()).hexdigest(), digest)
            for skill in sources:
                folder = target / "skills" / skill.name
                self.assertTrue((folder / "SKILL.md").is_file())
                # Each staged resource is the single canonical source, byte for byte.
                for name in manifest["files"]:
                    parts = Path(name).parts
                    if parts[1] == skill.name and parts[-1] != "LICENSE":
                        self.assertEqual((target / name).read_bytes(),
                                         (skill / Path(*parts[2:])).read_bytes())
                # Every local link in a staged skill must resolve inside that skill.
                for document in folder.rglob("*.md"):
                    text = re.sub(r"```.*?```", "", document.read_text(encoding="utf-8"), flags=re.S)
                    for raw in re.findall(r"\]\(([^)#]+)", text):
                        if "://" in raw or raw.startswith("mailto:"):
                            continue
                        resolved = (document.parent / raw).resolve()
                        self.assertTrue(resolved.is_file(), f"{document}: {raw}")
                        self.assertTrue(resolved.is_relative_to(folder.resolve()),
                                        f"{document}: {raw}")

    def test_all_set_refuses_a_missing_group(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.source_fixture(root)
            with self.assertRaises(ValueError):
                module.stage(module.ALL, root / "output", source)
            self.assertFalse((root / "output").exists())

    def test_all_set_refuses_duplicate_skill_names(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.full_source_fixture(root)
            shutil.copytree(source / "entry/agentic-entry",
                            source / "defence/agentic-entry")
            with self.assertRaises(ValueError):
                module.stage(module.ALL, root / "output", source)
            self.assertFalse((root / "output").exists())

    def test_all_set_refuses_symlinked_resource_in_any_group(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.full_source_fixture(root)
            secret = root / "private"
            secret.write_text("never stage")
            (source / "defence/agentic-security/leak").symlink_to(secret)
            with self.assertRaises(ValueError):
                module.stage(module.ALL, root / "output", source)
            self.assertFalse((root / "output").exists())

    @unittest.skipUnless(shutil.which("git"), "Git provenance needs Git")
    def test_all_set_stages_only_tracked_files_with_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.full_source_fixture(root)
            subprocess.run(["git", "init", "-q", str(source)], check=True)
            subprocess.run(["git", "add", "."], cwd=source, check=True)
            subprocess.run(["git", "-c", "user.name=Fixture", "-c",
                            "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                            "commit", "-qm", "Fixture"], cwd=source, check=True)
            (source / "foundation/agentic-foundation/untracked.txt").write_text("not reviewed")
            manifest = module.stage(module.ALL, root / "output", source)
            self.assertIsNotNone(manifest["sourceRevision"])
            self.assertTrue(manifest["sourceModified"])
            self.assertFalse(any(name.endswith("untracked.txt") for name in manifest["files"]))

    @unittest.skipUnless(shutil.which("git"), "Git provenance needs Git")
    def test_archive_inside_unrelated_repo_has_no_git_provenance(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "unrelated.txt").write_text("Unrelated repository\n")
            subprocess.run(["git", "add", "unrelated.txt"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Fixture", "-c",
                            "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                            "commit", "-qm", "Unrelated"], cwd=root, check=True)
            source = self.source_fixture(root)
            manifest = module.stage("entry", root / "output", source)
            self.assertIsNone(manifest["sourceRevision"])
            self.assertIsNone(manifest["sourceModified"])

    @unittest.skipUnless(shutil.which("git"), "Git provenance needs Git")
    def test_checkout_stages_only_tracked_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = self.source_fixture(root)
            (source / ".gitignore").write_text(".env\n")
            subprocess.run(["git", "init", "-q", str(source)], check=True)
            subprocess.run(["git", "add", "."], cwd=source, check=True)
            subprocess.run(["git", "-c", "user.name=Fixture", "-c",
                            "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false",
                            "commit", "-qm", "Fixture"], cwd=source, check=True)
            secret = source / "entry/agentic-entry/.env"
            secret.write_text("PRIVATE=must-not-stage\n")
            manifest = module.stage("entry", root / "output", source)
            self.assertIsNotNone(manifest["sourceRevision"])
            self.assertFalse(manifest["sourceModified"])
            self.assertFalse(any(name.endswith(".env") for name in manifest["files"]))
            self.assertFalse((root / "output/skills/agentic-entry/.env").exists())
            (secret.parent / "untracked.txt").write_text("not reviewed")
            second = module.stage("entry", root / "second", source)
            self.assertTrue(second["sourceModified"])
            self.assertFalse(any(name.endswith("untracked.txt") for name in second["files"]))

    def test_each_bundle_is_portable_and_manifest_matches_bytes(self):
        with tempfile.TemporaryDirectory() as temporary:
            for bundle in module.BUNDLES:
                target = Path(temporary) / bundle
                manifest = module.stage(bundle, target)
                self.assertEqual(json.loads((target / "manifest.json").read_text()), manifest)
                expected = {p.parent.name for p in (ROOT / bundle).glob("*/SKILL.md")}
                self.assertEqual({p.name for p in (target / "skills").iterdir()}, expected)
                actual = {p.relative_to(target).as_posix() for p in target.rglob("*")
                          if p.is_file() and p.name != "manifest.json"}
                self.assertEqual(actual, set(manifest["files"]))
                for name, digest in manifest["files"].items():
                    self.assertEqual(hashlib.sha256((target / name).read_bytes()).hexdigest(), digest)
                for name in expected:
                    self.assertEqual((target / "skills" / name / "LICENSE").read_bytes(),
                                     (ROOT / "LICENSE").read_bytes())

    def test_existing_destination_is_untouched(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "existing"
            target.mkdir()
            marker = target / "local-change"
            marker.write_text("keep")
            with self.assertRaises(FileExistsError):
                module.stage("defence", target)
            self.assertEqual(list(target.iterdir()), [marker])
            self.assertEqual(marker.read_text(), "keep")

    def test_symlink_resource_cannot_disclose_outside_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "source"
            shutil.copytree(ROOT / "entry", source / "entry")
            shutil.copy2(ROOT / "LICENSE", source / "LICENSE")
            shutil.copy2(ROOT / "VERSION", source / "VERSION")
            secret = root / "private"
            secret.write_text("never stage")
            (source / "entry/agentic-entry/leak").symlink_to(secret)
            with self.assertRaises(ValueError):
                module.stage("entry", root / "output", source)
            self.assertFalse((root / "output").exists())

    def test_dangling_destination_symlink_is_refused(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "link"
            target.symlink_to(Path(temporary) / "absent")
            with self.assertRaises(FileExistsError):
                module.stage("foundation", target)
            self.assertTrue(target.is_symlink())


if __name__ == "__main__":
    unittest.main()
