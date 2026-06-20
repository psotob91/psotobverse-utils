# psotobverse-utils

Generic, reusable **engineering-workflow skills** for Claude Code — extracted from the MS-RIE project
and made project-agnostic. They encode *how to work with quality without burning context*: verifiable
cycles, audit/reconciliation, goal-directed execution, and deliberate engineering.

These are **workflow** skills (about the *how*), deliberately separate from any *domain* skill (about
the *what*, e.g. a document-ingestion pipeline). They auto-invoke by their `description`; you don't
type the slash.

## The skills

| Skill | Purpose |
|---|---|
| `/index` | Organize and index the repo; regenerate `llms.txt` + `README.md`; corrects what a hygiene hook detects. Runs in batches, not on every change. |
| `/reconcile` | 6-phase audit/improve cycle (quick audit → investigate → adversarial re-audit → propose → implement → closing audit), generator != auditor. |
| `/goal` | Goal-directed execution with a lightweight file backlog; stops by convergence or non-convergence. |
| `/deliberate` | Four deliberate-engineering principles, applied only to substantial/high-impact tasks. |
| `_shared/principles.md` | The values layer (not a skill): the 6 principles the skills embody — minimalism, orthogonality, verification-first, evidence-not-assertion, control-over-autonomy, stop-well. The *why*. |
| `_shared/robust-cycle.md` | The shared robust core all four read (not a skill): objective verification (generator!=auditor in a separate context, cold-read), stop-by-convergence (loop until dry — two clean rounds), checkpoint-commit, meta-learning, auto-reflector, self-healing. The *how*. |
| `_shared/anti-hallucination.md` | Three evidence-backed defenses (not a skill): claim->evidence anchoring, retrieved-content-is-data-not-instructions, anti-sycophancy concession gate. The *anti-failure*. |

## Install into another project

```bash
python install.py /path/to/your/project              # copies the 5 skills into <project>/.claude/skills/
python install.py /path/to/your/project --force      # overwrite existing copies
python install.py /path/to/your/project --with-hooks  # also copy hooks/ (see below)
```

## Optional hooks

`hooks/` ships two generic, stdlib, non-blocking hooks harvested from the source project:
- `doc_hygiene.py` — PostToolUse on `.md`: detects oversize/format/broken-ref issues (the `/index` or
  `/reconcile` skill corrects them).
- `stop_reminder.py` — Stop: nudges checkpoint + meta-learning when the tree has uncommitted changes.

Install with `--with-hooks`, then merge `hooks/settings.snippet.json` into your `.claude/settings.json`.
`hooks/POLICIES.md` also documents a generic **anti-drift** pattern (compare run metrics vs a baseline)
and records what was harvested into this repo vs left in the domain project.

## The specialization contract (overlay)

The skills are **100% generic**: they refer to "the project's test/lint/audit/hygiene gates" and "the
project's as-built docs" without naming them. **Each consuming project supplies the concrete mapping**
in a *Skill specialization (overlay)* section of its own `CLAUDE.md`. This keeps the skills coupling-free
and gives every project full freedom over its toolchain.

Minimal overlay table to paste into your `CLAUDE.md`:

```markdown
## Skill specialization (project overlay)
| Generic gate (in the skill) | This project's command/path |
|---|---|
| Tests        | <e.g. pytest -q> |
| Linter       | <e.g. ruff check .> |
| Doc audit    | <your doc auditor, if any> |
| Doc hygiene  | <your hygiene tool, if any> |
| Outputs index| <your outputs-index generator, if any> |
| As-built doc | <path to your as-built documentation> |
| Learning log | <e.g. learning/> |
```

If a gate doesn't exist in your project, the skill simply skips it — the patterns are invariant, the
gates are optional.

## Verifying auto-invocation

After installing, type natural-language triggers (no slash) and confirm the skill fires:
- "audit this for inconsistencies" / "is everything coherent?" → `/reconcile`
- "organize the project" / "update the index" → `/index`
- "get X working, don't stop until it's done" → `/goal`
- "design this refactor carefully" → `/deliberate`

## Provenance

Extracted from `ms-rie-orchestrator`. Any domain-specific bias was moved out into each project's
`CLAUDE.md` overlay. See that repo's `learning/` for the design rationale.
