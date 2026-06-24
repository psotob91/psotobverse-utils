---
name: tidy
description: >-
  Propose where loose / misplaced files should go and relocate them ONLY after you confirm.
  Use it WHENEVER the user says "tidy up", "this file is in the wrong place", "where should this
  go?", "clean up the loose files", "organize this", "I dumped some files in the root", or when a
  write was just blocked for being outside the allowed structure. It NEVER moves anything
  automatically — it lists a proposed plan (from -> to, with reason) and waits for approval. This is
  the lightweight relocation verb that pairs with the `nothing_loose` write-guard hook; for a full
  repo organization pass (regenerate the index, README, split oversize docs) use `/index` instead;
  for content coherence (docs-vs-code) use `/reconcile`.
---

# /tidy — propose relocations for loose files (never auto-move)

Apply the **robust core** (`../_shared/robust-cycle.md`) and the **anti-hallucination primitives**
(`../_shared/anti-hallucination.md`). The allowed write structure for this project is declared in
`.claude/policy/paths.allow.json` (the same allowlist the `nothing_loose` PreToolUse hook enforces);
the project's concrete commands come from the `CLAUDE.md` overlay.

## Procedure
1. **Detect** — find files that sit outside the allowed structure or in an obviously wrong place:
   files in the repo root that belong under `docs/`, `outputs/`, `context/`, `tmp/`, source dirs, etc.;
   scratch/temporary files that should be in `tmp/`; duplicates of indexed artifacts. Use the project's
   hygiene tool if one is wired.
2. **Propose** — output a table `from -> to (reason)` for each loose file. Group by destination.
   Flag anything risky (a move that would break an import, a link, or a relative path) and say so.
   Do NOT move anything yet.
3. **Confirm** — wait for the user to approve, reject, or edit the plan. Default to NOT moving.
4. **Execute (only on approval)** — move the approved files. Do the move and any reference/link fix
   in **separate, verifiable steps** (move, then update references) so nothing breaks silently.
   Prefer `git mv` so history is preserved. After moving, re-check that no link/import broke.
5. **Close** — short summary of what moved and what was left. Record any recurring mess pattern in the
   project's learning log so the structure or the allowlist can be improved.

## Rules
- **Propose, then confirm. Never auto-move.** A wrong automatic move breaks paths, imports and links.
- **Don't invent destinations:** route to the allowlisted structure; if a file has no obvious home,
  say so and ask, rather than guessing.
- **Reversible first:** `git mv` over delete; never delete to "tidy" without explicit confirmation
  (deletion is `/index`'s archive-or-delete step, with confirmation).
- **Boundary:** loose-file relocation only. Index regeneration / README / oversize-doc splitting →
  `/index`. Docs-vs-code coherence → `/reconcile`.

## Output
The proposed `from -> to` plan (pre-approval), then — after approval — the executed moves, the
reference fixes, and the verification that nothing broke.
