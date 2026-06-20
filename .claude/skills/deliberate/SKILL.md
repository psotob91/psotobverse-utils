---
name: deliberate
description: >-
  Deliberate engineering principles for SUBSTANTIAL tasks (architecture, broad refactors, system
  design, hard debugging, changes touching many files or invariants). Consult this skill when a task
  is complex or high-impact and it pays to think before coding, not on trivial or mechanical changes.
  Fires on "design", "refactor deeply", "architecture", "this is delicate", "how do I tackle this weird
  bug", or when a plan has several risky steps. Applies 4 principles (think before coding, simplicity,
  surgical changes, objectives with verification). On simple, direct tasks do NOT use it: it would be
  overhead.
---

# /deliberate — deliberate engineering (only when it's worth it)

A light adaptation of Forrest Chang / Karpathy principles. Claude already embodies part of this; the
value here is to **reinforce it on high-impact tasks**, not recite it on everything. If the task is
trivial, ignore this skill.

## The 4 principles
1. **Think before coding.** Before writing, understand the problem and the existing code: which files
   you touch, what invariants exist, what could break. For large tasks, use plan mode. An hour of
   reading saves a day of undoing.
2. **Simplicity first.** The simplest solution that works wins. Don't add abstraction, configuration,
   or generality "just in case". Delete before adding. Code that doesn't exist has no bugs.
3. **Surgical changes.** Touch the minimum necessary. One change = one intent. Don't mix refactor with
   feature with formatting in the same commit. The smaller the diff, the easier to review and revert.
4. **Declarative objectives with verification.** Turn the instruction into an objective with an
   objective test of "done": "the importer parses a malformed file without crashing and returns a
   valid record", not "fix the parser". Define how you'll know it worked BEFORE starting, and verify
   it at the end (ties into the robust core `.claude/skills/_shared/robust-cycle.md`).

## How to apply it
- It's not a ceremonial checklist: use the principle the task needs. A weird bug calls for (1) and (4);
  a refactor calls for (2) and (3).
- Explain the **why** of your design decisions in the code/commit, not just the what.
- If you catch yourself adding complexity for a case nobody asked for, return to principle 2.

## When NOT to use it
One-line changes, mechanical edits, renames, typo fixes, single-obvious-step tasks. Forcing
deliberation there only wastes time and tokens. This skill is about the engineering judgement for
*how* to make a hard change; to track *progress toward* a multi-step objective use `/goal`, and for
an after-the-fact audit of work already done use `/reconcile`.
