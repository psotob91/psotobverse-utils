---
name: deliberate
description: >-
  Deliberate on the APPROACH before a substantial or risky change — design before coding. Use it for
  architecture, broad refactors, system design, hard debugging, or changes touching many files or
  invariants, where it pays to think first. Fires on "design this", "how should I approach", "refactor
  deeply", "architecture", "this is delicate", "how do I tackle this weird bug", or when a plan has
  several risky steps. It makes you pause and apply the engineering principles before writing code. On
  trivial or mechanical changes do NOT use it: it would be overhead.
---

# /deliberate — design the approach before a hard change

A thin verb: before a substantial/risky change, **stop and design the approach** instead of coding into
the unknown. It doesn't carry its own theory — it *applies* the shared principles
(`.claude/skills/_shared/principles.md`) to this specific task. Claude already embodies part of this;
the value here is to **reinforce it on high-impact work**, not recite it on everything.

## What to do
For the change in front of you, deliberately apply (from `principles.md`):
- **#1 Minimalism** — the simplest solution that works; delete before adding; don't generalize "just in
  case". (This is the old "simplicity first".)
- **#2 Understand before changing** — map the problem, the files you'll touch, the invariants at risk,
  what could break. For a large task, design/plan first.
- **#3 Surgical changes** — find the minimal edit that does the job; one change = one intent.
- **#5 Verification first** — define the objective done-check *before* you start ("the importer parses a
  malformed file without crashing and returns a valid record", not "fix the parser"), and how you'll
  verify it at the end (ties into `robust-cycle.md`; anchor the evidence per `anti-hallucination.md`).

Scale it to the task: a weird bug leans on #2 and #5; a broad refactor leans on #1 and #3.
It's not a ceremonial checklist — use the principle the task needs, and explain the *why* of your design
choices in the code/commit, not just the what.

## When NOT to use it
One-line changes, mechanical edits, renames, typo fixes, single-obvious-step tasks — forcing
deliberation there only wastes time and tokens. This skill is the engineering judgement for *how* to
make a hard change; to track *progress toward* a multi-step objective use `/goal`, and for an
after-the-fact audit of work already done use `/reconcile`.
