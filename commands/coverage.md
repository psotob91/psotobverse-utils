---
description: Recall safety net. Given a task, find ALL relevant policies/docs — including ones OFF the obvious routing path — via a decorrelated multi-agent vote, so nothing relevant is missed. Use before a substantial task, or whenever you must be sure a key policy was not silently skipped. Fans out cheap reviewers, aggregates by union (recall) and votes (triage), and reports what was deliberately excluded and why. Does not execute the task.
---

# /coverage — make sure no relevant policy is missed

You have been invoked deliberately as a **recall safety net**. The deterministic
routing (policy index + `routing.yml`) is precise but can have **false negatives** —
a relevant policy that no predicate fired on. Your job is to catch those by an
ensemble that *deliberately escapes the route*. Aggregate for **recall**, not
precision. Then **stop** — do not execute the task.

The task to assess: `$ARGUMENTS`

## 1. Build the catalog (cheap, full)

Read the project's policy catalog — `.claude/policies/00-index.md` (each row is a
policy + one-line scope). If the project declares a broader doc catalog, include it.
Also note the **on-route set**: which policies the conditional routing table /
`routing.yml` predicates would fire on for this task. This on-route set is the
*prior*, NOT a filter — the panel is free to nominate anything in the catalog.

## 2. Fan out 5 independent reviewers (decorrelated lenses) — use Sonnet

Spawn **five subagents in parallel** (Task tool, model **sonnet** — cheap, and the
catalog is tiny). Decorrelation is the mechanism that makes the union miss-rate ≈ pᴺ;
identical agents miss together, so each gets a DISTINCT lens. Give each: the task,
the FULL catalog (the one-line scopes), and its lens. Each returns, as structured
text:
- **Nominations** — every policy that *might* apply (be inclusive: "if it could
  matter, list it"), each with a one-line reason. Do NOT just echo the on-route set.
- **Negative justification** — for each major policy GROUP it did NOT nominate, one
  line on why it is not relevant (this turns silent omissions into auditable calls).

The five lenses:
1. **Data-type** — what kind of data is involved → which data / measurement policies.
2. **Study-design / estimand** — descriptive vs causal vs predictive → which
   methodology policies.
3. **Output / deliverable** — what is produced (tables, figures, report, model) →
   which reporting / reproducibility policies.
4. **Failure-mode** — what could go *wrong* here → which policy guards that failure
   (bias, missingness, leakage, immortal-time, separation, …).
5. **Adversarial escape** — "the obvious route is {on-route set}. What relevant
   policy is OFF that route, and why would skipping it bite us?" Argue for off-path
   policies specifically.

## 3. Aggregate — union for recall, votes for triage

- **Tier-1 — must consult:** nominated by a **majority** (≥3 of 5). High confidence.
- **Tier-2 — consider:** nominated by **≥1** agent (union). This tier IS the recall
  net — skim each one's one-line scope; cost is trivial. Everything the escape lens
  flagged lands here with its argument.
- Do **not** drop a Tier-2 item just because only one lens raised it — requiring
  agreement is a precision move that *lowers* recall.

## 4. Synthesize and report (you, the calling agent, do this — Opus-grade)

Present:
- **Tier-1 (must consult):** policy + why + vote count.
- **Tier-2 (consider):** policy + why + which lens flagged it.
- **Deliberately excluded:** the consolidated negative justifications (so the user
  can audit what was set aside and challenge it).
- **Decorrelation check:** did the lenses diverge, or return near-identical sets? If
  near-identical, **say so** — the safety margin is weak and a relevant policy could
  still hide; recommend a manual scan of the full index.
- **Off-route catches:** explicitly name any Tier-2 policy that was NOT in the
  on-route set — these are the false negatives the net just caught.

## 5. Hard stop

Do not plan or execute the task. Present the coverage map and stop. This is a
pre-flight check; the user decides what to do with it.
