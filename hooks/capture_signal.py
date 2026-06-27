"""UserPromptSubmit hook (meta-learner): cheap, crash-safe signal capture.

OPT-IN: no-op unless the project ships `.claude/meta-learner.json`. The domain
patterns (what counts as a "consensus" signal) come from that config, so the same
generic hook serves an agent-building repo and a biostatistics repo. Appends one
JSONL line to learning/queue/signals.jsonl when a prompt looks like a CORRECTION
or a domain CONSENSUS signal. Append-only, no network, sub-second, never blocks.
The judgement-heavy synthesis is deferred to the human-gated /reflect skill.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import meta_util as u  # noqa: E402


def _compile(patterns):
    try:
        return re.compile("|".join(f"(?:{x})" for x in patterns), re.I)
    except re.error:
        return None


def main() -> int:
    cfg = u.load_config()
    if cfg is None:
        return 0

    inp = u.read_stdin_json()
    prompt = (inp.get("prompt") or "").strip()
    if not prompt:
        return 0

    correction = _compile(cfg.get("correction_patterns") or u.DEFAULT_CORRECTION)
    consensus = _compile(cfg.get("consensus_patterns") or u.DEFAULT_CONSENSUS)

    kinds = []
    if correction and correction.search(prompt):
        kinds.append("correction")
    if consensus and consensus.search(prompt):
        kinds.append("consensus")
    if not kinds:
        return 0

    path = u.p(*u.QUEUE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    line = json.dumps({
        "ts": u.now_iso(),
        "branch": u.branch(),
        "kinds": kinds,
        "snippet": prompt[:300],
    }, ensure_ascii=False)
    with open(path, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    st = u.read_state()
    if st:
        st["last_turn_at"] = u.now_iso()
        u.write_state(st)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # fail open
        sys.exit(0)
