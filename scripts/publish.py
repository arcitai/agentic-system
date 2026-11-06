#!/usr/bin/env python3
"""Propagate Git-owned released references to their existing Notion Skills pages (#122).

Writes only artifacts whose manifest owner is git and label released-reference: the whole skill
directory through the Notion Skills API and the row's Version, Status and Source properties.
It never writes a Notion-owned original (those reach Git through scripts/export.py), and the
Source pin moves only to a release-tag commit. One run at a time (CI concurrency plus a local
lock) sets the commit status pending, writes serially by page identity, reads an uncertain write
back before one same-identity retry, reads every affected page back, then checks anonymous
content. Only a complete readback is success: every released reference's body, files and Version/Status/Source,
and for the affected pages an anonymous response that stays on the page's host and contains its expected content.
Anything less stays visibly pending (public browser readback, or release pending). Without --live it prints the plan and writes nothing.
"""

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tarfile
import urllib.error
import urllib.parse
import urllib.request
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent))
import notion_snapshot  # noqa: E402
import reconcile  # noqa: E402

CONTEXT = "agentic-system/docs-propagation"


class AccessError(Exception):
    """Missing, expired or unshared access: stop the run."""


class UncertainWrite(Exception):
    """Timeout, rate limit or server error: the write may or may not have been applied."""


def notion_edition(git_text, version):
    """The Notion copy of a released reference: Git's instructions with the pinned-reference preamble."""
    lines = git_text.split("\n")
    end = lines.index("---", 1)
    meta = dict(line.split(": ", 1) for line in lines[1:end] if ": " in line and not line.startswith(" "))
    body = "\n".join(lines[end + 1:]).lstrip("\n")
    title = re.match(r"# (.+)\n", body)
    if title:
        body = body[title.end():].lstrip("\n")
    head = f"**{title[1] if title else meta['name']}** · {version}\n\nPinned released reference; this copy preserves the published method for its version.\n\n"
    return f"---\nname: {meta['name']}\ndescription: {meta['description']}\n---\n\n" + head + body


def desired_files(root, item, version):
    files = reconcile.bundle_files(root, item["path"])
    files["SKILL.md"] = notion_edition(files["SKILL.md"].decode("utf-8"), version).encode("utf-8")
    return files


def tarball(name, files):
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for rel, data in sorted(files.items()):
            info = tarfile.TarInfo(f"{name}/{rel}")
            info.size, info.mode, info.mtime = len(data), 0o644, 0
            tar.addfile(info, io.BytesIO(data))
    return buffer.getvalue()


class NotionSkills:
    API = "https://api.notion.com/v1"

    def __init__(self, token):
        self.token = token
        self.reader = notion_snapshot.Reader(token)

    def _call(self, method, path, body=None, raw=None, content_type="application/json"):
        request = urllib.request.Request(self.API + path, method=method, data=raw if raw is not None else (None if body is None else json.dumps(body).encode()),
                                         headers={"Authorization": "Bearer " + self.token, "Notion-Version": notion_snapshot.NOTION_VERSION,
                                                  "Content-Type": content_type})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code in (401, 403, 404):
                raise AccessError(f"HTTP {error.code} on {method} {path}") from None
            raise UncertainWrite(f"HTTP {error.code} on {method} {path}") from None
        except (urllib.error.URLError, TimeoutError) as error:
            raise UncertainWrite(f"{method} {path}: {error}") from None

    def read(self, page, name):
        try:
            props = self.reader.get(f"/pages/{page}")
            skill = self.reader.get(f"/ai/skills/{page}")
            files = notion_snapshot.skill_files(self.reader.download(skill["url"]), name)
        except notion_snapshot.AccessError as error:
            raise AccessError(str(error)) from None
        except (urllib.error.URLError, TimeoutError, ValueError, tarfile.TarError) as error:
            raise UncertainWrite(f"readback {name}: {error}") from None
        p = props["properties"]
        return {"files": files, "public_url": props.get("public_url"), "types": {k: v.get("type") for k, v in p.items()},
                "revision": skill.get("version_id"),
                "Version": notion_snapshot.prop_text(p.get("Version")), "Status": notion_snapshot.prop_text(p.get("Status")),
                "Source": notion_snapshot.prop_text(p.get("Source"))}

    def upload(self, page, name, files):
        boundary = uuid.uuid4().hex
        body = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{name}.tar.gz"\r\n'
                f"Content-Type: application/gzip\r\n\r\n").encode() + tarball(name, files) + f"\r\n--{boundary}--\r\n".encode()
        self._call("POST", f"/ai/skills/{page}/upload", raw=body, content_type=f"multipart/form-data; boundary={boundary}")

    def set_properties(self, page, values, types):
        props = {}
        for name, value in values.items():
            kind = types.get(name)
            if kind in ("select", "status"):
                props[name] = {kind: {"name": value}}
            elif kind == "url":
                props[name] = {"url": value}
            elif kind == "rich_text":
                props[name] = {"rich_text": [{"text": {"content": value}}]}
            else:
                raise AccessError(f"property {name} has unsupported type {kind!r}; adjust the table schema")
        self._call("PATCH", f"/pages/{page}", {"properties": props})

    def public_receipt(self, url, markers, limit=2_000_000):
        """Plain anonymous GET (honest User-Agent, no browser imitation). Verified only if the response stays on the
        page's own host and its body contains every expected marker; a login page, error page or empty app shell
        with HTTP 200 is not a receipt."""
        result = {"url": url, "markers": markers, "verified": False}
        if not url:
            return {**result, "reason": "no public URL"}
        request = urllib.request.Request(url, headers={"User-Agent": "agentic-system-docs-readback (https://github.com/arcitai/agentic-systems)"})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                body = response.read(limit).decode("utf-8", "replace")
                result.update(status=response.status, final_url=response.geturl())
        except urllib.error.HTTPError as error:
            return {**result, "status": error.code, "reason": f"HTTP {error.code}"}
        except urllib.error.URLError as error:
            return {**result, "reason": str(error.reason)}
        return verify_receipt(result, body)


def verify_receipt(result, body):
    if urllib.parse.urlsplit(result.get("final_url") or "").netloc != urllib.parse.urlsplit(result["url"]).netloc:
        return {**result, "reason": f"redirected to {result.get('final_url')}"}
    missing = [m for m in result["markers"] if m not in body]
    if result.get("status") != 200 or missing:
        return {**result, "missing": missing, "reason": f"HTTP {result.get('status')}; expected content not in the anonymous response"}
    return {**result, "verified": True}


def public_markers(root, item):
    """Content an anonymous reader must see: the skill name, its version and its first instruction sentence."""
    text = (Path(root) / item["path"] / "SKILL.md").read_text(encoding="utf-8")
    body = text.split("\n---\n", 1)[1]
    first = next(line for line in body.splitlines() if line.strip() and not line.startswith("#"))
    return [item["key"].split("/", 1)[1], reconcile.git_skill_version(root, item["path"]), first.strip()[:60]]


class CommitStatus:
    """The native, visible receipt: one GitHub commit status per propagated commit."""

    def __init__(self, token, repository, sha):
        self.token, self.repository, self.sha = token, repository, sha

    def set(self, state, description):
        if not self.token:
            return
        request = urllib.request.Request(f"https://api.github.com/repos/{self.repository}/statuses/{self.sha}", method="POST",
                                         data=json.dumps({"state": state, "context": CONTEXT, "description": description[:140]}).encode(),
                                         headers={"Authorization": "Bearer " + self.token, "Accept": "application/vnd.github+json"})
        urllib.request.urlopen(request, timeout=30).close()


def matches(root, item, action, current):
    differ = reconcile.bundle_differences(root, item["path"], current["files"])
    props = {k: action[k.lower()] for k in ("Version", "Status", "Source")}
    return not differ and all(current.get(k) == v for k, v in props.items()), differ


def write_with_readback(write, check, log, key, what):
    """One write; on an uncertain result read back first, then retry once with the same identity."""
    for attempt in (1, 2):
        try:
            write()
            if check():
                log.append({"key": key, "action": what})
                return
            log.append({"key": key, "action": f"{what}-readback-differs", "attempt": attempt})
        except UncertainWrite as error:
            log.append({"key": key, "action": "uncertain", "what": what, "attempt": attempt, "error": str(error)})
            try:
                if check():
                    log.append({"key": key, "action": f"{what}-confirmed-after-uncertain-write"})
                    return
            except UncertainWrite:
                pass
    raise RuntimeError(f"{key}: {what} not confirmed after readback and one retry")


def run(root, actions, keys, target, status, lock_path):
    lock = Path(lock_path)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError:
        return {"result": "BUSY", "reason": f"another publication holds {lock}", "log": []}
    os.close(fd)
    log, urls = [], {}
    try:
        status.set("pending", f"propagating {len(actions)} released reference(s)" if actions else "verifying released references")
        for action in actions:  # only Git-owned released references are ever written
            item = keys.get(action["key"], {})
            if item.get("owner") != "git" or item.get("label") != "released-reference" or action.get("page") != item.get("notion"):
                raise RuntimeError(f"{action['key']}: refused; only Git-owned released references are propagated")
        for action in actions:
            item, name = keys[action["key"]], action["key"].split("/", 1)[1]
            current = target.read(action["page"], name)
            if current.get("Status") != reconcile.RELEASED_STATUS and not item.get("cutover"):
                raise RuntimeError(f"{action['key']}: page Status is {current.get('Status')!r}, not {reconcile.RELEASED_STATUS!r}; "
                                   "refusing to write a page that is not a released-reference copy without a cutover record")
            if reconcile.version_tuple(current.get("Version")) > reconcile.version_tuple(action["version"]):
                raise RuntimeError(f"{action['key']}: Notion copy {current.get('Version')} is newer than {action['version']}; refusing a downgrade")
            same, differ = matches(root, item, action, current)
            if same:
                log.append({"key": action["key"], "action": "unchanged"})
                continue
            if differ:
                files = desired_files(root, item, action["version"])
                write_with_readback(lambda: target.upload(action["page"], name, files),
                                    lambda: not reconcile.bundle_differences(root, item["path"], target.read(action["page"], name)["files"]),
                                    log, action["key"], "upload")
            values = {k: action[k.lower()] for k in ("Version", "Status", "Source")}
            types = current["types"]
            write_with_readback(lambda: target.set_properties(action["page"], values, types),
                                lambda: all(target.read(action["page"], name).get(k) == v for k, v in values.items()),
                                log, action["key"], "properties")
        receipts, pending_release, drift = {}, [], []
        for key, item in sorted(keys.items()):  # the whole coherent set, after all writes, actions or not
            if item.get("label") != "released-reference" or item.get("status", "active") != "active":
                continue
            current = target.read(item["notion"], key.split("/", 1)[1])
            pin = reconcile.released_pin(root, item, current.get("Source"))
            if pin is None:
                pending_release.append(key)
                continue
            want = {"Version": reconcile.git_skill_version(root, item["path"]), "Status": reconcile.RELEASED_STATUS, "Source": pin}
            differ = reconcile.bundle_differences(root, item["path"], current["files"])
            wrong = [f"{k}: {current.get(k)!r} != {v!r}" for k, v in want.items() if current.get(k) != v]
            if differ or wrong:
                drift.append(f"{key}: {'; '.join(differ + wrong)}")
            receipts[key] = {"revision": current.get("revision"), "public_url": current.get("public_url"),
                             "files": {rel: hashlib.sha256(reconcile.file_bytes(e)).hexdigest() for rel, e in sorted(current["files"].items())}}
        if drift:
            raise RuntimeError("final readback differs: " + " | ".join(drift))
        if pending_release:
            status.set("pending", f"release pending for {', '.join(pending_release)}; nothing written for them")
            return {"result": "RELEASE-PENDING", "pending_release": pending_release, "receipts": receipts, "log": log}
        affected = [a["key"] for a in actions] or sorted(receipts)
        checks = [target.public_receipt(receipts[k]["public_url"], public_markers(root, keys[k])) for k in affected]
        unverified = [c for c in checks if not c["verified"]]
        if unverified:
            status.set("pending", f"API readback complete; public browser readback pending for {len(unverified)} page(s)")
            return {"result": "PUBLIC-READBACK-PENDING", "browser_checklist": unverified, "receipts": receipts, "log": log}
        status.set("success", f"released references only: {len(actions)} propagated; set read back; public content verified for {len(checks)} page(s)")
        return {"result": "PUBLISHED" if actions else "NO-OP", "public": checks, "receipts": receipts, "log": log}
    except AccessError as error:
        status.set("failure", f"access missing or expired: {error}")
        return {"result": "FAILED-ACCESS", "reason": str(error), "log": log}
    except (RuntimeError, UncertainWrite) as error:
        status.set("failure", str(error))
        return {"result": "FAILED", "reason": str(error), "log": log}
    finally:
        lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True, help="Canonical snapshot frozen just before (scripts/notion_snapshot.py)")
    parser.add_argument("--live", action="store_true", help="Write through the dedicated connection")
    parser.add_argument("--lock", default=".agentic-system-docs-publish.lock")
    args = parser.parse_args(argv)
    _, keys, errors = reconcile.load_manifest()
    if errors:
        print("\n".join(errors))
        return 1
    actions = reconcile.plan(reconcile.ROOT, keys, args.snapshot)
    if not args.live:
        print(json.dumps({"result": "PLAN", "actions": actions}, indent=2))
        return 0
    token = os.environ.get("AGENTIC_SYSTEMS_PUBLIC_DOCS_TOKEN", "")
    if not token:
        print(json.dumps({"result": "FAILED-ACCESS", "reason": "not configured: AGENTIC_SYSTEMS_PUBLIC_DOCS_TOKEN"}))
        return 3
    status = CommitStatus(os.environ.get("GITHUB_TOKEN", ""), os.environ.get("GITHUB_REPOSITORY", ""), os.environ.get("AGENTIC_SYSTEMS_DOCS_SHA", ""))
    result = run(reconcile.ROOT, actions, keys, NotionSkills(token), status, args.lock)
    print(json.dumps(result, indent=2))
    return {"PUBLISHED": 0, "NO-OP": 0, "PUBLIC-READBACK-PENDING": 5, "RELEASE-PENDING": 6, "BUSY": 2, "FAILED-ACCESS": 3}.get(result["result"], 4)


if __name__ == "__main__":
    sys.exit(main())
