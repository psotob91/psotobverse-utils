#!/usr/bin/env python3
"""Install the psotobverse-utils workflow skills into another project.

Usage:
    python install.py <target-project-dir> [--force]

Copies the generic workflow skills (_shared, goal, deliberate, reconcile, index) into
<target-project-dir>/.claude/skills/ so Claude Code can auto-invoke them there. By design the skills
are project-agnostic: the consuming project supplies the concrete verification gates (test runner,
linter, doc auditor, hygiene tool, learning log) via a "Skill specialization" overlay section in its
own CLAUDE.md.

Stdlib only (no venv). Does not overwrite an existing skill unless --force is given.
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILLS = ["_shared", "goal", "deliberate", "reconcile", "index"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Install psotobverse-utils workflow skills.")
    parser.add_argument("target", help="Path to the target project root.")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite skills that already exist in the target."
    )
    args = parser.parse_args()

    src_root = Path(__file__).resolve().parent / ".claude" / "skills"
    if not src_root.is_dir():
        print(f"ERROR: source skills not found at {src_root}", file=sys.stderr)
        return 2

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"ERROR: target project dir does not exist: {target}", file=sys.stderr)
        return 2

    dst_root = target / ".claude" / "skills"
    dst_root.mkdir(parents=True, exist_ok=True)

    installed, skipped = [], []
    for name in SKILLS:
        src = src_root / name
        dst = dst_root / name
        if dst.exists() and not args.force:
            skipped.append(name)
            continue
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        installed.append(name)

    print(f"Installed into {dst_root}:")
    for name in installed:
        print(f"  + {name}")
    if skipped:
        print("Skipped (already present; use --force to overwrite):")
        for name in skipped:
            print(f"  = {name}")

    print(
        "\nNEXT STEP: add a 'Skill specialization (overlay)' section to the target's CLAUDE.md\n"
        "mapping the generic gates (Tests / Linter / Doc audit / Doc hygiene / Outputs index /\n"
        "as-built docs / learning log) to this project's concrete commands and paths.\n"
        "See this repo's README.md for the contract."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
