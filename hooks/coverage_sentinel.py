"""UserPromptSubmit hook: recall sentinel — nudge toward /coverage on a substantive task.

OPT-IN: no-op unless the project ships a policy catalog (`.claude/policies/00-index.md`).
NUDGE ONLY: it never spawns agents and never blocks — it injects a one-time, per-session
reminder (additionalContext) suggesting `/coverage` (or `/comprehend`, which runs it) so a
relevant policy off the obvious routing path is not silently missed. Fires at most once per
session (tracked in .claude/state/coverage_sentinel.json). Stdlib only; FAILS OPEN.
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_util as u  # noqa: E402

CATALOG = (".claude", "policies", "00-index.md")
MARKER = (".claude", "state", "coverage_sentinel.json")

# A prompt looks "substantive" if it is long enough or names design/build/analysis work.
# Domain-neutral on purpose (orthogonality): no project- or field-specific vocabulary —
# the catalog opt-in already scopes the hook; this is just a coarse substantive-ness gate.
SUBSTANTIVE = re.compile(
    r"\b(analy[sz]e|model|estimate|measure|design|implement|build|refactor|"
    r"pipeline|integrat|validate|verify|audit|review|migrat|onboard|"
    r"investigat|architect|plan)\w*", re.I,
)


def _emit(text: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": text,
        }
    }))


def main() -> int:
    # Opt-in: only where a policy catalog exists.
    if not os.path.isfile(u.p(*CATALOG)):
        return 0

    event = u.read_stdin_json()
    prompt = (event.get("prompt") or "").strip()
    if not prompt:
        return 0

    # Substantive heuristic: long prompt OR an analysis/build verb.
    if len(prompt) < 120 and not SUBSTANTIVE.search(prompt):
        return 0

    session = str(event.get("session_id") or event.get("session") or "")

    # Once per session: skip if we already nudged this session.
    marker_path = u.p(*MARKER)
    try:
        with open(marker_path, encoding="utf-8") as f:
            if json.load(f).get("session") == session and session:
                return 0
    except (OSError, ValueError):
        pass

    try:
        os.makedirs(os.path.dirname(marker_path), exist_ok=True)
        tmp = marker_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"session": session, "at": u.now_iso()}, f)
        os.replace(tmp, marker_path)
    except OSError:
        pass  # nudging is best-effort; never block

    _emit(
        "Recall sentinel: this looks like a substantive task. Before committing to a "
        "plan, consider running /coverage (or /comprehend, which includes it) to confirm "
        "no relevant policy sits off the obvious routing path. Routing is additive — you "
        "may consult any policy in .claude/policies/00-index.md regardless of what fired."
    )
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # fail open
        sys.exit(0)
