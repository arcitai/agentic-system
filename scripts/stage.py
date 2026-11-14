#!/usr/bin/env python3
"""Stage one reviewed skill bundle, or all of them as one flat set, into a fresh
directory; never install it."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUNDLES = ("foundation", "entry", "evaluation", "defence")
ALL = "all"


def source_info(source):
    """Use Git provenance only for this source root, never its enclosing repo."""
    try:
        result = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=source,
                                capture_output=True, text=True)
    except FileNotFoundError:
        if (source / ".git").exists():
            raise ValueError("Git is required to stage a Git checkout")
        return None, None, None
    if result.returncode or Path(result.stdout.strip()).resolve() != source.resolve():
        if (source / ".git").exists():
            raise ValueError("Cannot identify the source Git checkout")
        return None, None, None
    tracked = subprocess.run(["git", "ls-files", "-z", "--cached"], cwd=source,
                             capture_output=True, text=True, check=True)
    state = subprocess.run(["git", "status", "--porcelain"], cwd=source,
                           capture_output=True, text=True, check=True)
    head = subprocess.run(["git", "rev-parse", "--verify", "HEAD"], cwd=source,
                          capture_output=True, text=True)
    return set(tracked.stdout.split("\0")), head.stdout.strip() if not head.returncode else None, bool(state.stdout)


def stage(bundle, destination, source=ROOT):
    if bundle != ALL and bundle not in BUNDLES:
        raise ValueError("Select foundation, entry, evaluation, defence or all")
    destination = Path(destination)
    source = Path(source)
    tracked, revision, modified = source_info(source)
    if tracked is not None and not {"LICENSE", "VERSION"}.issubset(tracked):
        raise ValueError("LICENSE and VERSION must be tracked in the source checkout")
    skills = []
    for group in BUNDLES if bundle == ALL else (bundle,):
        found = sorted(p.parent for p in (source / group).glob("*/SKILL.md"))
        if tracked is not None:
            found = [p for p in found if (p / "SKILL.md").relative_to(source).as_posix() in tracked]
        if not found:
            raise ValueError(f"The {group} bundle has no skills")
        skills.extend(found)
    # A flat set must not let one group's skill silently replace another's.
    if len({skill.name for skill in skills}) != len(skills):
        raise ValueError("Skill names must be unique across the staged set")
    files = {}
    license_bytes = (source / "LICENSE").read_bytes()
    version = (source / "VERSION").read_text().strip()
    for skill in skills:
        if skill.is_symlink():
            raise ValueError("Skill sources must not be symlinks")
        for path in sorted(skill.rglob("*")):
            if tracked is not None and path.relative_to(source).as_posix() not in tracked:
                continue
            if path.is_symlink():
                raise ValueError("Skill resources must not be symlinks")
            if path.is_file():
                relative = Path("skills") / skill.name / path.relative_to(skill)
                files[relative.as_posix()] = path.read_bytes()
        files[f"skills/{skill.name}/LICENSE"] = license_bytes
    manifest = {
        "format": 1, "systemVersion": version, "bundle": bundle,
        "sourceRevision": revision, "sourceModified": modified,
        "files": {name: hashlib.sha256(data).hexdigest()
                  for name, data in sorted(files.items())},
    }
    # Exclusive creation refuses both existing directories and dangling symlinks.
    # A failed copy leaves an inspectable partial stage without a complete manifest.
    destination.mkdir(mode=0o700)
    for name, data in files.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (destination / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", choices=BUNDLES + (ALL,))
    parser.add_argument("--output", required=True, type=Path,
                        help="New directory under an existing parent")
    args = parser.parse_args()
    try:
        manifest = stage(args.bundle, args.output)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Stage failed: {error}\n")
    print(f"Staged {manifest['bundle']} {manifest['systemVersion']} at {args.output}")
    print("Inspect manifest.json and files before native adoption; nothing was installed.")


if __name__ == "__main__":
    main()
