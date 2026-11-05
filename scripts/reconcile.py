#!/usr/bin/env python3
"""Reconcile Factory's documentation sources with their owners (#122), read-only.

Validates docs/sources.json, maps a Git diff to the affected artifacts, optionally compares
the Git exports with a frozen canonical snapshot, and always reports a visible result:
NO-OP, CHANGES, ATTENTION or CONFLICT. It never writes to Notion, and never treats an older
Git export as newer than its Notion original. Exit 1 only on CONFLICT or an invalid manifest.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "docs/sources.json"
GROUPS = ("foundation", "agent-ops", "adlc")
KEY = re.compile(r"^[a-z]+/[a-z0-9]+(?:-[a-z0-9]+)*$")
LABELS = {"notion": {"authoring-edition", "export"}, "git": {"released-reference", "main-working"}}
STATUSES = {"active", "renamed", "retired"}
PRIVATE = (".factory-task", ".claude", ".git", "dist", ".venv")
# Exported artifacts carry their canonical binding in these lines; editing an export without
# changing its binding means the Notion original was bypassed.
BINDING = {"declaration": re.compile(r"^# Canonical YAML SHA-256 .*$|^definition_version: .*$", re.M),
           "skill": re.compile(r'^  (?:version|updated): ".*"$', re.M)}


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout


def load_manifest(root=ROOT):
    root = Path(root)
    data = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    errors, keys, paths = [], {}, {}
    if data.get("format") != 1:
        errors.append("manifest: format must be 1")
    for item in data.get("artifacts", []):
        key = item.get("key", "")
        status = item.get("status", "active")
        if not KEY.fullmatch(key) or key in keys:
            errors.append(f"{key or '?'}: invalid or duplicate key")
        keys[key] = item
        if item.get("owner") not in LABELS or item.get("label") not in LABELS.get(item.get("owner"), ()):
            errors.append(f"{key}: owner/label combination is not allowed")
        if status not in STATUSES:
            errors.append(f"{key}: unknown status {status}")
        if status == "renamed" and item.get("renamed_to") not in {i.get("key") for i in data["artifacts"]}:
            errors.append(f"{key}: renamed_to must name another key")
        path = item.get("path")
        if item.get("label") in ("export", "released-reference", "main-working") and not path:
            errors.append(f"{key}: a Git path is required for label {item.get('label')}")
        if path:
            if any(part in PRIVATE for part in Path(path).parts):
                errors.append(f"{key}: private path {path} cannot be a public source")
            if status == "active":
                if not (root / path).exists():
                    errors.append(f"{key}: path {path} does not exist")
                if path in paths:
                    errors.append(f"{key}: path {path} already owned by {paths[path]}")
                paths[path] = key
        if item.get("owner") == "notion" and not re.fullmatch(r"[0-9a-f-]{36}", item.get("notion", "")):
            errors.append(f"{key}: a Notion-owned artifact needs its page id")
    skills = {p.parent.relative_to(root).as_posix() for g in GROUPS for p in (root / g).glob("*/SKILL.md")}
    mapped = {i["path"] for i in keys.values() if i.get("kind") == "skill" and i.get("path")
              and i.get("status", "active") == "active"}
    errors += [f"skill {s}: no manifest entry" for s in sorted(skills - mapped)]
    errors += [f"skill {s}: manifest entry without SKILL.md" for s in sorted(mapped - skills)]
    return data, keys, errors


def owner_of(keys, path):
    best = None
    for item in keys.values():
        p = item.get("path")
        if p and item.get("status", "active") == "active" and (path == p or path.startswith(p.rstrip("/") + "/")):
            if best is None or len(p) > len(best["path"]):
                best = item
    return best


def binding_changed(root, item, base, head):
    pattern = BINDING.get(item["kind"])
    target = item["path"] + ("/SKILL.md" if item["kind"] == "skill" else "")

    def lines(rev):
        try:
            return pattern.findall(git(root, "show", f"{rev}:{target}"))
        except subprocess.CalledProcessError:
            return None
    return pattern is not None and lines(base) != lines(head)


def impact(root, keys, base, head):
    items = []
    diff = git(root, "diff", "--name-status", "-M", base, head)
    for line in diff.splitlines():
        status, *names = line.split("\t")
        old, new = names[0], names[-1]
        for path in {old, new}:
            if any(part in PRIVATE for part in Path(path).parts):
                items.append({"level": "CONFLICT", "path": path, "reason": "private path in a public diff"})
        item = owner_of(keys, new) or owner_of(keys, old)
        entry = {"path": new, "change": status[0], "key": item["key"] if item else None}
        if status[0] == "R" and old != new:
            entry["from"] = old
        former = next((i for i in keys.values() if i.get("path") and i.get("status", "active") != "active"
                       and (old == i["path"] or old.startswith(i["path"].rstrip("/") + "/"))), None)
        if item is None and former is not None and status[0] in "DR":
            entry.update(key=former["key"], level="CHANGE", reason=f"{former['status']} per manifest; keep its Key and readers' route")
        elif item is None:
            entry.update(level="ATTENTION", reason="no owning manifest entry; add one before publication")
        elif item["owner"] == "notion":
            if binding_changed(root, item, base, head):
                entry.update(level="CHANGE", reason="deliberate export with a new canonical binding; review against the frozen original")
            else:
                entry.update(level="CONFLICT", reason="Git edit of a Notion-owned export without a new canonical binding; edit the Notion original first")
        elif item["label"] == "released-reference":
            if binding_changed(root, item, base, head):
                entry.update(level="CHANGE", reason="new released-reference version; update its Notion copy after the release, not before")
            else:
                entry.update(level="CONFLICT", reason="released references are immutable for their version; change the version for a new release")
        else:
            entry.update(level="CHANGE", reason="Git-owned source; projections may need propagation")
        if status[0] == "D" and item and not (Path(root) / item["path"]).exists():
            entry.update(level="CONFLICT", reason="artifact removed while its manifest entry is still active; mark it retired or renamed")
        items.append(entry)
        if status[0] == "R" and item is not None and former is not None:
            items.append({"path": old, "change": "R", "key": former["key"], "level": "CHANGE",
                          "reason": f"{former['status']} per manifest; keep its Key and readers' route"})
    return items


# ---- canonical comparison (snapshot produced outside CI by a reader with access) ----

PREAMBLE = re.compile(r"^(# |\*\*[^*]+\*\* · |Pinned released reference|Notion authoring edition|Supporting files are in )")


def normalize_skill(text):
    """Compare instructions, not Notion's rendering: frontmatter style, <br />, preambles, link markup."""
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
    # Notion renders a relative link either as inline code of its text or as "text (`target`)";
    # reduce both forms and Git's [text](target) to the text. Supporting files are compared separately.
    text = re.sub(r"\[([^\]]+)\]\((?![a-z]+:)[^)\s]+\)", r"\1", text)
    text = re.sub(r"\s*\(`[^`]*(?:/|\.md)[^`]*`\)", "", text).replace("`", "")
    return meta, " ".join(text.split())


def version_tuple(value):
    return tuple(int(x) for x in re.findall(r"\d+", value or "")[:3]) or (0,)


def git_skill_version(root, path):
    match = re.search(r'^  version: "([^"]+)"', (Path(root) / path / "SKILL.md").read_text(encoding="utf-8"), re.M)
    return match[1] if match else ""


def compare(root, keys, snapshot_dir):
    snapshot_dir = Path(snapshot_dir)
    snap = json.loads((snapshot_dir / "snapshot.json").read_text(encoding="utf-8"))
    items = []
    for key, item in sorted(keys.items()):
        if item.get("status", "active") != "active" or item["kind"] not in ("skill", "declaration"):
            continue
        canon = snap["artifacts"].get(key)
        entry = {"key": key, "owner": item["owner"], "label": item["label"]}
        if canon is None:
            entry.update(level="ATTENTION", reason="not in the canonical snapshot (unreadable or not frozen)")
            items.append(entry)
            continue
        entry["canonical"] = {k: canon.get(k) for k in ("revision", "version", "readAt")}
        if not item.get("path"):
            entry.update(level="INFO", reason="authoring edition without a portable export; export only by a reviewed release")
            items.append(entry)
            continue
        if item["kind"] == "declaration":
            header = re.search(r"Canonical YAML SHA-256 [^:]*: ([0-9a-f]{64})", (Path(root) / item["path"]).read_text(encoding="utf-8"))
            same = bool(header) and header[1] == canon.get("sha256")
            entry.update(level="IN-SYNC" if same else "ATTENTION",
                         reason="export binding equals the canonical hash" if same else "canonical declaration changed after this export; export pending")
            items.append(entry)
            continue
        differ = []
        for rel, text in sorted(canon.get("files", {}).items()):
            local = Path(root) / item["path"] / rel
            if not local.is_file():
                differ.append(f"{rel}: missing in Git")
            elif rel == "SKILL.md":
                if normalize_skill(text) != normalize_skill(local.read_text(encoding="utf-8")):
                    differ.append(f"{rel}: instructions differ")
            elif hashlib.sha256(local.read_bytes()).hexdigest() != hashlib.sha256(text.encode("utf-8")).hexdigest():
                differ.append(f"{rel}: bytes differ")
        local_files = {p.relative_to(Path(root) / item["path"]).as_posix() for p in (Path(root) / item["path"]).rglob("*") if p.is_file()}
        differ += [f"{rel}: only in Git" for rel in sorted(local_files - set(canon.get("files", {})))]
        gv, cv = git_skill_version(root, item["path"]), canon.get("version", "")
        entry["git_version"] = gv
        if not differ:
            entry.update(level="IN-SYNC", reason="normalized instructions and supporting bytes equal")
        elif item["owner"] == "git":
            entry.update(level="ATTENTION", reason="Notion copy of a released reference drifted; correct the copy, never the release", differences=differ)
        elif version_tuple(cv) > version_tuple(gv):
            entry.update(level="ATTENTION", reason=f"canonical {cv} is newer than export {gv}; deliberate export pending (never overwrite Notion from Git)", differences=differ)
        else:
            entry.update(level="CONFLICT", reason=f"export {gv} differs from canonical {cv} without a newer original", differences=differ)
        items.append(entry)
    return items


# ---- projections that a publisher may write (Git-owned facts only) ----

def projections(root=ROOT, keys=None):
    root = Path(root)
    if keys is None:
        keys = load_manifest(root)[1]
    head = git(root, "rev-parse", "HEAD").strip()
    version = (root / "VERSION").read_text().strip()
    try:
        tag = git(root, "describe", "--tags", "--abbrev=0", "--match", "v*", "HEAD").strip()
        tagged = git(root, "rev-list", "-n1", tag).strip() == head
    except subprocess.CalledProcessError:
        tag, tagged = "", False
    rows = [{"key": "status/release", "label": "released" if tagged and tag == f"v{version}" else "main-working",
             "summary": (f"Release v{version}" if tagged and tag == f"v{version}" else
                         f"Main working revision {version} (unreleased); latest release {tag or 'none'}"),
             "commit": head}]
    decl = (root / "factory.yaml").read_text(encoding="utf-8")
    field = lambda name: (re.search(rf"^  {name}: ([^\s#]+)", decl, re.M) or [None, "?"])[1]
    dv = (re.search(r'^definition_version: "([^"]+)"', decl, re.M) or [None, "?"])[1]
    rows.append({"key": "status/lab-workspace", "label": "export",
                 "summary": f"Lab workspace {field('selected')} {field('channel')} {field('candidate_version')} (declaration {dv}; evidence docs/qualification.md)",
                 "commit": head})
    for key, item in sorted(keys.items()):
        if item.get("kind") != "skill" or item.get("status", "active") != "active":
            continue
        if item.get("path"):
            summary = f"{item['label']} {git_skill_version(root, item['path'])} at {item['path']}"
        else:
            summary = "authoring edition; no portable export in this revision"
        rows.append({"key": key, "label": item["label"], "summary": summary, "commit": head})
    for row in rows:
        row["hash"] = hashlib.sha256(json.dumps({k: row[k] for k in ("key", "label", "summary")}, sort_keys=True).encode()).hexdigest()
    return rows


def report(result, summary_path=None):
    lines = [f"## Documentation reconciliation: {result['result']}", "",
             f"Head `{result.get('head', '')[:12]}`, base `{(result.get('base') or 'none')[:12]}`; canonical comparison: {result['canonical']}.", ""]
    if result["result"] == "NO-OP":
        lines.append("No owned artifact changed; nothing to propagate.")
    for item in result["items"]:
        lines.append(f"- **{item['level']}** `{item.get('key') or item.get('path')}`: {item.get('reason', '')}")
    text = "\n".join(lines) + "\n"
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(text)
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Base commit for the impact diff (PR base or previous main commit)")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--canonical", type=Path, help="Frozen canonical snapshot directory (optional)")
    parser.add_argument("--json", type=Path, help="Write the full result here")
    args = parser.parse_args(argv)
    data, keys, errors = load_manifest(ROOT)
    result = {"head": git(ROOT, "rev-parse", args.head).strip(), "base": None, "items": [],
              "canonical": "NOT RUN (no snapshot supplied)"}
    result["items"] += [{"level": "CONFLICT", "reason": e} for e in errors]
    if args.base and not re.fullmatch(r"0+", args.base):
        result["base"] = git(ROOT, "rev-parse", args.base).strip()
        result["items"] += impact(ROOT, keys, result["base"], result["head"])
    if args.canonical:
        result["canonical"] = f"snapshot {args.canonical.name}"
        result["items"] += compare(ROOT, keys, args.canonical)
    levels = {i["level"] for i in result["items"]}
    result["result"] = ("CONFLICT" if "CONFLICT" in levels else "ATTENTION" if "ATTENTION" in levels
                        else "CHANGES" if "CHANGE" in levels else "NO-OP")
    result["projections"] = projections(ROOT, keys) if not errors else []
    if args.json:
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(report(result, os.environ.get("GITHUB_STEP_SUMMARY")))
    return 1 if result["result"] == "CONFLICT" else 0


if __name__ == "__main__":
    sys.exit(main())
