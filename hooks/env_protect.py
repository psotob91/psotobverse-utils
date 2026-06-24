#!/usr/bin/env python3
"""PreToolUse hook: deny access to secret files regardless of tool or project.

Reads the JSON tool event from stdin. If the target path's basename looks like a
secret (.env, .env.<anything> except .env.example, *.pem, *.key, id_*), the call
is DENIED. Otherwise it allows.

Globally safe: this does NOT depend on CLAUDE_PROJECT_DIR, so it is correct to run
machine-wide in Cowork — you never want an agent reading or writing real secrets,
in any project. Stdlib only.
"""
from __future__ import annotations

import fnmatch
import json
import sys
from pathlib import Path

SECRET_GLOBS = ("*.pem", "*.key", "id_rsa", "id_ed25519", "id_*")


def _deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def _is_secret(name: str) -> bool:
    if name == ".env":
        return True
    if name.startswith(".env.") and name != ".env.example":
        return True
    return any(fnmatch.fnmatch(name, glob) for glob in SECRET_GLOBS)


def main() -> None:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)  # fail open on parse error

    tool_input = event.get("tool_input", {}) or {}
    target = None
    for key in ("file_path", "path", "notebook_path"):
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            target = value
            break
    if not target:
        sys.exit(0)

    if _is_secret(Path(target).name):
        _deny(
            f"Access to secret file '{Path(target).name}' is blocked by policy. "
            "Document required keys in .env.example; never read or write real secrets."
        )
    sys.exit(0)


if __name__ == "__main__":
    main()
