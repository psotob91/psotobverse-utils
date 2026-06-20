---
name: index
description: >-
  Project organizer and indexer: keeps the repo navigable, with no loose or undocumented files and no
  redundancies, with a machine-navigable index (llms.txt) and a human README. Use it when the user
  says "organize the project", "this is a mess", "I can't find anything", "update the index", "there
  are duplicates", "document the structure", "reorganize", or periodically when closing a milestone. It
  also CORRECTS what the hygiene hook detects: splits large docs into a hierarchy, archives or deletes
  obsolete files (deletions with confirmation), renames to a convention. Regenerates llms.txt/README
  and the outputs index. Fires even if they just say "this needs order". This handles *file-level*
  tidiness and navigability; for *content* contradictions or docs-vs-code coherence, use `/reconcile`.
---

# /index — organize and index the project

Apply the **robust core** (`.claude/skills/_shared/robust-cycle.md`). This skill is the part that
**CORRECTS** what the hygiene hook only **detects** (cheap continuous detection vs batched correction:
do NOT reorganize on every change, do it periodically or when closing a milestone). Concrete tools
(hygiene tool, outputs-index generator) come from the project's `CLAUDE.md` overlay. Deciding a file is
obsolete/regenerable is a factual claim — anchor it to what you observed before archiving or deleting
(`.claude/skills/_shared/anti-hallucination.md`).

## What it does
1. **Audit the state** — walk the repo: loose/undocumented files, duplicates (e.g. `.md` vs
   regenerable `.html`), obsolete copies, docs over their size limit. Use the project's hygiene tool if any.
2. **Organize** —
   - **Rename** to the convention (clear, consistent slugs).
   - **Remove redundancies:** archive the regenerable/obsolete into `archive/` (reversible, no
     confirmation) or **delete** (ONLY with explicit user confirmation; remember git already keeps history).
   - **Leave nothing loose:** every file must be referenced from `llms.txt` or a sub-index.
3. **Split large docs** — if a `.md` exceeds its limit and compressing would lose info, split it into a
   hierarchy with **progressive disclosure** (an index + referenced sections), never truncate.
4. **Regenerate indices** —
   - root `llms.txt`: machine-navigable, **~10KB ceiling**, one line per file/dir with its purpose.
   - root `README.md`: didactic for humans (what it is, how to run it, folder map, status/errors).
   - outputs index: if the project defines an outputs index, regenerate it (e.g. via its build script).

## Rules
- **Deleting requires confirmation** from the user; archiving does not (it's reversible). When in doubt, archive.
- **Verify before moving:** if a file you were about to delete contradicts how it was described, or you
  didn't create it, stop and report instead of proceeding.
- **No broken links in indices:** after regenerating, validate that each linked path exists and that
  `llms.txt` stays under 10KB.
- **Respect declared memory/size ceilings** (don't bloat context: the index is for navigation, not for
  dumping content).
- **Cadence:** run in batches (when closing a milestone / on-demand), not on every edit.

## Output
A summary of what was reorganized (renamed/archived/deleted/split), `llms.txt` and `README.md` updated
and validated, the outputs index regenerated, and a commit of the ordering.
