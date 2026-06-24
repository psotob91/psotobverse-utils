#!/usr/bin/env python3
"""Install the psotobverse-utils workflow skills into another project (legacy vendor path).

NOTE: the PRIMARY install is now the Claude Code PLUGIN (this repo ships
.claude-plugin/plugin.json + hooks/hooks.json). Installing as a plugin also runs the hooks and
subagents in Cowork (settings.json hooks do not). Use this script only for a Code-only vendor copy
when you do not want to install the plugin.

Usage:
    python install.py <target-project-dir> [--force] [--with-hooks] [--no-overlay]
    python install.py <target-project-dir> --check        # verify parity, no writes

Copies the generic workflow skills (_shared, goal, deliberate, reconcile, index, tidy) into
<target-project-dir>/.claude/skills/ so Claude Code can auto-invoke them there. By design the skills
are project-agnostic: the consuming project supplies the concrete verification gates (test runner,
linter, doc auditor, hygiene tool, learning log) via a "Skill specialization" overlay section in its
own CLAUDE.md.

Always edit the CANONICAL copy in this repo first, then re-run with --force to sync. Use --check to
detect drift between a target's installed copies and this canonical source.

Stdlib only (no venv). Does not overwrite an existing skill unless --force is given.
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

SKILLS = ["_shared", "goal", "deliberate", "reconcile", "index", "tidy"]

OVERLAY_MARKERS = ("skill specialization", "especializacion de skills")

OVERLAY_TEMPLATE = """
<!-- ===== psotobverse-utils: Skill specialization (overlay) — FILL THIS IN ===== -->
## Skill specialization (project overlay)
The generic skills (`/goal`, `/reconcile`, `/index`, `/deliberate`) and `_shared/` talk about "the
project's gates" without naming them. Map them to THIS project's concrete commands/paths:

| Generic gate (in the skill) | This project's command/path |
|---|---|
| Tests         | <e.g. pytest -q> |
| Linter        | <e.g. ruff check .> |
| Doc audit     | <your doc auditor, if any> |
| Doc hygiene   | <your hygiene tool, if any> |
| Outputs index | <your outputs-index generator, if any> |
| As-built doc  | <path to your as-built documentation> |
| Learning log  | <e.g. learning/> |

A gate the project doesn't have is simply skipped by the skills. (Delete this comment once filled.)
<!-- ===== end overlay ===== -->
"""


def _find_claude_md(target: Path) -> Path | None:
    for candidate in (target / "CLAUDE.md", target / ".claude" / "CLAUDE.md"):
        if candidate.is_file():
            return candidate
    return None


def _diff_tree(src: Path, dst: Path) -> list[str]:
    """Return human-readable drift lines for src vs dst (empty = identical).

    Compares file CONTENT (filecmp.cmp shallow=False), not stat signatures — shutil.copy2 preserves
    mtime, so a shallow compare would miss same-size content edits, which is exactly the drift --check
    must catch.
    """
    if not dst.exists():
        return [f"MISSING in target: {dst.name}/"]
    src_files = {p.relative_to(src) for p in src.rglob("*") if p.is_file()}
    dst_files = {p.relative_to(dst) for p in dst.rglob("*") if p.is_file()}
    drift: list[str] = []
    for rel in sorted(src_files - dst_files):
        drift.append(f"missing in target: {dst.name}/{rel.as_posix()}")
    for rel in sorted(dst_files - src_files):
        drift.append(f"extra in target:   {dst.name}/{rel.as_posix()}")
    for rel in sorted(src_files & dst_files):
        if not filecmp.cmp(src / rel, dst / rel, shallow=False):
            drift.append(f"differs:           {dst.name}/{rel.as_posix()}")
    return drift


def check_parity(src_root: Path, dst_root: Path) -> int:
    """--check: report drift between canonical skills and the target's installed copies."""
    all_drift: list[str] = []
    for name in SKILLS:
        all_drift.extend(_diff_tree(src_root / name, dst_root / name))
    if not all_drift:
        print(f"[check] parity OK — {dst_root} matches the canonical source (no drift).")
        return 0
    print(f"[check] DRIFT detected between canonical source and {dst_root}:")
    for line in all_drift:
        print(f"  - {line}")
    print(
        "\nFix: edit the CANONICAL copy in this repo, then re-run install with --force.\n"
        "Note: --force replaces each skill folder wholesale (rmtree + copy), so any target-local files\n"
        "inside a skill folder are NOT preserved — keep project-specific content out of the skill dirs."
    )
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Install psotobverse-utils workflow skills.")
    parser.add_argument("target", help="Path to the target project root.")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite skills that already exist in the target."
    )
    parser.add_argument(
        "--with-hooks", action="store_true",
        help="Also copy hooks/ (doc_hygiene, stop_reminder) into the target.",
    )
    parser.add_argument(
        "--no-overlay", action="store_true",
        help="Do not scaffold the Skill-specialization overlay into the target's CLAUDE.md.",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="Verify the target's installed skills match this canonical source; write nothing. "
             "Exit non-zero on drift.",
    )
    args = parser.parse_args()

    src_root = Path(__file__).resolve().parent / "skills"
    if not src_root.is_dir():
        print(f"ERROR: source skills not found at {src_root}", file=sys.stderr)
        return 2

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"ERROR: target project dir does not exist: {target}", file=sys.stderr)
        return 2

    dst_root = target / ".claude" / "skills"

    if args.check:
        return check_parity(src_root, dst_root)

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

    if args.with_hooks:
        hooks_src = Path(__file__).resolve().parent / "hooks"
        hooks_dst = target / "hooks"
        hooks_dst.mkdir(parents=True, exist_ok=True)
        for f in ("doc_hygiene.py", "stop_reminder.py", "settings.snippet.json", "POLICIES.md"):
            src = hooks_src / f
            dst = hooks_dst / f
            if dst.exists() and not args.force:
                print(f"  = hooks/{f} (already present; use --force)")
                continue
            shutil.copy2(src, dst)
            print(f"  + hooks/{f}")
        print(
            "\nHOOKS: merge hooks/settings.snippet.json into the target's .claude/settings.json "
            "to activate doc_hygiene (PostToolUse) and stop_reminder (Stop)."
        )

    _handle_overlay(target, no_overlay=args.no_overlay)
    return 0


def _handle_overlay(target: Path, no_overlay: bool) -> None:
    """Scaffold the overlay template into the target's CLAUDE.md if it's missing."""
    if no_overlay:
        return
    claude_md = _find_claude_md(target)
    if claude_md is None:
        print(
            "\nOVERLAY: no CLAUDE.md found in the target. Create one with a 'Skill specialization "
            "(overlay)' section so the skills know this project's concrete gates (see README)."
        )
        return
    text = claude_md.read_text(encoding="utf-8", errors="replace")
    if any(m in text.lower() for m in OVERLAY_MARKERS):
        print(f"\nOVERLAY: {claude_md.name} already has a Skill-specialization section — left as is.")
        return
    with claude_md.open("a", encoding="utf-8") as fh:
        fh.write("\n" + OVERLAY_TEMPLATE)
    print(
        f"\nOVERLAY: appended a commented overlay template to {claude_md} — FILL IT IN with this "
        "project's gates (or pass --no-overlay to skip). Without it, the skills' 'run the project's "
        "gates' steps have nothing concrete to run."
    )


if __name__ == "__main__":
    raise SystemExit(main())
