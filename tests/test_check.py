import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("check", ROOT / "scripts/check.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CheckTests(unittest.TestCase):
    def test_metadata_and_reference_failures_are_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / "evaluation/example"
            skill.mkdir(parents=True)
            path = skill / "SKILL.md"
            (root / "VERSION").write_text("0.1.4\n")
            valid = ('---\nname: example\ndescription: A test skill.\nlicense: MIT\n'
                     'metadata:\n  version: "0.1.4"\n  updated: "2026-10-09"\n---\n')
            (skill / "reference.md").write_text("# Reference\n\nRevision: 0.1.4 · Updated: 2026-10-09\n")
            path.write_text(valid + "[Local](reference.md)\n")
            self.assertEqual(module.check(root), ([], 1))
            path.write_text(valid.replace("name: example", "name: wrong"))
            self.assertTrue(any("invalid/duplicate name" in e for e in module.check(root)[0]))
            path.write_text(valid + "[Missing](absent.md)\n")
            self.assertTrue(any("broken link" in e for e in module.check(root)[0]))
            (root / "outside.md").write_text("Must not become a hidden dependency.\n")
            path.write_text(valid + "[Escapes](../../outside.md)\n")
            self.assertTrue(any("escapes" in e for e in module.check(root)[0]))
            path.write_text(valid + "[Encoded escape](%2E%2E/%2E%2E/outside.md)\n")
            self.assertTrue(any("escapes" in e for e in module.check(root)[0]))


    def test_revision_metadata_rejects_malformed_or_future_release_values(self):
        valid = ('---\nname: example\ndescription: A test skill.\nlicense: MIT\n'
                 'metadata:\n  version: "0.1.4"\n  updated: "2026-10-09"\n---\n')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "VERSION").write_text("0.1.4\n")
            folder = root / "evaluation/example"
            folder.mkdir(parents=True)
            path = folder / "SKILL.md"
            for source in (valid, valid.replace('"0.1.4"', '"0.1.3"'),
                           valid.replace('A test skill.', 'A skill --- with punctuation.')):
                path.write_text(source)
                self.assertEqual(module.check(root), ([], 1))
            invalid = [
                valid.replace('metadata:\n  version: "0.1.4"\n  updated: "2026-10-09"\n', ''),
                valid.replace('"0.1.4"', '"0.1.5"'),
                valid.replace('"0.1.4"', '"01.1.4"'),
                valid.replace('"2026-10-09"', '"2026-02-30"'),
                valid.replace('"2026-10-09"', '2026-10-09'),
                valid.replace('"2026-10-09"', '"2026-1-9"'),
                valid.replace('  version:', '  version: "0.1.3"\n  version:'),
                valid.replace('  updated:', '  arbitrary:'),
                valid.replace('"2026-10-09"', '"2026-10-09\t"'),
                valid.replace('\n---\n', '\n---not-a-delimiter\n'),
            ]
            for source in invalid:
                with self.subTest(source=source):
                    path.write_text(source)
                    self.assertTrue(module.check(root)[0])

    def test_documents_need_top_revision_but_templates_do_not(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "VERSION").write_text("0.1.4\n")
            doc = root / "README.md"
            template = root / ".github/pull_request_template.md"
            template.parent.mkdir()
            template.write_text("## Describe this change\n")
            for text, expected in [
                ("# Guide\n\nRevision: 0.1.3 · Updated: 2026-10-08\n", False),
                ("# Guide\nNo edit record.\n", True),
                ("# Guide\n\nRevision: 0.1.5 · Updated: 2026-10-09\n", True),
                ("# Guide\n\nRevision: 0.1.4 · Updated: 2026-13-09\n", True),
                ("# Guide\n" + "\n" * 6 + "Revision: 0.1.4 · Updated: 2026-10-09\n", True),
            ]:
                with self.subTest(text=text):
                    doc.write_text(text)
                    errors = module.check(root)[0]
                    self.assertEqual(any("README.md" in e for e in errors), expected)
                    self.assertFalse(any("pull_request_template" in e for e in errors))

    def test_harness_context_is_skipped_but_maintained_dot_sources_are_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "VERSION").write_text("0.1.4\n")
            # Sandboxes mask harness paths with unreadable non-files; a directory reproduces that.
            (root / ".claude/loop.md").mkdir(parents=True)
            (root / ".claude/notes.md").write_text("Private notes without a revision.\n")
            template = root / ".github/pull_request_template.md"
            template.parent.mkdir()
            template.write_text("[Missing](absent.md)\n")
            listed = []
            scandir = os.scandir

            def recording_scandir(path="."):
                listed.append(Path(os.fsdecode(path)))
                return scandir(path)

            with mock.patch.object(os, "scandir", recording_scandir):
                errors = module.check(root)[0]
            self.assertTrue(listed)
            self.assertFalse([p for p in listed if ".claude" in p.parts])
            self.assertFalse(any(".claude" in e for e in errors))
            self.assertTrue(any("pull_request_template.md: broken link" in e for e in errors))

    def test_private_task_records_are_skipped_but_ordinary_documents_are_checked(self):
        invalid = "# Note\n\nNo revision header.\n\n[Missing](absent.md)\n"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "VERSION").write_text("0.1.4\n")
            private = root / ".agentic-system-task/qualification/result.md"
            private.parent.mkdir(parents=True)
            private.write_text(invalid)
            self.assertFalse(any(".agentic-system-task" in e for e in module.check(root)[0]))
            ordinary = root / "docs/result.md"
            ordinary.parent.mkdir()
            ordinary.write_text(invalid)
            errors = module.check(root)[0]
            self.assertTrue(any("docs/result.md" in e for e in errors))
            self.assertTrue(any("docs/result.md: broken link" in e for e in errors))
            self.assertFalse(any(".agentic-system-task" in e for e in errors))

    def test_links_in_code_spans_fences_and_titles_are_not_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "VERSION").write_text("0.1.4\n")
            (root / "target.md").write_text("# Target\n")
            doc = root / "guide.md"
            doc.write_text(
                "# Guide\n\nRevision: 0.1.4 · Updated: 2026-10-09\n\n"
                "`[a](missing.md)`\n"
                "``[a](x.md) with ` tick``\n"
                "~~~\n[a](missing.md)\n~~~\n"
                '[c](target.md "Title")\n'
                "[c](target.md 'Title')\n"
                "[c](target.md (Title))\n"
            )
            errors = module.check(root)[0]
            self.assertFalse(any("broken link" in e for e in errors))

    def test_real_broken_links_still_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "VERSION").write_text("0.1.4\n")
            (root / "kept.md").write_text("# Kept\n")
            doc = root / "guide.md"
            doc.write_text(
                "# Guide\n\nRevision: 0.1.4 · Updated: 2026-10-09\n\n"
                "[Missing plain](absent-plain.md)\n"
                '[Missing title](absent-title.md "Title")\n'
                "`[code](kept.md)` [Broken on code line](absent-codeline.md)\n"
                "`~~~` inside a code span, then [Broken after code span](absent-after.md)\n"
                "`[Ignored span](ignored-span.md)`\n"
                "~~~\n[Ignored fence](ignored-fence.md)\n~~~\n"
                "[Broken after fence](absent-after-fence.md)\n"
                "~~~\n[Second ignored fence](ignored-second-fence.md)\n~~~\n"
            )
            errors = module.check(root)[0]
            broken = sorted(
                e for e in errors if "broken link" in e
            )
            expected = sorted(
                f"{doc.relative_to(root)}: broken link {raw}"
                for raw in [
                    "absent-plain.md",
                    'absent-title.md "Title"',
                    "absent-codeline.md",
                    "absent-after.md",
                    "absent-after-fence.md",
                ]
            )
            self.assertEqual(broken, expected)

    def test_package_version_is_required_and_numeric(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for value in (None, "next", "01.2.3"):
                if value is not None:
                    (root / "VERSION").write_text(value)
                self.assertTrue(any("VERSION:" in e for e in module.check(root)[0]))


if __name__ == "__main__":
    unittest.main()
