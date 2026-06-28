"""PreToolUse hook: the one routing write-gate (asks, never denies).

OPT-IN: no-op unless the project ships `.claude/policy/routing.yml`. For a Write/Edit
whose target path matches a rule with `mode: block` and a `requires_first` list, if no
required sibling artifact (e.g. an ASCII timeline / decision diagram for a phenotype)
exists next to the target, emit permissionDecision=ask so the human can confirm. This
is the ONLY place routing can interrupt, it applies ONLY to writes (never to reading a
policy), and it ASKS rather than denies (Invariant 0). Stdlib only; FAILS OPEN.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import routing_util as ru  # noqa: E402


def _target(tool_input: dict):
    for k in ("file_path", "path", "notebook_path"):
        v = tool_input.get(k)
        if isinstance(v, str) and v:
            return v
    return None


def main() -> int:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw and raw.strip() else {}
    except Exception:
        return 0
    if event.get("tool_name") not in ("Write", "Edit", "MultiEdit"):
        return 0
    target = _target(event.get("tool_input", {}) or {})
    if not target:
        return 0

    rules = ru.load_rules()
    if not rules:
        return 0

    for r in rules:
        if r.get("mode") != "block" or not r.get("path_glob"):
            continue
        if not ru.match_path(r, target):
            continue
        if ru.sibling_satisfied(r, target):
            return 0  # artifact present -> allow
        req = ", ".join(r.get("requires_first", [])) or "a comprehension artifact"
        byp = r.get("bypass_if") or ""
        reason = (
            f"Comprehension gate: before writing '{os.path.basename(target)}', a "
            f"required artifact ({req}) should exist alongside it — e.g. the ASCII "
            f"timeline / decision diagram that proves the rule is understood (see "
            f"{r.get('next_policy','the relevant policy')}). "
            + (f"Bypass if {byp}. " if byp else "")
            + "Create the diagram first, or confirm you want to proceed."
        )
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": reason,
            }
        }))
        return 0
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # fail open
        sys.exit(0)
