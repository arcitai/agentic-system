import importlib.util
import io
import json
from pathlib import Path
import sys
import tarfile
import unittest
from unittest.mock import patch
import urllib.error

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
    def test_sparse_members_are_refused_before_their_logical_size_is_expanded(self):
        raw = io.BytesIO()
        with tarfile.open(fileobj=raw, mode='w', format=tarfile.GNU_FORMAT) as tar:
            info = tarfile.TarInfo('factory-x/SKILL.md'); info.size = 1
            tar.addfile(info, io.BytesIO(b'a'))
            sparse = tarfile.TarInfo('factory-x/sparse'); sparse.type = tarfile.GNUTYPE_SPARSE
            tar.addfile(sparse)
        import gzip
        with self.assertRaises(snapshot.ArchiveError):
            snapshot.skill_files(gzip.compress(raw.getvalue()), 'factory-x')

    def test_credential_copy_whitespace_is_safe_and_invalid_headers_never_echo_it(self):
        self.assertEqual(snapshot.Reader('  fixture-token\n').token, 'fixture-token')
        with self.assertRaises(ValueError) as raised:
            snapshot.Reader('PRIVATE-VALUE\nInjected: bad')
        self.assertNotIn('PRIVATE-VALUE', str(raised.exception))

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

    def test_a_folder_retained_from_an_earlier_import_is_reported_not_merged_or_dropped(self):
        members = [("agentic-x/SKILL.md", b"new", "file"), ("factory-x/SKILL.md", b"old", "file"), ("factory-x/references/kept.md", b"k", "file")]
        with self.assertRaises(snapshot.ArchiveError) as raised:
            snapshot.skill_files(archive(members), "agentic-x")
        self.assertIn("factory-x/SKILL.md", str(raised.exception))
        self.assertIn("neither merged nor dropped", str(raised.exception))

    def test_an_archive_that_unpacks_beyond_the_limit_is_refused_before_parsing(self):
        bomb = archive([("factory-x/SKILL.md", b"a", "file"), ("factory-x/references/big.bin", bytes(200_000), "file")])
        self.assertLess(len(bomb), 2_000)  # compresses far below what it expands to
        with patch.object(snapshot, "ARCHIVE_LIMIT", 100_000), self.assertRaises(snapshot.ArchiveError):
            snapshot.skill_files(bomb, "factory-x")

    def test_a_cut_off_archive_is_a_read_failure_not_a_partial_skill(self):
        whole = archive([("factory-x/SKILL.md", b"a" * 5000, "file")])
        with self.assertRaises(tarfile.TarError):
            snapshot.skill_files(whole[:len(whole) // 2], "factory-x")


class DownloadTests(unittest.TestCase):
    SIGNED = "https://download/x?X-Amz-Signature=SIGNED-SECRET"

    def test_only_the_api_request_carries_the_connection(self):
        seen = []

        def opener(request, timeout=None):
            seen.append((request.full_url, request.get_header("Authorization")))
            return Response(b"archive" if request.full_url == self.SIGNED else b"{}")
        reader = snapshot.Reader("token", opener)
        reader.get("/ai/skills/p")
        self.assertEqual(reader.download(self.SIGNED), b"archive")
        self.assertEqual(seen, [("https://api.notion.com/v1/ai/skills/p", "Bearer token"), (self.SIGNED, None)])

    def test_a_signed_archive_url_is_never_repeated_in_an_error(self):
        def refused(request, timeout=None):
            raise urllib.error.HTTPError(request.full_url, 403, "Forbidden", {}, io.BytesIO())

        def reset(request, timeout=None):
            raise ConnectionResetError(f"reset while fetching {request.full_url}")
        skill = {"skill/factory-x": {"key": "skill/factory-x", "kind": "skill", "owner": "notion", "notion": "p"}}
        for name, url, opener in (("not https", "signed.example/x?X-Amz-Signature=SIGNED-SECRET", None),
                                  ("plain http", self.SIGNED.replace("https:", "http:"), None),
                                  ("expired", self.SIGNED, refused), ("reset", self.SIGNED, reset)):
            with self.subTest(name):
                pages = {"/pages/p": {"properties": {}}, "/ai/skills/p": {"version_id": "v", "url": url}}

                def notion(request, timeout=None, opener=opener, pages=pages):
                    if request.full_url.startswith(snapshot.API):
                        return Response(json.dumps(pages[request.full_url.split("/v1", 1)[1]]).encode())
                    return (opener or reset)(request, timeout)
                result = snapshot.freeze(skill, snapshot.Reader("token", notion))
                self.assertEqual(result["artifacts"], {})
                self.assertEqual(len(result["errors"]), 1)
                self.assertNotIn("SIGNED-SECRET", json.dumps(result))
                self.assertNotIn("signed.example", json.dumps(result))

    def test_an_oversized_download_is_refused(self):
        reader = snapshot.Reader("token", lambda request, timeout=None: Response(bytes(5_000)))
        with patch.object(snapshot, "ARCHIVE_LIMIT", 1_000), self.assertRaises(snapshot.ArchiveError):
            reader.download(self.SIGNED)


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
