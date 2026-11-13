#!/usr/bin/env python3
"""Deliberately export Notion-owned skills from a frozen canonical snapshot into their portable
Git bundles (#122). Notion -> Git only, for keys whose manifest owner is notion; a Git-owned
released reference is refused. The export restores portable form from Notion's rendering
(frontmatter, preamble, title, line breaks, relative links), copies supporting files byte for
byte, writes nothing outside the selected bundle and records the canonical binding (revision,
version) in docs/sources.json. A link it cannot resolve to a bundled file stays as written and
is reported, never guessed.
"""

import argparse
import base64
import json
from pathlib import Path, PurePosixPath
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reconcile  # noqa: E402

PREAMBLE = re.compile(r"^(\*\*([^*]+)\*\* · \S+|Pinned released reference.*|Notion authoring edition.*|Supporting files are in .*)$")


def file_bytes(entry):
    if isinstance(entry, dict):
        return base64.b64decode(entry["base64"])
    return entry.encode("utf-8")


def portable_skill(text, name, version, updated, title, bundled, hints=None, list_indent=True):
    hints = hints or {}
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        raise ValueError(f"{name}: canonical SKILL.md has no frontmatter")
    meta, _ = reconcile.normalize_skill(text)
    if meta.get("name") != name or not meta.get("description"):
        raise ValueError(f"{name}: canonical frontmatter name/description mismatch")
    body = lines[lines.index("---", 1) + 1:]
    kept, seen, derived = [], 0, None
    for line in body:
        if line.strip():
            seen += 1
            match = PREAMBLE.match(line.strip()) if seen <= 4 else None
            if match:
                derived = derived or match.group(2)
                continue
        kept.append(line)
    while kept and not kept[0].strip():
        kept.pop(0)
    # Newer Skills API downloads keep the authored H1. Older renderings omit
    # it, so only those need the previous export's title restored.
    has_heading = bool(kept and re.fullmatch(r"# .+", kept[0]))
    restored = []
    for line in kept:
        first, *rest = line.split("<br />")
        marker = re.match(r"^(\s*)([-*+]|\d+[.)]) ", first)
        indent = " " * (len(marker[0])) if marker and list_indent else ""
        restored.append("\n".join([first] + [indent + part for part in rest]))
    text = "\n".join(restored)
    unresolved = []
    basenames = {}
    for path in bundled:
        basenames.setdefault(path.rsplit("/", 1)[-1], []).append(path)

    def resolve(token):
        path, _, anchor = token.partition("#")
        if path in bundled:
            return token
        if "/" not in path and len(basenames.get(path, [])) == 1:
            return basenames[path][0] + (f"#{anchor}" if anchor else "")
        return None

    def labelled(match):
        # Notion keeps the target but not where the link text starts: take the text from the previous
        # export's link to the same target; otherwise leave Notion's rendering and report it.
        target = resolve(match[2])
        for label in sorted(hints.get(target, ()), key=len, reverse=True):
            if target and label == target:  # a literal parenthesis around a bare link
                return f"{match[1]} ([{target}]({target}))"
            if target and match[1].endswith(label):
                return f"{match[1][:-len(label)]}[{label}]({target})"
        unresolved.append(f"{match[1][-40:]} -> {match[2]}")
        return match[0]

    def bare(match):
        target = resolve(match[1])
        return f"[{match[1]}]({target})" if target else match[0]

    # "text (`target`)" is Notion's rendering of [text](target); `file.md` of [file.md](path).
    text = re.sub(r"(?<![\w`\]])([^\n()`\[\]]*?[^\s()`\[\]]) \(`([^`\s]+\.md(?:#[^`\s]*)?)`\)", labelled, text)
    text = re.sub(r"`([^`\s]+\.md(?:#[^`\s]*)?)`", bare, text)
    header = (f"---\nname: {name}\ndescription: {meta['description']}\nlicense: MIT\nmetadata:\n"
              f'  version: "{version}"\n  updated: "{updated}"\n---\n\n')
    if not has_heading:
        header += f"# {title or derived or name}\n\n"
    return header + text.rstrip("\n") + "\n", unresolved


def export(root, snapshot_dir, key, title=None):
    root, snapshot_dir = Path(root), Path(snapshot_dir)
    data, keys, errors = reconcile.load_manifest(root)
    item = keys.get(key)
    if item is not None and item.get("path"):
        # A first export creates its own bundle; only that bundle may be missing.
        first = {f"{key}: path {item['path']} does not exist", f"skill {item['path']}: manifest entry without SKILL.md"}
        errors = [e for e in errors if e not in first]
    if errors or item is None:
        raise ValueError("; ".join(errors) or f"{key}: not in the manifest")
    if item["owner"] != "notion" or item["kind"] != "skill" or not item.get("path"):
        raise ValueError(f"{key}: only Notion-owned skills with a Git export path are exported")
    snap = json.loads((snapshot_dir / "snapshot.json").read_text(encoding="utf-8"))
    canon = snap["artifacts"].get(key)
    if not canon:
        raise ValueError(f"{key}: not in the canonical snapshot")
    if not re.fullmatch(r"\d+\.\d+\.\d+", canon.get("version", "")) or not canon.get("lastEdited"):
        raise ValueError(f"{key}: canonical version/edit time missing")
    target = root / item["path"]
    name = target.name
    existing = target / "SKILL.md"
    if title is None and existing.is_file():
        heading = re.search(r"^# (.+)$", existing.read_text(encoding="utf-8"), re.M)
        title = heading[1] if heading else None
    files = canon["files"]
    for rel in files:  # the snapshot is input: never write outside the bundle
        parts = PurePosixPath(rel).parts
        if not rel or "\\" in rel or PurePosixPath(rel).is_absolute() or ".." in parts or not parts:
            raise ValueError(f"{key}: unsafe file path {rel!r} in the snapshot")
    bundled = set(files)
    hints = {}
    if existing.is_file():
        for label, link in re.findall(r"\[([^\]]+)\]\((?![a-z]+:)([^)\s]+)\)", existing.read_text(encoding="utf-8")):
            hints.setdefault(link, set()).add(label)
    list_indent = True
    if existing.is_file():  # keep the previous export's continuation style; a first export indents
        previous = existing.read_text(encoding="utf-8")
        if re.search(r"(?m)^(?:[-*+]|\d+[.)]) .*\n(?! |\n|[-*+] |\d+[.)] |#)\S", previous) and not re.search(r"(?m)^(?:[-*+]|\d+[.)]) .*\n  +\S", previous):
            list_indent = False
    skill, unresolved = portable_skill(file_bytes(files["SKILL.md"]).decode("utf-8"), name, canon["version"],
                                       canon["lastEdited"][:10], title, bundled, hints, list_indent)
    written = {"SKILL.md": skill.encode("utf-8")}
    for rel, entry in files.items():
        if rel != "SKILL.md":
            written[rel] = file_bytes(entry)
    stale = sorted(p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()) if target.exists() else []
    removed = [rel for rel in stale if rel not in written]
    for rel, content in written.items():
        out = target / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(content)
    for rel in removed:
        (target / rel).unlink()
    item["binding"] = {"revision": canon["revision"], "version": canon["version"]}
    (root / reconcile.MANIFEST).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"key": key, "path": item["path"], "version": canon["version"], "revision": canon["revision"],
            "files": sorted(written), "removed": removed, "unresolved_links": unresolved}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--key", action="append", required=True)
    parser.add_argument("--title", help="Fallback H1 when Notion omits it (default: the existing export's title)")
    args = parser.parse_args(argv)
    results = []
    for key in args.key:
        try:
            results.append(export(reconcile.ROOT, args.snapshot, key, args.title))
        except (ValueError, KeyError, OSError) as error:
            print(f"EXPORT REFUSED {key}: {error}")
            return 1
    print(json.dumps(results, indent=2))
    return 1 if any(r["unresolved_links"] for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
