#!/usr/bin/env python3
"""Freeze the canonical Notion originals named in docs/sources.json into a neutral snapshot
for scripts/reconcile.py --canonical (#122). Read-only: page/block GETs and the Notion Skills
API download; nothing is written to Notion. The connection comes from the environment
variable named by --token-env and is never printed or stored.
"""

import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path
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


def call(token, path):
    request = urllib.request.Request(API + path, headers={"Authorization": "Bearer " + token, "Notion-Version": NOTION_VERSION})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as error:
        if error.code in (401, 403, 404):
            raise AccessError(f"{path.split('?')[0]}: HTTP {error.code} (missing, expired or unshared access)") from None
        raise


def plain(rich):
    return "".join(t.get("plain_text", "") for t in rich or [])


def freeze(keys, token, read_at=None):
    read_at = read_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
    artifacts, errors = {}, []
    for key, item in sorted(keys.items()):
        if item.get("status", "active") != "active" or item["kind"] not in ("skill", "declaration"):
            continue
        try:
            if item["kind"] == "skill":
                page = call(token, f"/pages/{item['notion']}")
                version = plain((page["properties"].get("Version") or {}).get("rich_text"))
                skill = call(token, f"/ai/skills/{item['notion']}")
                with urllib.request.urlopen(skill["url"], timeout=60) as response:
                    archive = response.read()
                files = {}
                with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
                    for member in tar.getmembers():
                        if member.isfile():
                            files[member.name.split("/", 1)[1]] = tar.extractfile(member).read().decode("utf-8")
                artifacts[key] = {"revision": skill.get("version_id"), "version": version, "readAt": read_at,
                                  "lastEdited": page.get("last_edited_time"), "files": files,
                                  "archiveSha256": hashlib.sha256(archive).hexdigest()}
            else:
                children = call(token, f"/blocks/{item['notion']}/children?page_size=100")["results"]
                code = [b for b in children if b["type"] == "code" and b["code"].get("language") == "yaml"]
                if len(code) != 1:
                    raise AccessError(f"{key}: expected exactly one YAML code block, found {len(code)}")
                text = plain(code[0]["code"]["rich_text"]).replace("\r\n", "\n").rstrip("\n") + "\n"
                artifacts[key] = {"revision": code[0].get("last_edited_time"), "readAt": read_at,
                                  "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                                  "version": next((l.split('"')[1] for l in text.splitlines() if l.startswith("definition_version")), "")}
        except (AccessError, KeyError, IndexError, urllib.error.URLError) as error:
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
    snapshot = freeze(keys, token)
    args.output.mkdir(mode=0o700)
    (args.output / "snapshot.json").write_text(json.dumps(snapshot, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(f"froze {len(snapshot['artifacts'])} artifacts; {len(snapshot['errors'])} unreadable")
    for error in snapshot["errors"]:
        print("UNREADABLE", error)
    return 0 if not snapshot["errors"] else 4


if __name__ == "__main__":
    sys.exit(main())
