# Shared robust core (robust-cycle)

> Common reference read by the `/index`, `/reconcile`, `/goal` and `/deliberate` skills.
> It is NOT a skill itself (no frontmatter, never auto-invoked). It defines the **primitives**
> that make any work cycle verifiable, self-healing, and resistant to stalling or bloating.
> When a skill says "apply the robust core", it means this.
>
> **Project specialization:** the concrete verification gates (test runner, linter, doc auditor,
> hygiene tool, learning log) are project-specific. Each project declares them in its `CLAUDE.md`
> (look for a "Skill specialization" / overlay section). The patterns below are invariant; the
> exact commands are whatever that project defines.

## (a) Objective verification (the model does not decide the truth)
Before declaring a step "done", pass whatever gates the repo defines (see the project's `CLAUDE.md`
overlay). Typical gates:
- **Tests** — the project's test suite, green (or document why a skip is legitimate).
- **Linter** — the project's linter, clean.
- **Doc audit** — if the project has a docs auditor, 0 invalid `file:line` references.
- **Doc hygiene** — if the project has a hygiene tool, no size/format/ref alerts on touched `.md`.
- If the change has an associated benchmark, run it and compare against the baseline.

**Generator != auditor, in a SEPARATE context.** One role writes the code; the verification is a
distinct step run in a *fresh* context — ideally a different subagent that did NOT see the generation
reasoning — and it tries to REFUTE, not confirm. Why separate context: a model asked to review its own
work in the same conversation rationalizes its choices ("the student grading their own exam"); isolating
the auditor from the generator's context is what makes the refutation real, not theatre. This is a
well-supported primitive (Chain-of-Verification, Dhuliawala et al. 2023, arXiv:2309.11495); it is a
pattern several agent systems converge on — anchor that observation to the project's competitive
analysis before asserting it as fact.

**Cold-read.** The auditor evaluates the artifact *fresh*, without the history of previous review
rounds. Carrying round history anchors the reviewer ("we already agreed this was fine"); a cold read
catches what accumulated context hides. Score each round independently, then combine.

**Claim -> evidence.** Every claim the auditor or generator makes must be anchored to `file:line` or a
reproducible command output — never opinion. The full anchoring discipline lives in `anti-hallucination.md`
(primitive 1); apply it here.

## (b) Meta-learning (what did we learn, is it reusable?)
When closing a block, ask: "what did I learn that wasn't obvious?". If it is reusable, write it to the
project's learning log (e.g. a `learning/` directory: a lesson log and an operable playbook). Before
re-investigating something, check those first. Do not duplicate what is already recorded.

## (c) Auto-reflector (triage, to avoid infinite improvement)
Every candidate improvement is classified (e.g. in `learning/REFLECTOR.md`) as:
- **now** — high value, low risk, unblocks other things -> do it now.
- **defer** — worth it, but depends on a condition (resource, another phase) -> note the **trigger condition**.
- **optional** — nice-to-have; only if budget is left over.
- **discard** — not worth the cost; note WHY (prevents re-proposing it every round).
The reflector and the backlog **feed each other**: the reflector triages backlog items; backlog
results (what worked, what didn't) feed the reflector.

## (d) TWO stopping criteria (distinct, do not conflate)
1. **CONVERGENCE ("good enough") — loop until DRY:** tests green + stable benchmark + **two
   consecutive rounds** each finding 0 NEW high-severity issues. One clean round is not enough: the
   first clean round often just means the previous round's fixes haven't been adversarially re-checked
   yet. Require a *second* clean round (ideally cold-read by a separate auditor) so a fix that silently
   introduced a new issue still gets caught before you close. This is the normal success: stop and close.
2. **NON-CONVERGENCE ("can't right now"):** a goal is not reachable. Before giving up (anti-premature
   abandonment: agents tend to give up too early), exhaust:
   - a **budget cap** (tokens/iterations) large but bounded,
   - several distinct **re-approaches** (not the same attempt repeated),
   - a **diagnosis that CONFIRMS** the real blocker (needs an external resource: GPU/driver, credential, network, a paywalled resource).
   Only then mark the goal **BLOCKED**, record the trigger condition, and **continue with the other
   goals** (multi-goal: don't get stuck on one). Block the WHOLE run only when everything reachable is
   done and the blocked part is confirmed -> **escalate to the user** (graceful degradation).

## (e) Self-healing + rollback
If a flow or a benchmark fails: first a bounded **fix-loop** (diagnose root cause, fix, re-verify).
If 3 attempts don't fix it, **re-approach** (different strategy) or **roll back** to the last sane
tag/checkpoint and record the lesson. Never leave the repo broken between blocks.

## (f) Checkpoint-commit (protect progress)
Commit when **starting a plan's execution** and at **each milestone** (not on every change: that's
noise). Clear message with what was done and the verification that passed. Use tags (`pre-*`, `*-done`)
as a rollback net before large changes. This guarantees a failure never costs more than one block.

## (g) Plan and backlog hygiene (don't bloat, split when needed)
- The **plan** = strategy/goals (stable; edited only at re-plan checkpoints). If it grows past the
  limit and compressing would lose info -> **split the detail into a referenced `.md`** (progressive
  disclosure), never truncate.
- The **backlog** = tactical state (volatile). COMPLETED items move to a history (RUNLOG) so it doesn't
  grow. If the backlog MUST be large, split and index it like any doc.
- Both pass through the project's hygiene gate.

## Operable summary (the cycle in one line)
implement -> **verify (a)** -> **checkpoint (f)** -> **meta-learn (b)** + **reflect (c)** ->
review/update the plan or backlog (g) -> next; stop by **convergence or non-convergence (d)**;
on failure, **self-heal or roll back (e)**.
