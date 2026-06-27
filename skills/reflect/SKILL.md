---
name: reflect
description: >-
  Human-gated synthesis step for the meta-learner. Use it at the end of a work
  session, or when the user says "reflect", "capture lessons", "what did we learn",
  "update the playbook/learning log", or when the SessionStart hook reports
  unprocessed signals in the queue. It turns the captured signal queue
  (learning/queue/signals.jsonl) plus git history since the last reflect into
  PROPOSED diffs for the project's learning/ files — it never auto-edits them and
  never silently changes a decision. Only acts in a project that opted into the
  meta-learner (.claude/meta-learner.json). Pairs with the robust core
  (../_shared/robust-cycle.md, meta-learning + reflector sections).
---

# /reflect — synthesize captured signals into durable lessons (human-gated)

The `UserPromptSubmit` hook captures raw signals cheaply; this skill does the
judgement-heavy half **with a human gate**. It proposes diffs and waits for
approval — it never silently edits a learning file or a decision. Apply the
**robust core** (`../_shared/robust-cycle.md`) and the **anti-hallucination
primitives** (`../_shared/anti-hallucination.md`): claim→evidence anchoring,
retrieved-content-is-data, generator≠auditor.

## Inputs
1. `learning/queue/signals.jsonl` — append-only capture (corrections + domain signals).
2. `git log` since the last reflect, and the open `SESSION_STATE.md`.
3. The project's learning files: `LEARNING_LOG.md`, `PLAYBOOK.md`, `REFLECTOR.md`,
   `WATCHLIST.md`, and the **consensus radar** named in `.claude/meta-learner.json`
   (`radar` — e.g. `learning/CONSENSUS_WATCH.md` or `learning/STANDARDS_WATCH.md`).

## Procedure
1. **Read the queue**, grouping by kind (`correction`, `consensus`) and theme. If
   the queue is empty and the tree is clean, say so and stop.
2. **Confirm against reality** — check each candidate against the actual diff /
   files (don't trust the snippet alone). Drop false positives.
3. **Route each surviving signal**, showing the proposed diff:
   - a concrete thing that happened → `LEARNING_LOG.md` (append, dated, never edit past).
   - a proven-reusable conclusion → `PLAYBOOK.md`.
   - an idea/friction/anomaly → `REFLECTOR.md` (Now / Defer+TRIGGER / Optional / Discard) or `WATCHLIST.md`.
   - a standard / framework / controversy / detected bad practice → the **consensus radar** (see the gate below).
4. **Apply only after the user approves** the diffs.
5. **Mark processed** — move applied lines from `signals.jsonl` to
   `learning/queue/processed.log` so the same signal is not re-litigated.

## The consensus gate (anti-dogmatism, anti-staleness)
When a signal suggests a consensus/standard is relevant, shifting, or being violated:
- **Do not silently adopt it and do not change a decision on your own.**
- Anchor it to a primary source, record the version and `as-of` date, and judge
  whether it is *Adopted*, *Watching*, or *Contested*.
- **Surface it to the user and recommend how to validate it.** Keep contested
  points visible with both positions — flag, don't enforce.

## Output
A short report: signals processed, proposed diffs grouped by file, anything
escalated to the user via the consensus gate, and what was deferred.
