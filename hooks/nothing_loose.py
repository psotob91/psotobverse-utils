#!/usr/bin/env python3
"""PreToolUse hook: keep file writes inside the project's allowed structure.

Reads the JSON tool event from stdin. For Write/Edit/MultiEdit it resolves the
target path and checks it against the per-project write allowlist at
    $CLAUDE_PROJECT_DIR/.claude/policy/paths.allow.json
If the target is outside every allowed glob (or outside the project root), the
write is DENIED via permissionDecision=deny.

FAIL-OPEN by design: if CLAUDE_PROJECT_DIR is unset/unresolvable, the allowlist
is missing or unreadable, or anything unexpected happens, the hook ALLOWS (exit
0). This is mandatory: the plugin is installed machine-global in Cowork, so a
fail-closed default would block every unrelated project that has no allowlist.

Stdlib only. See docs/adr/0002 in the template for the verification spike.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _allow(reason: str = "") -> None:
    if reason:
        print(reason, file=sys.stderr)
    sys.exit(0)


def _deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def _target_path(tool_input: dict) -> str | None:
    for key in ("file_path", "path", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _matches(rel_posix: str, pattern: str) -> bool:
    """Allowlist entries are directory prefixes, optionally ending in /** or /*."""
    p = pattern.rstrip("/")
    for suffix in ("/**", "/*"):
        if p.endswith(suffix):
            p = p[: -len(suffix)]
            break
    p = p.strip("/")
    if not p:
        return True
    return rel_posix == p or rel_posix.startswith(p + "/")


def main() -> None:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        _allow("nothing_loose: could not parse stdin; failing open")

    if event.get("tool_name", "") not in ("Write", "Edit", "MultiEdit"):
        _allow()

    target = _target_path(event.get("tool_input", {}) or {})
    if not target:
        _allow()

    project = os.environ.get("CLAUDE_PROJECT_DIR")
    if not project:
        _allow("nothing_loose: CLAUDE_PROJECT_DIR unset; failing open")

    project_root = Path(project)
    allow_file = project_root / ".claude" / "policy" / "paths.allow.json"
    if not allow_file.is_file():
        _allow("nothing_loose: no per-project allowlist; failing open")

    try:
        policy = json.loads(allow_file.read_text(encoding="utf-8"))
        allow = policy.get("allow_write", [])
    except Exception:
        _allow("nothing_loose: allowlist unreadable; failing open")

    try:
        tgt = Path(target)
        if not tgt.is_absolute():
            tgt = project_root / tgt
        rel_posix = tgt.resolve().relative_to(project_root.resolve()).as_posix()
    except Exception:
        _deny(
            f"Write to '{target}' is outside the project root. Keep work inside the "
            "allowed structure (see .claude/policy/paths.allow.json) or use /tidy."
        )

    for pattern in allow:
        if _matches(rel_posix, pattern):
            _allow()

    _deny(
        f"Path '{rel_posix}' is outside the allowed write paths {allow}. "
        "Use /tidy to propose a correct location, or add the path to "
        ".claude/policy/paths.allow.json."
    )


if __name__ == "__main__":
    main()
