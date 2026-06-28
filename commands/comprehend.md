---
description: Before planning or doing anything, explain back — in your own words — what you understood the request to be, then STOP. Use it to catch hallucination or drift early on anything non-trivial, ambiguous, or high-stakes ("explain what you understood", "restate the request", "take an exam first", "what do you think I'm asking"). Produces goal, explicit + hidden assumptions, success criteria, ambiguities, clarifying questions, scope/data limits, and what you will NOT assume; runs a /coverage sweep; renders diagrams when the task is about rules or timelines. Does NOT plan or execute.
---

# /comprehend — restate understanding before acting

You have been invoked **deliberately** as a comprehension gate. The user wants to
confirm you actually understand the request — and that you have not hallucinated or
drifted — BEFORE any planning or execution. Produce the sections below, in order,
then **STOP**. Do not design, plan, or change anything.

The request to comprehend: `$ARGUMENTS`
(If empty, comprehend the user's most recent substantive request in this session.)

## Produce, in order

1. **Restate the goal** — in your own words: the objective, who it is for, and why it
   matters. Not a paraphrase of the wording — your understanding of the intent.
2. **Explicit assumptions** — what the request states or clearly implies as given.
3. **Hidden assumptions** — what it presupposes but does not say; what you would be
   silently assuming if you just started. Flag each as an assumption, not a fact.
4. **Success criteria & passing gates** — what "done" looks like, stated so it could
   be checked: the observable outcomes and the gates that must pass (tests, render,
   review, the user's sign-off).
5. **Ambiguities & edge cases** — where the request is under-specified, could be read
   more than one way, or has boundary cases that change the approach.
6. **Clarifying questions** — the few questions whose answers would most change what
   you do. Ask only what genuinely matters; do not pad.
7. **Scope & data limits** — what is in and out of scope; what data/access/tools you
   have and what you do not; anything you are not permitted to touch.
8. **What you will NOT assume** — explicit non-assumptions, to prevent silent scope
   creep (e.g. "I will not assume the data is already cleaned / that I may push").

## Coverage sweep (recall)

Run `/coverage` on this request (or apply its method inline): fan out decorrelated
reviewers over the policy catalog and report the Tier-1 (must-consult) and Tier-2
(consider) policies, plus what was deliberately excluded — so a relevant policy off
the obvious routing path is not silently missed. Fold the result into your answer.

## Diagrams (when rules or time logic are involved)

If the task concerns decision rules, eligibility/timeline logic, or a phenotype/
indicator, render the relevant picture as part of comprehension — BEFORE any code:
- decision logic → an ASCII decision diagram (or a mermaid flowchart);
- time logic (windows, washout, episodes) → an ASCII timeline.
A rule you cannot draw is a rule you do not yet understand. Show the drawing and ask
the user to confirm it matches their intent.

## Hard stop

After presenting the above, **stop and wait**. Do not produce a plan, write code, or
take any action. Silence is not consent — only an explicit go-ahead (or a `/deliberate`
or planning request) moves past this gate.
