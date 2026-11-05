#!/usr/bin/env python3
"""Freeze the canonical Notion originals named in docs/sources.json into a neutral snapshot
for scripts/reconcile.py --canonical and scripts/export.py (#122). Read-only: page, block and
data-source GETs and the Notion Skills API download; nothing is written to Notion. The
connection comes from the environment variable named by --token-env and is never printed or
stored. Every list is paginated; a skill archive must hold exactly one top-level folder named
after the skill, with unique, relative, regular files; anything else makes that artifact
unreadable rather than silently incomplete.
"""

import argparse
import base64
import datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import sys
import tarfile
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reconcile  # noqa: E402

API = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"


class AccessError(Exception):
    pass


class Reader:
    def __init__(self, token, opener=urllib.request.urlopen):
        self.token, self.opener = token, opener

    def get(self, path):
        request = urllib.request.Request(API + path, headers={"Authorization": "Bearer " + self.token, "Notion-Version": NOTION_VERSION})
        try:
            with self.opener(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in (401, 403, 404):
                raise AccessError(f"{path.split('?')[0]}: HTTP {error.code} (missing, expired or unshared access)") from None
            raise

    def download(self, url):
        with self.opener(urllib.request.Request(url), timeout=60) as response:
            return response.read()

    def children(self, block_id):
        out, cursor = [], None
        while True:
            page = self.get(f"/blocks/{block_id}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else ""))
            out += page["results"]
            if not page.get("has_more"):
                return out
            cursor = page["next_cursor"]


def plain(rich):
    return "".join(t.get("plain_text", "") for t in rich or [])


def prop_text(prop):
    """Text of a title/rich_text/select/status/url property; None if absent."""
    if not prop:
        return None
    value = prop.get(prop.get("type"))
    if isinstance(value, list):
        return plain(value)
    if isinstance(value, dict):
        return value.get("name")
    return value


def page_text(reader, block_id, depth=0, limit=3):
    """Readable text of a page's blocks, in order; child pages/databases are referenced, not followed."""
    lines = []
    for block in reader.children(block_id):
        kind = block["type"]
        body = block.get(kind, {})
        if kind in ("child_page", "child_database"):
            lines.append(f"[{kind}: {body.get('title', '')}]")
            continue
        if "rich_text" in body:
            lines.append(plain(body["rich_text"]))
        if block.get("has_children") and depth < limit:
            lines += page_text(reader, block["id"], depth + 1, limit)
    return lines


def skill_files(archive, name):
    files = {}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.isdir():
                continue
            path = PurePosixPath(member.name)
            if not member.isfile() or path.is_absolute() or ".." in path.parts or len(path.parts) < 2 or path.parts[0] != name:
                raise ValueError(f"unsafe or unexpected archive member {member.name!r}")
            rel = PurePosixPath(*path.parts[1:]).as_posix()
            if rel in files:
                raise ValueError(f"duplicate archive member {member.name!r}")
            data = tar.extractfile(member).read()
            try:
                files[rel] = data.decode("utf-8")
            except UnicodeDecodeError:
                files[rel] = {"base64": base64.b64encode(data).decode("ascii")}
    if "SKILL.md" not in files:
        raise ValueError("archive has no SKILL.md")
    return files


def freeze(keys, reader, read_at=None):
    read_at = read_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    artifacts, errors = {}, []
    for key, item in sorted(keys.items()):
        if item.get("status", "active") != "active" or item["owner"] != "notion" and item["kind"] != "skill":
            continue
        try:
            if item["kind"] == "skill":
                page = reader.get(f"/pages/{item['notion']}")
                props = page["properties"]
                skill = reader.get(f"/ai/skills/{item['notion']}")
                archive = reader.download(skill["url"])
                name = item["key"].split("/", 1)[1]
                artifacts[key] = {"revision": skill.get("version_id"), "version": prop_text(props.get("Version")) or "",
                                  "status": prop_text(props.get("Status")), "source": prop_text(props.get("Source")),
                                  "readAt": read_at, "lastEdited": page.get("last_edited_time"),
                                  "archiveSha256": hashlib.sha256(archive).hexdigest(), "files": skill_files(archive, name)}
            elif item["kind"] == "declaration":
                code = [b for b in reader.children(item["notion"]) if b["type"] == "code" and b["code"].get("language") == "yaml"]
                if len(code) != 1:
                    raise ValueError(f"expected exactly one YAML code block, found {len(code)}")
                text = plain(code[0]["code"]["rich_text"]).replace("\r\n", "\n").rstrip("\n") + "\n"
                artifacts[key] = {"revision": code[0].get("last_edited_time"), "readAt": read_at,
                                  "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                                  "version": next((l.split('"')[1] for l in text.splitlines() if l.startswith("definition_version")), "")}
            elif item["kind"] == "page":
                page = reader.get(f"/pages/{item['notion']}")
                artifacts[key] = {"revision": page.get("last_edited_time"), "readAt": read_at, "public_url": page.get("public_url"),
                                  "text": "\n".join(page_text(reader, item["notion"]))}
        except (AccessError, ValueError, KeyError, IndexError, tarfile.TarError, urllib.error.URLError) as error:
            errors.append(f"{key}: {error}")
    return {"format": 1, "readAt": read_at, "artifacts": artifacts, "errors": errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New snapshot directory")
    parser.add_argument("--token-env", default="FACTORY_PUBLIC_DOCS_TOKEN")
    args = parser.parse_args(argv)
    token = os.environ.get(args.token_env, "")
    if not token:
        print(f"MISSING ACCESS: {args.token_env} is not set; canonical comparison not run")
        return 3
    _, keys, errors = reconcile.load_manifest()
    if errors:
        print("\n".join(errors))
        return 1
    snapshot = freeze(keys, Reader(token))
    args.output.mkdir(mode=0o700)
    (args.output / "snapshot.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"froze {len(snapshot['artifacts'])} artifacts; {len(snapshot['errors'])} unreadable")
    for error in snapshot["errors"]:
        print("UNREADABLE", error)
    return 0 if not snapshot["errors"] else 4


if __name__ == "__main__":
    sys.exit(main())
