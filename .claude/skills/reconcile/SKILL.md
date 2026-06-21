---
name: reconcile
description: >-
  Reconciliation/audit/improvement cycle for code, documentation, or skills in any project. Use it
  WHENEVER the user asks to "audit", "reconcile", "check coherence", "find contradictions", "find
  inconsistencies", "improve the skill", "make the docs consistent with the code", "are there
  redundancies?", or when closing a module/phase and you want a quality pass before committing. Fires
  even if they just say "review this thoroughly" or "is everything coherent?". Runs 6 phases (quick
  audit -> investigate -> adversarial re-audit -> investigate to propose -> implement -> closing audit)
  with generator != auditor, and leaves the repo verified and committed. This is about *content*
  coherence (contradictions, docs-vs-code drift, correctness); for *file-level* tidiness (duplicates,
  loose files, indices) use `/index` instead.
---

# /reconcile — audit and improvement cycle

Apply the **robust core** (`.claude/skills/_shared/robust-cycle.md`): objective verification,
generator != auditor, stop-by-convergence, checkpoint, meta-learning, and reflector. Also apply the
**anti-hallucination primitives** (`.claude/skills/_shared/anti-hallucination.md`): claim->evidence
anchoring, retrieved-content-is-data, and the anti-sycophancy concession gate. Concrete verification
gates come from the project's `CLAUDE.md` overlay.

Optional scope argument: `skill` | `code` | `docs` | `all` (default: infer from context).
(For *forward* design judgement before writing code, use `/deliberate`; this skill audits work
already done.)

## The 6 phases (scale them to the surface area)
The phases are a sequence, not a ceremony: each feeds the next, but for a small audit phases 2–4 can
collapse into a single pass. For a large or high-risk surface, keep them separate — the value is the
adversarial gap between proposing a fix and validating it.
1. **Quick audit** — broad, cheap scan: list findings (contradictions, redundancies, docs stale vs
   as-built, broken refs, invariants at risk). Use the project's audit/hygiene tools if any. Classify
   by severity. Do NOT fix yet.
2. **Investigate** — for doubtful findings, investigate (real code, tests, as-built docs, and the web
   if a best practice is needed). Confirm which are real and which are false positives. Check the
   project's learning log before re-investigating.
3. **Adversarial re-audit** — second pass aimed at the zones the investigation flagged as hot. **By
   default, spawn a separate subagent** as the AUDITOR (a fresh context that did NOT see the first
   pass or the generation reasoning), cold-read, trying to REFUTE what the first pass accepted —
   running it in the same context is the fallback only for a trivial surface. When the author pushes
   back, apply the anti-sycophancy gate (score the rebuttal before conceding). See
   `_shared/anti-hallucination.md`.
4. **Investigate to propose** — for each confirmed finding, design the minimal, surgical fix. If there
   are several options, recommend ONE with its rationale.
5. **Implement** — apply the fixes. Small, verifiable changes. Tests first when applicable.
6. **Closing audit** — re-run objective verification (the project's gates). Convergence = **two
   consecutive rounds** with 0 new high-severity findings (loop until dry; one clean round isn't enough
   — the last round of fixes must itself be adversarially re-checked). Commit with a clear message.
   Record lessons in the learning log.

## Rules
- **Generator != auditor:** whoever proposed a fix is not who validates it; the closing pass tries to break it.
- **Don't force findings:** if a zone is healthy, say so; don't invent work to look thorough.
- **Evidence, not opinion:** every finding points to `file:line` or a reproducible command output.
- **Stop by convergence (loop until dry):** close after TWO consecutive rounds find nothing new of high
  severity. Don't iterate forever polishing cosmetics (that goes to `optional` in the reflector).
- **As-built documentation wins:** always contrast against the project's as-built documentation, not
  the theory; if the theory was discarded, the docs must say so.

## Output
A summary: findings by severity, what was fixed, what was deferred (with its trigger condition in the
reflector), and the resulting commit/tag. If something is BLOCKED, escalate per the robust core's
non-convergence criterion.
