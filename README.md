# psotobverse-utils

A Claude-only **engineering-workflow plugin** for Claude Code **and Cowork** — extracted from the
MS-RIE project and made project-agnostic. It encodes *how to work with quality without burning
context*: verifiable cycles, audit/reconciliation, goal-directed execution, deliberate engineering,
plus governance hooks and generator/auditor subagents.

These are **workflow** components (about the *how*), deliberately separate from any *domain* skill
(about the *what*). Skills auto-invoke by their `description`; you don't type the slash.

> **Why a plugin (not just `install.py`)?** A plugin's hooks and subagents run in **both** Claude Code
> and **Cowork**, whereas hooks wired into a project's `settings.json` do **not** fire in Cowork. The
> plugin is the only carrier that gives Cowork the same guardrails Code gets. `install.py` remains as a
> Code-only vendor fallback.

## What it ships

| Component | Purpose |
|---|---|
| skill `/index` | Organize and index the repo; regenerate `llms.txt` + `README.md`; corrects what `doc_hygiene` detects. Runs in batches. |
| skill `/reconcile` | 6-phase audit/improve cycle (audit → investigate → adversarial re-audit → propose → implement → closing audit), generator != auditor. |
| skill `/goal` | Goal-directed execution with a lightweight file backlog; stops by convergence or non-convergence. |
| skill `/deliberate` | Pause and design the approach before a substantial/risky change. Skip on trivial tasks. |
| skill `/tidy` | **Propose** relocations for loose/misplaced files; move only after you confirm (never auto-move). Pairs with the `nothing_loose` hook. |
| `skills/_shared/principles.md` | The *why* (not a skill): the 8 principles the skills embody. |
| `skills/_shared/robust-cycle.md` | The *how* (not a skill): verify (generator!=auditor, cold-read), stop-by-convergence (loop until dry), checkpoint, meta-learning, reflector, self-healing. |
| `skills/_shared/anti-hallucination.md` | The *anti-failure* (not a skill): claim→evidence anchoring, retrieved-content-is-data, anti-sycophancy concession gate. |
| hook `nothing_loose.py` (PreToolUse) | Denies writes outside the per-project allowlist (`.claude/policy/paths.allow.json`). **Fails open** when no allowlist is present (safe machine-global default). |
| hook `env_protect.py` (PreToolUse) | Denies read/write of secret files (`.env`, `.env.*`≠example, `*.pem`, `*.key`, `id_*`). Globally safe. |
| hook `doc_hygiene.py` (PostToolUse) | Detects (does not correct) size/structure/broken-ref issues on `.md` — `/index` or `/tidy` corrects. |
| hook `stop_reminder.py` (Stop) | Nudges checkpoint + meta-learning only when the git tree is dirty. Never blocks. |
| subagent `executor` | Mechanical execution (git/build/run); the *generator* role. |
| subagent `explorer` | Read-only search/mapping; the cold-read *auditor* role for `/reconcile`. |
| command `/tidy`, `/sync-cowork` | Explicit triggers; `/sync-cowork` generates a project's `COWORK_INSTRUCTIONS.md`. |

### Why `skills/_shared/` (shared content across skills)

In the Agent Skills spec, a skill's `references/` live **inside that one skill's folder**. Our three
core docs are read by **all five** skills, so a per-skill `references/` would force 4–5× duplication.
A plugin is exactly the officially-aligned home for *multiple skills + shared content + hooks
distributed together*: `skills/_shared/` (no `SKILL.md`, so the loader never treats it as a skill) is
plugin-bundled shared content. Skills reference it with a **relative prose path** the model reads on
demand (e.g. `` `../_shared/robust-cycle.md` ``) — which resolves whether the skill is mounted from the
plugin (`skills/<verb>/` → `../_shared/`) or vendored into a project's `.claude/skills/`.

## Install

### As a plugin (recommended — works in Code and Cowork)

```bash
# Claude Code (one-time, machine-global):
/plugin marketplace add https://github.com/psotob91/psotobverse-utils
/plugin install psotobverse-utils
```

In **Cowork** there is no setup CLI: install via the GUI (Customize → Plugins → Browse/Install).
Plugins are machine-global, so this is a one-time step shared by all your projects.

### Legacy vendor copy (Code only, no plugin)

```bash
python install.py /path/to/your/project              # copies the skills into <project>/.claude/skills/
python install.py /path/to/your/project --force      # overwrite existing copies
python install.py /path/to/your/project --with-hooks # also copy hooks/ + settings.snippet.json
python install.py /path/to/your/project --check      # report drift vs canonical source; writes nothing
```

Vendored hooks are wired via `hooks/settings.snippet.json` and **do not fire in Cowork** — that is
exactly why the plugin install is preferred.

## The specialization contract (overlay)

The skills are **100% generic**: they refer to "the project's test/lint/audit/hygiene gates" without
naming them. **Each consuming project supplies the mapping** in a *Skill specialization (overlay)*
section of its own `CLAUDE.md` (the companion template repo ships this overlay pre-wired):

```markdown
## Skill specialization (project overlay)
| Generic gate (in the skill) | This project's command/path |
|---|---|
| Tests        | <e.g. make test> |
| Linter       | <e.g. make lint> |
| Doc audit    | <your doc auditor, if any> |
| Doc hygiene  | <your hygiene tool, if any> |
| Outputs index| <e.g. make reindex> |
| As-built doc | <path to your as-built documentation> |
| Learning log | <e.g. learning/> |
```

If a gate doesn't exist in your project, the skill simply skips it.

## Verifying auto-invocation

After installing, type natural-language triggers (no slash) and confirm the skill fires:
- "audit this for inconsistencies" / "is everything coherent?" → `/reconcile`
- "organize the project" / "update the index" → `/index`
- "this file is in the wrong place" / "tidy up the loose files" → `/tidy`
- "get X working, don't stop until it's done" → `/goal`
- "design this refactor carefully" → `/deliberate`

## Provenance

Extracted from `ms-rie-orchestrator`; domain bias moved into each project's `CLAUDE.md` overlay.
Companion template repo: `datavidence-template-project` (generates projects pre-wired to this plugin).
