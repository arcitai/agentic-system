import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("notion_snapshot", ROOT / "scripts/notion_snapshot.py")
snapshot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(snapshot)


def archive(members):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for name, data, kind in members:
            info = tarfile.TarInfo(name)
            if kind == "file":
                info.size = len(data)
                tar.addfile(info, io.BytesIO(data))
            else:
                info.type, info.linkname = tarfile.SYMTYPE, "../../etc/passwd"
                tar.addfile(info)
    return buffer.getvalue()


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


class FakeNotion:
    """Paginated block children and a Skills API download, as the Notion API returns them."""

    def __init__(self, pages):
        self.pages, self.calls = pages, []

    def __call__(self, request, timeout=None):
        url = request.full_url
        self.calls.append(url)
        if url.startswith("https://download/"):
            return Response(self.pages[url])
        path = url.split("/v1", 1)[1]
        return Response(json.dumps(self.pages[path]).encode())


class ArchiveTests(unittest.TestCase):
    def test_complete_archive_with_binary_file(self):
        files = snapshot.skill_files(archive([("factory-x/SKILL.md", b"---\n", "file"), ("factory-x/references/a.png", b"\x89PNG\xff", "file")]), "factory-x")
        self.assertEqual(files["SKILL.md"], "---\n")
        self.assertEqual(files["references/a.png"], {"base64": "iVBOR/8="})

    def test_unsafe_or_incomplete_archives_are_refused(self):
        cases = {
            "duplicate": [("factory-x/SKILL.md", b"a", "file"), ("factory-x/SKILL.md", b"b", "file")],
            "traversal": [("factory-x/SKILL.md", b"a", "file"), ("factory-x/../evil", b"b", "file")],
            "absolute": [("/factory-x/SKILL.md", b"a", "file")],
            "other folder": [("factory-y/SKILL.md", b"a", "file")],
            "symlink": [("factory-x/SKILL.md", b"a", "file"), ("factory-x/link", b"", "link")],
            "no SKILL.md": [("factory-x/references/a.md", b"a", "file")],
        }
        for name, members in cases.items():
            with self.subTest(name), self.assertRaises(ValueError):
                snapshot.skill_files(archive(members), "factory-x")


class PaginationTests(unittest.TestCase):
    def test_renamed_skill_uses_its_path_with_the_same_stable_key(self):
        fake = FakeNotion({
            "/pages/p": {"properties": {}, "last_edited_time": "t"},
            "/ai/skills/p": {"version_id": "v", "url": "https://download/x"},
            "https://download/x": archive([("agentic-x/SKILL.md", b"name: agentic-x", "file")]),
        })
        keys = {"skill/factory-x": {"key": "skill/factory-x", "kind": "skill", "owner": "notion", "notion": "p", "path": "evaluation/agentic-x"}}
        result = snapshot.freeze(keys, snapshot.Reader("token", fake))
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["artifacts"]["skill/factory-x"]["files"]["SKILL.md"], "name: agentic-x")

    def test_declaration_code_block_on_a_later_page_is_found(self):
        block = {"type": "code", "id": "b", "last_edited_time": "t", "code": {"language": "yaml", "rich_text": [{"plain_text": 'definition_version: "0.9"\n'}]}}
        filler = [{"type": "paragraph", "id": str(i), "paragraph": {"rich_text": []}} for i in range(100)]
        fake = FakeNotion({
            "/blocks/decl/children?page_size=100": {"results": filler, "has_more": True, "next_cursor": "c2"},
            "/blocks/decl/children?page_size=100&start_cursor=c2": {"results": [block], "has_more": False},
        })
        keys = {"declaration/x": {"key": "declaration/x", "kind": "declaration", "owner": "notion", "notion": "decl"}}
        result = snapshot.freeze(keys, snapshot.Reader("token", fake))
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["artifacts"]["declaration/x"]["version"], "0.9")
        self.assertEqual(len([c for c in fake.calls if "children" in c]), 2)

    def test_unreadable_skill_is_an_error_not_a_partial_snapshot(self):
        fake = FakeNotion({
            "/pages/p": {"properties": {}, "last_edited_time": "t"},
            "/ai/skills/p": {"version_id": "v", "url": "https://download/x"},
            "https://download/x": archive([("factory-x/SKILL.md", b"a", "file"), ("factory-x/SKILL.md", b"b", "file")]),
        })
        keys = {"skill/factory-x": {"key": "skill/factory-x", "kind": "skill", "owner": "notion", "notion": "p"}}
        result = snapshot.freeze(keys, snapshot.Reader("token", fake))
        self.assertEqual(result["artifacts"], {})
        self.assertIn("duplicate", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
