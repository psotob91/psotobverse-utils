---
name: audit-report
description: >-
  Structure the output of a multi-agent audit, diagnostic, workflow review, or any
  large analysis so it does NOT blow context. Use it whenever you run a workflow /
  fan-out audit / deep review whose raw result is large (many KB of JSON or
  per-agent maps), or when the user asks to "organize the audit", "save the
  diagnosis properly", "where did the audit go". It writes a small indexed summary
  to docs/audits/<date>-<slug>/ and keeps the raw as a referenced sidecar — never
  inline a mega-artifact into the conversation or a single unindexed temp blob.
---

# /audit-report — organize audit / diagnostic output (anti-context-blowup)

A multi-agent audit can emit hundreds of KB. Reading that wholesale blows context
and invites drift/hallucination; leaving it in a temp file loses it and indexes
nothing. This skill enforces a small, layered, indexed structure.

## The structure
Write results to `docs/audits/<YYYY-MM-DD>-<slug>/`:

```
docs/audits/<date>-<slug>/
  00-summary.md     # ALWAYS-READ. ~1–2 screens: purpose, top findings (severity),
                    #   the verdict, and the decision/next steps. Bounded by design.
  01-findings.md    # optional, medium: the full findings list with evidence (file:line).
  raw/              # optional sidecars: per-agent maps / large JSON. Referenced, NOT read wholesale.
  INDEX.md          # one line per file above — the cheap entry point.
```

## Rules
1. **Summary first, bounded.** `00-summary.md` is the contract: if it grows past
   ~2 screens, push detail down into `01-findings.md` or `raw/`. The summary is what
   a future session reads to recover the audit cheaply.
2. **Raw is a sidecar, never inline.** Large JSON / per-agent maps go under `raw/`
   (or stay in the workflow transcript and are *linked* by path). Never paste a
   mega-artifact into the chat or read it whole — `grep`/section-read it.
3. **Index it.** Add an `INDEX.md` line, and (if durable) a pointer from
   `CHANGELOG.md` / `SESSION_STATE.md`. An unindexed audit is a dangling artifact.
4. **Verdict is part of the summary.** If the audit used an adversarial / cold-read
   verifier, fold its confirmations and corrections into `00-summary.md`.
5. **Carry findings into the loop.** Route durable lessons to `learning/` via
   `/reflect`; file actionable items in `REFLECTOR.md`/`WATCHLIST.md`.

## When invoked
Given an audit/workflow result (a path to a large output, or in-context findings):
write the `docs/audits/<date>-<slug>/` tree, distill `00-summary.md` (+ `INDEX.md`),
move/reference the raw under `raw/`, and report the summary path — do not echo the
raw back into context.
