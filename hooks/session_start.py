"""SessionStart hook (meta-learner): orient fast + detect unclean exit (crash).

OPT-IN: no-op unless the project ships `.claude/meta-learner.json`. When active,
injects a concise additionalContext (rolling SESSION_STATE.md + last-handoff
pointer) so a new session resumes cheaply, and arms a dirty-bit. SessionEnd flips
it to clean_exit; an `active` bit at the next start ⇒ the previous session ended
uncleanly (crash / killed terminal). Fails open (exit 0) on any error.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_util as u  # noqa: E402


def main() -> int:
    cfg = u.load_config()
    if cfg is None:
        return 0  # project not opted in

    inp = u.read_stdin_json()
    sid = inp.get("session_id", "")
    source = inp.get("source", "")

    prev = u.read_state()
    crashed = prev.get("status") == "active"

    parts = [f"[meta-learner] {u.project_label(cfg)} · branch {u.branch()}"]
    if crashed:
        parts.append(
            "WARNING: the previous session did not close cleanly (possible crash "
            f"or hard exit; last active {prev.get('last_turn_at', '?')}). "
            "Reconcile SESSION_STATE.md against `git status` before trusting it — "
            "the last in-flight turn may not have persisted."
        )
        last = prev.get("last_handoff")
        if last:
            parts.append(f"Last good handoff: {last}")

    state_md = u.read_head(u.p(*u.SESSION_STATE_MD), 30)
    if state_md:
        parts.append("Current SESSION_STATE.md:\n" + state_md)

    nsig = u.queue_count()
    if nsig:
        parts.append(f"{nsig} unprocessed learning signal(s) queued — run /psotobverse-utils:reflect to triage them.")

    u.write_state({
        "status": "active",
        "branch": u.branch(),
        "started_at": u.now_iso(),
        "last_turn_at": u.now_iso(),
        "session_id": sid,
        "source": source,
        "last_handoff": prev.get("last_handoff", ""),
    })

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": "\n\n".join(parts),
        }
    }))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # fail open
        sys.exit(0)
