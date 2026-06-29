---
name: rescue-manifest
description: >-
  Plans the migration of an arbitrary legacy / source repository into a project's target layout:
  inventories every item, classifies it KEEP / DROP / REGENERATE / KEEP-EXTERNAL, and applies four
  tests -- regenerability (rebuilds from in-repo sources quickly without human judgment -> do not
  carry), the archivist test (would a data archivist include it in a deposit package? -> practice
  vs agent-derived), a hard-coded-path audit (flag absolute paths before copying), and a size gate
  (large agent-class files need justification or are dropped) -- then emits a decision-matrix
  manifest for human sign-off. Use it when the user says "migrate / rescue / salvage this old repo
  into the template", "harmonize a legacy project", "what should we keep or drop", or "build a
  migration manifest". It PLANS the migration (a proposal) and moves nothing -- hand the approved
  moves to /tidy. For relocating loose files WITHIN one repo use /tidy; for organizing + indexing
  a single repo use /index; for docs-vs-code coherence use /reconcile.
---

# /rescue-manifest -- plan a repo migration as a decision matrix

Apply the **robust core** (`../_shared/robust-cycle.md`) and the **anti-hallucination primitives**
(`../_shared/anti-hallucination.md`): every classification is a factual claim -> anchor it to what
you observed (a path, a size, a grep hit), never a guess. Generic by design -- the *consuming*
project supplies the concrete target layout in its `CLAUDE.md` overlay; this skill never hard-codes
a project's folders. It PLANS; `/tidy` executes the approved moves.

## What it does
1. **Inventory the source** -- walk the source repo: a file/dir manifest with sizes, every config
   and manifest, and any external data the repo points at. Copy nothing yet.
2. **Classify each item** into exactly one class:
   - **KEEP** -- carries to the new project (inputs, human-canonical docs, code, living records).
   - **DROP** -- both the item and its source are omitted: another KEEP item (code/build) already
     rebuilds it, so there is nothing to carry.
   - **REGENERATE** -- agent-derived output to rebuild on demand: the generator is KEEP, only its
     output is dropped (gitignored on rebuild).
   - **KEEP-EXTERNAL** -- large / private data that never lives in the repo: register its path + an
     env var + a symlink/junction; never copy the bytes in.
3. **Apply the four tests** (each decides or flags a class):
   - **Regenerability** -- if it rebuilds from in-repo sources in under 30 minutes (or the
     project-declared rebuild budget) without human judgment -> DROP/REGENERATE; do not carry.
   - **Archivist** -- "would a data archivist include it in a deposit package?" yes -> practice
     (committed); no -> agent-derived (regenerable, gitignored).
   - **Hard-coded-path audit** -- grep every config/manifest for absolute paths; flag each
     `needs-update` before anything is copied.
   - **Size gate** -- any agent-class file over 1 MB (default; the consuming project may override
     it in its overlay) needs explicit justification or auto-proposes DROP.
4. **Emit the manifest** -- one decision-matrix table:

   | item | class | decision | destination | why | flags |
   |------|-------|----------|-------------|-----|-------|

   plus a short list of every flagged item (hard-coded path, oversize, undecidable).
5. **Human sign-off** -- present the manifest and wait. Nothing moves on silence.

## Rules
- **Plan, do not move.** The manifest is a proposal; never auto-move or auto-delete. Deletions
  require explicit confirmation (git already keeps history; when in doubt, KEEP).
- **KEEP-EXTERNAL never copies bytes** -- it registers path + env var + symlink/junction only.
- **Flag every hard-coded path** before a copy; an unresolved absolute path blocks that item.
- **Evidence per row** -- anchor each classification to a path / size / grep hit
  (`../_shared/anti-hallucination.md`).
- **Stop by convergence** -- re-audit the manifest until a pass finds nothing new to reclassify.
- **Hand off to `/tidy`** for the actual relocation of approved **KEEP** items only;
  KEEP-EXTERNAL is registered separately (env var + symlink/junction), never relocated by `/tidy`.

## Output
A `MIGRATION_MANIFEST.md` (or the project's chosen path): the decision-matrix table, the flagged
list, and the open questions for sign-off. Approved moves are executed by `/tidy`; regenerables are
rebuilt by the project's build, not carried.
