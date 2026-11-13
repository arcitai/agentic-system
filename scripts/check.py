#!/usr/bin/env python3
"""Check Agentic Systems' deliberately small metadata format and portable local links."""

from datetime import date
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
REVISION = re.compile(rf"^Revision: ({VERSION}) · Updated: (\d{{4}}-\d{{2}}-\d{{2}})$")
# Generated output, private harness context (including sandbox masks) and Agentic Systems' private
# task records are not Agentic Systems sources.
SKIPPED_DIRS = {".git", "dist", ".venv", ".claude", ".agentic-system-task", ".factory-task"}


def markdown_sources(root):
    def fail(error):
        raise error

    for folder, dirs, files in os.walk(root, onerror=fail):
        dirs[:] = [name for name in dirs if name not in SKIPPED_DIRS]
        yield from (Path(folder) / name for name in files if name.endswith(".md"))


def valid_revision(version, updated, package_version):
    if not re.fullmatch(VERSION, version) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", updated):
        return False
    try:
        date.fromisoformat(updated)
    except ValueError:
        return False
    return tuple(map(int, version.split("."))) <= tuple(map(int, package_version.split(".")))


def check(root=ROOT):
    root = Path(root).resolve()
    errors = []
    version_path = root / "VERSION"
    package_version = version_path.read_text().strip() if version_path.is_file() else ""
    if not re.fullmatch(VERSION, package_version):
        errors.append("VERSION: expected a numeric X.Y.Z release")
        package_version = "0.0.0"
    skills = [p for group in ("foundation", "entry", "evaluation", "defence")
              for p in (root / group).glob("*/SKILL.md")]
    if not skills:
        errors.append("No skills found")
    names = set()
    for path in skills:
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not lines or lines[0] != "---" or "---" not in lines[1:]:
            errors.append(f"{path.relative_to(root)}: missing frontmatter")
            continue
        end = lines.index("---", 1)
        fields = {}
        metadata = {}
        in_metadata = False
        # This is the package's constrained format, not a general YAML parser.
        for line in lines[1:end]:
            if line == "metadata:" and not in_metadata:
                in_metadata = True
                continue
            if in_metadata:
                match = re.fullmatch(r'  (version|updated): ("[^"\\]*")', line)
                if not match or match[1] in metadata:
                    errors.append(f"{path.relative_to(root)}: invalid/duplicate revision metadata")
                    continue
                try:
                    metadata[match[1]] = json.loads(match[2])
                except json.JSONDecodeError:
                    errors.append(f"{path.relative_to(root)}: invalid revision string")
                continue
            key, separator, value = line.partition(": ")
            if not separator or key not in {"name", "description", "license"} or key in fields:
                errors.append(f"{path.relative_to(root)}: unsupported/duplicate metadata")
                continue
            if not value or ": " in value or " #" in value or value[0] in "[{&*!|>'\"%@`":
                errors.append(f"{path.relative_to(root)}: use a plain one-line scalar")
            fields[key] = value
        name = fields.get("name", "")
        if (name != path.parent.name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
                or len(name) > 64 or name in names):
            errors.append(f"{path.relative_to(root)}: invalid/duplicate name")
        names.add(name)
        if not 1 <= len(fields.get("description", "")) <= 1024 or fields.get("license") != "MIT":
            errors.append(f"{path.relative_to(root)}: description/license invalid")
        if not valid_revision(metadata.get("version", ""), metadata.get("updated", ""), package_version):
            errors.append(f"{path.relative_to(root)}: invalid/missing revision or edit date")
    for path in markdown_sources(root):
        source = path.read_text(encoding="utf-8")
        if path not in skills and ".github" not in path.relative_to(root).parts:
            matches = [m for line in source.splitlines()[:6] if (m := REVISION.fullmatch(line))]
            if len(matches) != 1 or not valid_revision(matches[0][1], matches[0][2], package_version):
                errors.append(f"{path.relative_to(root)}: invalid/missing top revision or edit date")
        text = re.sub(r"```.*?```", "", source, flags=re.S)
        text = re.sub(r"(?ms)^~~~.*?^~~~[^\n]*", "", text)
        # Inline code spans (single or multi-backtick) are not link targets.
        text = re.sub(r"(`+)(.*?)\1", "", text)
        skill_root = next((p.parent for p in skills if path.is_relative_to(p.parent)), None)
        for raw in re.findall(r"\]\(([^)]+)\)", text):
            # A CommonMark title, if present, follows the destination after a
            # space and must not become part of the target path.
            destination = raw.split()[0] if raw.split() else raw
            url = urlsplit(destination)
            if url.scheme or not url.path:
                continue
            target = (path.parent / unquote(url.path)).resolve()
            if not target.exists():
                errors.append(f"{path.relative_to(root)}: broken link {raw}")
            if skill_root and not target.is_relative_to(skill_root.resolve()):
                errors.append(f"{path.relative_to(root)}: skill link escapes its staged folder: {raw}")
    return errors, len(skills)


if __name__ == "__main__":
    errors, count = check()
    for error in errors:
        print(error, file=sys.stderr)
    print(f"{count} skills checked; {len(errors)} errors")
    sys.exit(bool(errors))
