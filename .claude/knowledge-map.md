# Knowledge map — psotobverse-utils (developing the plugin)

A router. Open the one file the task needs.

## Read-first

1. `.claude/constitution.md` (dogfoods `skills/_shared/`)
2. `CLAUDE.md` (layout, conventions, commands, safe-edit protocol)
3. this map

## Task → consult

| Task | Consult |
|------|---------|
| Add / change a **skill** | `skills/<name>/SKILL.md` + `skills/_shared/` (the shared core) |
| Add / change a **hook** | `hooks/<name>.py` + register in `hooks/hooks.json` (fail-open bootstrap) |
| Add / change a **command** | `commands/<name>.md` (frontmatter `description:` + body + `$ARGUMENTS`) |
| The lint/test **gate** | `python hooks/doc_hygiene.py --all` |
| **Safe-edit** a live hook | `CLAUDE.md` → "Safe-edit protocol" (cache fires, not source) |
| **Release** | bump `.claude-plugin/plugin.json` version + `CHANGELOG.md` |
| Self-guard allowlist | `.claude/policy/paths.allow.json` |
| Recurring lesson | `learning/PLAYBOOK.md`; shifting convention → `learning/STANDARDS_WATCH.md` |

## Lazy-loading

One row, one file. Do not preload `skills/`, `hooks/`, or `docs/` wholesale.
