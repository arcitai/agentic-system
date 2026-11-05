#!/usr/bin/env python3
"""Publish Factory's Git-owned documentation projections to one public status table (#122).

Writes only rows keyed by stable Keys from scripts/reconcile.py projections: release label,
Lab workspace declaration and per-skill distribution state. It never writes a Notion-owned
original. One run is serialized (CI concurrency plus a local lock), marks propagation pending
first, upserts idempotently by Key and content hash, reads an uncertain write back before one
same-identity retry, reads the whole affected set back, and only then marks it complete. A
failure stays visible as failed. Without --live it prints the plan and touches nothing.
"""

import argparse
import datetime
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reconcile  # noqa: E402

MARKER = "run/propagation"
FIELDS = ("label", "summary", "commit", "hash", "propagation")


class AccessError(Exception):
    """Missing, expired or unshared access: stop the whole run; nothing else is attempted."""


class UncertainWrite(Exception):
    """Timeout, rate limit or server error: the write may or may not have been applied."""


class NotionTable:
    """Rows of one dedicated public data source; properties are Key (title) and rich text."""

    API = "https://api.notion.com/v1"
    NAMES = {"label": "Label", "summary": "Summary", "commit": "Commit", "hash": "Content hash", "propagation": "Propagation"}

    def __init__(self, token, data_source, public_url):
        self.token, self.data_source, self.public_url = token, data_source, public_url

    def _call(self, method, path, body=None):
        request = urllib.request.Request(self.API + path, method=method, data=None if body is None else json.dumps(body).encode(),
                                         headers={"Authorization": "Bearer " + self.token, "Notion-Version": "2026-03-11",
                                                  "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in (401, 403, 404):
                raise AccessError(f"HTTP {error.code} on {method} {path.split('?')[0]}") from None
            raise UncertainWrite(f"HTTP {error.code} on {method}") from None
        except (urllib.error.URLError, TimeoutError) as error:
            raise UncertainWrite(str(error)) from None

    def _props(self, key, row):
        props = {"Key": {"title": [{"text": {"content": key}}]}}
        for field in FIELDS:
            if field in row:
                props[self.NAMES[field]] = {"rich_text": [{"text": {"content": str(row[field])[:1900]}}]}
        return props

    def query(self, key):
        found = self._call("POST", f"/data_sources/{self.data_source}/query",
                           {"filter": {"property": "Key", "title": {"equals": key}}, "page_size": 10})["results"]
        rows = []
        for page in found:
            p = page["properties"]
            rows.append({"id": page["id"], **{f: "".join(t.get("plain_text", "") for t in p.get(n, {}).get("rich_text", []))
                                             for f, n in self.NAMES.items()}})
        return rows

    def create(self, key, row):
        return self._call("POST", "/pages", {"parent": {"data_source_id": self.data_source}, "properties": self._props(key, row)})["id"]

    def update(self, row_id, key, row):
        self._call("PATCH", f"/pages/{row_id}", {"properties": self._props(key, row)})

    def anonymous_status(self):
        try:
            with urllib.request.urlopen(urllib.request.Request(self.public_url, headers={"User-Agent": "factory-docs-readback"}), timeout=30) as r:
                return r.status
        except urllib.error.HTTPError as error:
            return error.code
        except urllib.error.URLError:
            return None


def upsert(target, key, row, log):
    """Create or update one Key; on an uncertain write, read back before one same-identity retry."""
    for attempt in (1, 2):
        existing = target.query(key)
        if len(existing) > 1:
            raise RuntimeError(f"{key}: {len(existing)} rows share this Key; resolve the duplicate by hand (nothing deleted)")
        if existing and all(existing[0].get(f, "") == str(row.get(f, "")) for f in row):
            log.append({"key": key, "action": "unchanged" if attempt == 1 else "confirmed-after-uncertain-write"})
            return
        try:
            if existing:
                target.update(existing[0]["id"], key, row)
            else:
                target.create(key, row)
            log.append({"key": key, "action": "updated" if existing else "created"})
            return
        except UncertainWrite as error:
            log.append({"key": key, "action": "uncertain", "attempt": attempt, "error": str(error)})
    after = target.query(key)
    if len(after) == 1 and all(after[0].get(f, "") == str(row.get(f, "")) for f in row):
        log.append({"key": key, "action": "confirmed-after-uncertain-write"})
        return
    raise RuntimeError(f"{key}: write still uncertain after readback and one retry")


def run(rows, target, lock_path, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc).isoformat()
    lock = Path(lock_path)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return {"result": "BUSY", "reason": f"another publication holds {lock}", "log": []}
    os.close(fd)
    log, commit = [], rows[0]["commit"] if rows else ""
    try:
        planned = {r["key"]: {f: r[f] for f in ("label", "summary", "commit", "hash")} for r in rows}
        changed = []
        for key, row in planned.items():
            existing = target.query(key)
            if len(existing) > 1:
                raise RuntimeError(f"{key}: {len(existing)} rows share this Key; resolve the duplicate by hand (nothing deleted)")
            if not existing or existing[0].get("hash") != row["hash"]:
                changed.append(key)
        if not changed:
            upsert(target, MARKER, {"summary": f"no-op at {commit[:12]}", "commit": commit, "propagation": f"complete {now}"}, log)
            return {"result": "NO-OP", "log": log, "public": target.anonymous_status()}
        upsert(target, MARKER, {"summary": f"{len(changed)} pending: {', '.join(changed)[:1500]}", "commit": commit,
                                "propagation": f"pending {now}"}, log)
        for key in changed:
            upsert(target, key, planned[key], log)
        wrong = [k for k in changed if [r.get("hash") for r in target.query(k)] != [planned[k]["hash"]]]
        public = target.anonymous_status()
        if wrong or public != 200:
            raise RuntimeError(f"readback failed: rows {wrong or 'ok'}, anonymous status {public}")
        upsert(target, MARKER, {"summary": f"{len(changed)} propagated: {', '.join(changed)[:1500]}", "commit": commit,
                                "propagation": f"complete {now}"}, log)
        return {"result": "PUBLISHED", "changed": changed, "log": log, "public": public}
    except AccessError as error:
        return {"result": "FAILED-ACCESS", "reason": str(error), "log": log}
    except (RuntimeError, UncertainWrite) as error:
        try:
            upsert(target, MARKER, {"summary": str(error)[:1500], "commit": commit, "propagation": f"failed {now}"}, log)
        except (AccessError, RuntimeError, UncertainWrite):
            pass
        return {"result": "FAILED", "reason": str(error), "log": log}
    finally:
        lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true", help="Write to the configured public table (requires the dedicated connection)")
    parser.add_argument("--lock", default=".factory-docs-publish.lock")
    args = parser.parse_args(argv)
    _, keys, errors = reconcile.load_manifest()
    if errors:
        print("\n".join(errors))
        return 1
    rows = reconcile.projections(keys=keys)
    if not args.live:
        print(json.dumps({"result": "PLAN", "rows": rows}, indent=2))
        return 0
    env = {name: os.environ.get(name, "") for name in ("FACTORY_PUBLIC_DOCS_TOKEN", "FACTORY_PUBLIC_DOCS_DATA_SOURCE", "FACTORY_PUBLIC_DOCS_URL")}
    missing = [name for name, value in env.items() if not value]
    if missing:
        print(json.dumps({"result": "FAILED-ACCESS", "reason": f"not configured: {', '.join(missing)}"}))
        return 3
    result = run(rows, NotionTable(*env.values()), args.lock)
    print(json.dumps(result, indent=2))
    return {"PUBLISHED": 0, "NO-OP": 0, "BUSY": 2, "FAILED-ACCESS": 3}.get(result["result"], 4)


if __name__ == "__main__":
    sys.exit(main())
