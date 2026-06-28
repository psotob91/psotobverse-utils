"""UserPromptSubmit hook: additive policy routing.

OPT-IN: no-op unless the project ships `.claude/policy/routing.yml`. When a prompt
matches a rule's `signal.prompt` keywords, inject a NON-BLOCKING reminder
(additionalContext) pointing to the next policy and its bypass condition. This is
ADDITIVE ONLY (Invariant 0): it never hides a policy and never blocks — it only
suggests. The one write-gate lives in comprehension_gate.py. Stdlib only; FAILS OPEN.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import routing_util as ru  # noqa: E402


def main() -> int:
    try:
        raw = sys.stdin.read()
        event = json.loads(raw) if raw and raw.strip() else {}
    except Exception:
        return 0
    prompt = (event.get("prompt") or "").strip()
    if not prompt:
        return 0

    rules = ru.load_rules()
    if not rules:
        return 0

    hits = []
    for r in rules:
        if r.get("prompt") and ru.match_prompt(r, prompt):
            nxt = r.get("next_policy") or "(unspecified)"
            byp = r.get("bypass_if") or ""
            line = f"- {nxt}" + (f"  — bypass if {byp}" if byp else "")
            hits.append(line)
    if not hits:
        return 0

    # de-dup, keep order
    seen, ordered = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h); ordered.append(h)

    msg = (
        "Policy routing (additive — suggestions, not gates; consult any policy you "
        "need regardless):\n" + "\n".join(ordered) +
        "\nThe full hub is .claude/policies/00-index.md; run /coverage if unsure."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": msg,
        }
    }))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # fail open
        sys.exit(0)
