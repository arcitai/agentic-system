#!/usr/bin/env python3
"""Reconcile Factory's public documentation and skill distributions with their owners (#122).

Read-only. Validates docs/sources.json, maps a Git diff to the affected artifacts and, with a
frozen canonical snapshot (scripts/notion_snapshot.py), compares every distribution with its
original. Propagation follows ownership: a Notion-owned original reaches Git only through a
deliberate export bound to its canonical revision (scripts/export.py); a Git-owned released
reference reaches its Notion copy only from a release tag (scripts/publish.py); an editorial
change to a Notion page is a visible handoff with its exact before/after until the canonical
readback shows it applied. The result is always printed: NO-OP, CHANGES, ATTENTION or CONFLICT,
or UNVERIFIED when the canonical side was not read. Exit 1 only on CONFLICT.
"""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/sources.json"
GROUPS = ("foundation", "agent-ops", "adlc")
KEY = re.compile(r"^[a-z]+/[a-z0-9]+(?:-[a-z0-9]+)*$")
LABELS = {"notion": {"authoring-edition", "export"}, "git": {"released-reference", "main-working"}}
STATUSES = {"active", "renamed", "retired"}
KINDS = {"page", "database", "declaration", "skill", "doc", "code", "asset"}
PRIVATE = (".factory-task", ".claude", ".git", "dist", ".venv")
REPO_URL = "https://github.com/arcitai/factory"
RELEASED_STATUS = "Released reference"
# What binds an artifact to its source. A Notion-owned skill export is bound by its docs/sources.json binding
# (written by scripts/export.py); a declaration export by its recorded canonical hash; a released reference by
# its version line. Editing the artifact without changing that binding bypasses the original.
BINDING = {"declaration": re.compile(r"^# Canonical YAML SHA-256 .*$", re.M),
           "released-reference": re.compile(r'^  version: ".*"$', re.M)}
RANK = {"CONFLICT": 4, "ATTENTION": 3, "CHANGE": 2, "INFO": 1, "IN-SYNC": 0}


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def validate(data, root):
    errors, keys, paths = [], {}, {}
    if data.get("format") != 1:
        errors.append("manifest: format must be 1")
    all_keys = {i.get("key") for i in data.get("artifacts", [])}
    for item in data.get("artifacts", []):
        key, status, path = item.get("key", ""), item.get("status", "active"), item.get("path")
        if not KEY.fullmatch(key) or key in keys:
            errors.append(f"{key or '?'}: invalid or duplicate key")
        keys[key] = item
        if item.get("kind") not in KINDS:
            errors.append(f"{key}: kind must be one of {', '.join(sorted(KINDS))}")
        if item.get("owner") not in LABELS or item.get("label") not in LABELS.get(item.get("owner"), ()):
            errors.append(f"{key}: owner/label combination is not allowed")
        if status not in STATUSES:
            errors.append(f"{key}: unknown status {status}")
        if status == "renamed" and item.get("renamed_to") not in all_keys - {key}:
            errors.append(f"{key}: renamed_to must name another key")
        if item.get("label") in ("export", "released-reference", "main-working") and not path:
            errors.append(f"{key}: a Git path is required for label {item.get('label')}")
        if item.get("owner") == "notion" and not re.fullmatch(r"[0-9a-f-]{36}", item.get("notion", "")):
            errors.append(f"{key}: a Notion-owned artifact needs its page id")
        if item.get("label") == "released-reference" and not re.fullmatch(r"[0-9a-f-]{36}", item.get("notion", "")):
            errors.append(f"{key}: a released reference needs the page id of its Notion copy")
        binding = item.get("binding")
        if binding is not None and (item.get("label") != "export" or not binding.get("revision") or not binding.get("version")):
            errors.append(f"{key}: binding needs label export, revision and version")
        for pending in item.get("pending", []):
            if not pending.get("id") or not pending.get("after") or not pending.get("holder") or item.get("owner") != "notion":
                errors.append(f"{key}: pending handoff needs id, after and holder on a Notion-owned artifact")
        if path:
            if PurePosixPath(path).is_absolute() or ".." in PurePosixPath(path).parts or any(p in PRIVATE for p in PurePosixPath(path).parts):
                errors.append(f"{key}: path {path} is not a public repository path")
            if status == "active":
                if not (Path(root) / path).exists():
                    errors.append(f"{key}: path {path} does not exist")
                if path in paths:
                    errors.append(f"{key}: path {path} already owned by {paths[path]}")
                paths[path] = key
    for item in keys.values():
        if item.get("label") == "released-reference" and item.get("status", "active") == "active":
            shared = [k for k, other in keys.items() if other is not item and other.get("status", "active") == "active"
                      and other.get("notion") == item.get("notion")]
            if shared:
                errors.append(f"{item['key']}: its Notion copy's page id is also used by {', '.join(shared)}")
    skills = {p.parent.relative_to(root).as_posix() for g in GROUPS for p in (Path(root) / g).glob("*/SKILL.md")}
    mapped = {i["path"] for i in keys.values() if i.get("kind") == "skill" and i.get("path") and i.get("status", "active") == "active"}
    errors += [f"skill {s}: no manifest entry" for s in sorted(skills - mapped)]
    errors += [f"skill {s}: manifest entry without SKILL.md" for s in sorted(mapped - skills)]
    return keys, errors


def load_manifest(root=ROOT):
    root = Path(root)
    data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    keys, errors = validate(data, root)
    return data, keys, errors


def owner_of(keys, path, active=True):
    best = None
    for item in keys.values():
        p = item.get("path")
        if p and (item.get("status", "active") == "active") == active and (path == p or path.startswith(p.rstrip("/") + "/")):
            if best is None or len(p) > len(best["path"]):
                best = item
    return best


def manifest_at(root, rev):
    try:
        return {i["key"]: i for i in json.loads(git(root, "show", f"{rev}:{MANIFEST}")).get("artifacts", [])}
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        return {}


def binding_changed(root, item, base, head):
    if item["kind"] == "skill" and item["owner"] == "notion":
        before = manifest_at(root, base).get(item["key"], {}).get("binding")
        after = manifest_at(root, head).get(item["key"], {}).get("binding")
        return after is not None and before != after
    pattern = BINDING.get("released-reference" if item["label"] == "released-reference" else item["kind"])
    if pattern is None:
        return False
    target = item["path"] + ("/SKILL.md" if item["kind"] == "skill" else "")

    def lines(rev):
        try:
            return pattern.findall(git(root, "show", f"{rev}:{target}"))
        except subprocess.CalledProcessError:
            return None
    return lines(base) != lines(head)


def impact(root, keys, base, head):
    items = []
    before = manifest_at(root, base)
    for key, item in sorted(keys.items()):
        old = before.get(key)
        if old and (old.get("owner"), old.get("label")) != (item.get("owner"), item.get("label")):
            items.append({"key": key, "level": "ATTENTION", "reason": f"ownership change {old.get('owner')}/{old.get('label')} -> "
                          f"{item.get('owner')}/{item.get('label')}: a source cutover needs an owner decision and its own review"})
    for line in git(root, "diff", "--name-status", "-M", base, head).splitlines():
        status, *names = line.split("\t")
        old, new = names[0], names[-1]
        for path in {old, new}:
            if any(part in PRIVATE for part in PurePosixPath(path).parts):
                items.append({"level": "CONFLICT", "path": path, "reason": "private path in a public diff"})
        item = owner_of(keys, new) or owner_of(keys, old)
        former = owner_of(keys, old, active=False)
        entry = {"path": new, "change": status[0], "key": item["key"] if item else None}
        if status[0] == "R" and old != new:
            entry["from"] = old
        if item is None and former is not None and status[0] in "DR":
            entry.update(key=former["key"], level="CHANGE", reason=f"{former['status']} per manifest; keep its Key and readers' route")
        elif item is None:
            entry.update(level="ATTENTION", reason="no owning manifest entry; add one before publication")
        elif item["owner"] == "notion":
            if binding_changed(root, item, base, head):
                entry.update(level="CHANGE", reason="deliberate export with a new canonical binding; verify against the frozen original")
            else:
                entry.update(level="CONFLICT", reason="Git edit of a Notion-owned export without a new canonical binding; edit the Notion original first")
        elif item["label"] == "released-reference":
            if binding_changed(root, item, base, head):
                entry.update(level="CHANGE", reason="new released-reference version; its Notion copy is updated from the release tag, not before")
            else:
                entry.update(level="CONFLICT", reason="released references are immutable for their version; change the version for a new release")
        else:
            entry.update(level="CHANGE", reason="Git-owned source, public natively in this repository")
        if status[0] == "D" and item and not (Path(root) / item["path"]).exists():
            entry.update(level="CONFLICT", reason="artifact removed while its manifest entry is still active; mark it retired or renamed")
        items.append(entry)
        if status[0] == "R" and item is not None and former is not None:
            items.append({"path": old, "change": "R", "key": former["key"], "level": "CHANGE",
                          "reason": f"{former['status']} per manifest; keep its Key and readers' route"})
    return items


# ---- comparing a distribution with its original ----

PREAMBLE = re.compile(r"^(# |\*\*[^*]+\*\* · |Pinned released reference|Notion authoring edition|Supporting files are in )")


def file_bytes(entry):
    return base64.b64decode(entry["base64"]) if isinstance(entry, dict) else entry.encode("utf-8")


def normalize_skill(text):
    """Compare instructions and link targets, not Notion's rendering (frontmatter style, <br />, preamble, link markup)."""
    lines = text.replace("\r\n", "\n").split("\n")
    meta, body = {}, lines
    if lines and lines[0] == "---" and "---" in lines[1:]:
        end = lines.index("---", 1)
        front, body, i = lines[1:end], lines[end + 1:], 0
        while i < len(front):
            key, _, value = front[i].partition(":")
            value, i = value.strip(), i + 1
            if value in ("|-", "|", ">-", ">"):
                block = []
                while i < len(front) and front[i].startswith("  "):
                    block.append(front[i].strip())
                    i += 1
                value = " ".join(block)
            if key in ("name", "description"):
                meta[key] = value.strip('"')
    kept, seen = [], 0
    for line in body:
        if line.strip():
            seen += 1
            if seen <= 4 and PREAMBLE.match(line.strip()):
                continue
        kept.append(line)
    text = "\n".join(kept).replace("<br />", " ")

    # Notion renders [text](target) as "text (`target`)", and [file.md](path/file.md) or [t](t) as `file.md`/`t`.
    # Reduce Git links to the same text-plus-target form so a changed target is still a difference.
    def link(match):
        label, target = match[1], match[2]
        if label == target or label == target.split("#")[0].rsplit("/", 1)[-1]:
            return label
        return f"{label} ({target})"
    text = re.sub(r"\[([^\]]+)\]\((?![a-z]+:)([^)\s]+)\)", link, text)
    text = text.replace("`", "")
    return meta, " ".join(text.split())


def bundle_files(root, path):
    folder = Path(root) / path
    return {p.relative_to(folder).as_posix(): p.read_bytes() for p in sorted(folder.rglob("*")) if p.is_file()}


def bundle_differences(root, path, canonical_files):
    local = bundle_files(root, path)
    differ = []
    for rel, entry in sorted(canonical_files.items()):
        if rel not in local:
            differ.append(f"{rel}: missing in Git")
        elif rel == "SKILL.md":
            if normalize_skill(file_bytes(entry).decode("utf-8")) != normalize_skill(local[rel].decode("utf-8")):
                differ.append(f"{rel}: instructions or link targets differ")
        elif hashlib.sha256(local[rel]).digest() != hashlib.sha256(file_bytes(entry)).digest():
            differ.append(f"{rel}: bytes differ")
    differ += [f"{rel}: only in Git" for rel in sorted(set(local) - set(canonical_files))]
    return differ


def version_tuple(value):
    return tuple(int(x) for x in re.findall(r"\d+", value or "")[:3]) or (0,)


def git_skill_version(root, path):
    match = re.search(r'^  version: "([^"]+)"', (Path(root) / path / "SKILL.md").read_text(encoding="utf-8"), re.M)
    return match[1] if match else ""


def release_context(root):
    """(tag, tag commit, is HEAD that release) — a release is the tag that equals VERSION."""
    version = (Path(root) / "VERSION").read_text().strip()
    head = git(root, "rev-parse", "HEAD").strip()
    try:
        commit = git(root, "rev-list", "-n1", f"v{version}").strip()
    except subprocess.CalledProcessError:
        return f"v{version}", None, False
    return f"v{version}", commit, commit == head


def released_pin(root, item, current_source):
    """Keep an existing pin while the bundle there equals the working tree; else pin the release commit."""
    match = re.search(r"/blob/([0-9a-f]{40})/", current_source or "")
    if match:
        try:
            subprocess.run(["git", "diff", "--quiet", match[1], "HEAD", "--", item["path"]], cwd=root, check=True,
                           capture_output=True)
            return current_source
        except subprocess.CalledProcessError:
            pass
    _, commit, is_release = release_context(root)
    return f"{REPO_URL}/blob/{commit}/{item['path']}/SKILL.md" if is_release else None


def check_pending(item, canon):
    out = []
    for pending in item.get("pending", []):
        if pending.get("file") is None:
            where = canon.get("text") or ""
        else:
            where = file_bytes(canon.get("files", {}).get(pending["file"], "")).decode("utf-8", "replace")
        flat = " ".join(where.replace("<br />", " ").split())
        after, before = " ".join(pending["after"].split()), " ".join(pending.get("before", "").split())
        entry = {"key": item["key"], "pending": pending["id"], "holder": pending["holder"], "level": "ATTENTION"}
        if after in flat:
            entry["reason"] = f"handoff {pending['id']} is applied in the canonical readback; remove the pending entry (and export if needed)"
        elif before and before not in flat:
            entry["reason"] = f"handoff {pending['id']}: canonical text changed since it was prepared; re-prepare against the new original"
        else:
            verb = "after" if pending.get("action") == "insert-after" else "replace"
            entry["reason"] = (f"handoff {pending['id']} pending for {pending['holder']}: "
                               + (f"insert after {before[:120]!r}: {after[:160]!r}" if verb == "after" else f"replace {before[:120]!r} with {after[:160]!r}"))
        out.append(entry)
    return out


def compare(root, keys, snapshot_dir):
    snap = json.loads((Path(snapshot_dir) / "snapshot.json").read_text(encoding="utf-8"))
    items = [{"key": None, "level": "ATTENTION", "reason": f"unreadable canonical source: {e}"} for e in snap.get("errors", [])]
    for key, item in sorted(keys.items()):
        if item.get("status", "active") != "active" or item["kind"] not in ("skill", "declaration", "page"):
            continue
        canon = snap["artifacts"].get(key)
        entry = {"key": key, "owner": item["owner"], "label": item["label"]}
        if canon is None:
            items.append({**entry, "level": "ATTENTION", "reason": "not in the canonical snapshot (unreadable or not frozen)"})
            continue
        entry["canonical"] = {k: canon.get(k) for k in ("revision", "version", "readAt")}
        items += check_pending(item, canon)
        if item["kind"] == "page":
            continue
        if item["kind"] == "declaration":
            header = re.search(r"Canonical YAML SHA-256 [^:]*: ([0-9a-f]{64})", (Path(root) / item["path"]).read_text(encoding="utf-8"))
            same = bool(header) and header[1] == canon.get("sha256")
            items.append({**entry, "level": "IN-SYNC" if same else "ATTENTION",
                          "reason": "export binding equals the canonical hash" if same else "canonical declaration changed after this export; export pending"})
            continue
        if not item.get("path"):
            items.append({**entry, "level": "INFO", "reason": "authoring edition without a portable export; export it deliberately when a distribution needs it"})
            continue
        differ = bundle_differences(root, item["path"], canon.get("files", {}))
        gv, cv = git_skill_version(root, item["path"]), canon.get("version", "")
        entry.update(git_version=gv, differences=differ)
        if item["owner"] == "git":
            if version_tuple(cv) > version_tuple(gv):
                items.append({**entry, "level": "ATTENTION", "downgrade": True,
                              "reason": f"Notion copy {cv} is newer than this Git revision's {gv}; refusing a downgrade"})
                continue
            pin = released_pin(root, item, canon.get("source"))
            props = {"Version": (canon.get("version"), gv), "Status": (canon.get("status"), RELEASED_STATUS), "Source": (canon.get("source"), pin)}
            drift = [f"{name}: {have!r} -> {want!r}" for name, (have, want) in props.items() if have != want]
            if not differ and not drift:
                entry.update(level="IN-SYNC", reason="Notion copy equals the released reference and its pinned source")
            elif pin is None:
                entry.update(level="ATTENTION", reason="released-reference change awaits its release tag before the Notion copy is updated", drift=drift)
            else:
                entry.update(level="ATTENTION", reason="Notion copy differs from the released reference; scripts/publish.py propagates it", drift=drift)
            items.append(entry)
            continue
        binding = item.get("binding")
        versions = {cv, gv} | ({binding["version"]} if binding else set())
        if len(versions) > 1 and not differ:
            entry.update(level="ATTENTION", reason=f"versions disagree (canonical {cv}, export {gv}"
                         + (f", binding {binding['version']}" if binding else "") + "); deliberate export pending")
        elif binding and binding["revision"] == canon.get("revision"):
            entry.update(level="IN-SYNC" if not differ else "CONFLICT",
                         reason="export equals its bound canonical revision" if not differ else "export differs from the canonical revision it claims")
        elif not differ:
            entry.update(level="IN-SYNC", reason="normalized instructions and supporting bytes equal" + (
                "; record the binding at the next export" if not binding else "; canonical revision changed without content change"))
        elif binding or version_tuple(cv) > version_tuple(gv):
            since = f" since bound revision {binding['revision'][:12]}" if binding else ""
            entry.update(level="ATTENTION", reason=f"canonical {cv} changed{since}; deliberate export pending (scripts/export.py; never overwrite Notion from Git)")
        else:
            entry.update(level="CONFLICT", reason=f"export {gv} differs from canonical {cv} without a newer original")
        items.append(entry)
    return items


def plan(root, keys, snapshot_dir):
    """Publisher actions: Git-owned released references whose Notion copy differs, only from a release tag."""
    snap = json.loads((Path(snapshot_dir) / "snapshot.json").read_text(encoding="utf-8"))["artifacts"]
    actions = []
    for entry in compare(root, keys, snapshot_dir):
        item = keys.get(entry.get("key") or "", {})
        if item.get("label") == "released-reference" and entry["level"] == "ATTENTION" and "pending" not in entry and not entry.get("downgrade"):
            pin = released_pin(root, item, snap.get(item["key"], {}).get("source"))
            if pin:
                actions.append({"key": item["key"], "page": item["notion"], "path": item["path"],
                                "version": git_skill_version(root, item["path"]), "status": RELEASED_STATUS, "source": pin})
    return actions


def report(result, summary_path=None):
    lines = [f"## Documentation reconciliation: {result['result']}", "",
             f"Head `{result.get('head', '')[:12]}`, base `{(result.get('base') or 'none')[:12]}`; canonical comparison: {result['canonical']}.", ""]
    if result["result"] == "NO-OP":
        lines.append("No owned artifact changed and every distribution equals its original; nothing to propagate.")
    if result["result"].startswith("UNVERIFIED"):
        lines.append("The canonical Notion originals were not read, so Notion-side changes and pending exports are unknown.")
    for item in sorted(result["items"], key=lambda i: -RANK.get(i["level"], 0)):
        lines.append(f"- **{item['level']}** `{item.get('key') or item.get('path')}`: {item.get('reason', '')}")
        for detail in item.get("differences", [])[:5] + item.get("drift", [])[:3]:
            lines.append(f"  - {detail}")
    text = "\n".join(lines) + "\n"
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(text)
    return text


def run(root, base=None, head="HEAD", canonical=None):
    data, keys, errors = load_manifest(root)
    result = {"head": git(root, "rev-parse", head).strip(), "base": None, "items": [], "canonical": "NOT RUN (no snapshot supplied)"}
    result["items"] += [{"level": "CONFLICT", "reason": e} for e in errors]
    if base and not re.fullmatch(r"0+", base):
        result["base"] = git(root, "rev-parse", base).strip()
        result["items"] += impact(root, keys, result["base"], result["head"])
    if canonical and not errors:
        result["canonical"] = f"snapshot {Path(canonical).name}"
        result["items"] += compare(root, keys, canonical)
        result["plan"] = plan(root, keys, canonical)
    elif not errors:
        result["items"] += [{"key": i["key"], "level": "ATTENTION", "pending": p["id"], "holder": p["holder"],
                             "reason": f"handoff {p['id']} pending for {p['holder']} (canonical not read)"}
                            for i in keys.values() for p in i.get("pending", [])]
    worst = max((RANK[i["level"]] for i in result["items"]), default=0)
    result["result"] = {4: "CONFLICT", 3: "ATTENTION", 2: "CHANGES"}.get(worst, "NO-OP")
    if not canonical and result["result"] in ("NO-OP", "CHANGES"):
        result["result"] = f"UNVERIFIED (Git side: {result['result']})"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Base commit for the impact diff (PR base or previous main commit)")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--canonical", type=Path, help="Frozen canonical snapshot directory (optional)")
    parser.add_argument("--json", type=Path, help="Write the full result here")
    args = parser.parse_args(argv)
    result = run(ROOT, args.base, args.head, args.canonical)
    if args.json:
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report(result, os.environ.get("GITHUB_STEP_SUMMARY")))
    return 1 if result["result"] == "CONFLICT" else 0


if __name__ == "__main__":
    sys.exit(main())
