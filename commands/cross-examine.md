---
description: Adversarial multi-agent review. Fan out independent skeptics to try to REFUTE a piece of work, a set of findings, a plan, or a claim, vote, and report only what survives. Use when correctness matters and you want more than one set of eyes ("cross-examine this", "adversarial review", "red-team these findings", "fan out reviewers", "is this actually right"). Reviewers run on Sonnet; synthesis is yours. Proposes, does not auto-fix.
---

# /cross-examine — adversarial review by a panel

You have been invoked deliberately to **stress-test** something by sending independent
skeptics at it. Reviewers try to *break* the work, not bless it. Aggregate by vote,
report only what survives, and **propose** — do not auto-apply fixes.

Target to cross-examine: `$ARGUMENTS`
(If empty, cross-examine the most recent substantial change / finding / plan in this
session — name explicitly what you chose.)

## 1. Frame

State concisely: what is being examined, and the **dimensions of risk** that matter for
it (e.g. correctness, methodology/stats validity, security, reproducibility, data
leakage, missed edge cases, clarity). Pick the 3–5 dimensions that fit this target.

## 2. Fan out independent reviewers (Sonnet)

Spawn **3–5 reviewers in parallel** (Task tool, model **sonnet** — cheap, independent
contexts catch what one misses). Give each a DISTINCT dimension/lens from step 1 and the
same instruction: *adversarial* — "try to find what is WRONG, missing, or unjustified;
for each issue give a concrete location + why it's a real problem + severity
(blocker/major/minor); default to skepticism but do not invent problems." For verifying
specific CLAIMS rather than reviewing work, instruct each reviewer to attempt to REFUTE
the claim and return refuted / holds / uncertain with reasoning.

Scale: a quick check → 3 reviewers; "thorough" / high-stakes → 5 + a second pass on the
hottest findings (a finding is only **confirmed** if it survives a majority of independent
looks; a claim only **holds** if a majority fail to refute it).

## 3. Aggregate by vote

- **Confirmed issues:** raised (or, for claims, left un-refuted) by a majority of
  reviewers. These are real.
- **Contested:** raised by a minority or disputed — list separately, do not drop silently.
- **Refuted / non-issues:** explicitly note what was checked and found fine (so the
  absence of an issue is evidence, not an omission).

## 4. Synthesize (you — Opus-grade)

Report: confirmed issues ranked by severity (with locations); contested items with the
disagreement; what was verified-clean; and your overall verdict (ship / fix-then-ship /
rework). Separate fact from inference. If reviewers largely agreed, say so; if they
diverged sharply, that itself is a signal of unclear or risky work.

## 5. Propose, don't apply

Present findings and a recommended fix order. Do not edit or commit anything — wait for
the user to choose what to act on (or to invoke `/deliberate` on a fix).
