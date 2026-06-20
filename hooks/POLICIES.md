# Generic meta-system policies (harvested from ms-rie-orchestrator)

These are project-agnostic patterns extracted from the MS-RIE project's meta-system. They pair with
the workflow skills and the robust core (`.claude/skills/_shared/robust-cycle.md`).

## What was harvested vs left in the domain project

| Aspect | Verdict | Why |
|---|---|---|
| `doc_hygiene.py` hook | **Adapted to utils** (`hooks/`) | Pure stdlib, no domain logic; detects size/format/broken-ref issues on any `.md`. |
| `stop_reminder.py` hook | **Adapted to utils** (`hooks/`) | Pure stdlib; only nudges checkpoint+meta-learning when the tree is dirty. Generic. |
| Anti-drift **pattern** | **Pattern adapted** (this doc) | The pattern (compare a run's metrics vs a baseline, alert on regression) is generic. |
| Anti-drift **monitor code** | **Left in the domain project** | The concrete metrics (e.g. tables/figures/formulas extracted) are domain-specific. |
| Output-layout contract | **Left in the domain project** | The artifact schema is domain-specific; the hygiene hook already enforces generic structure. |

## The anti-drift policy (generic pattern)

Drift = silent quality regression between runs that tests don't catch. The cheap, deterministic guard:

1. **Baseline.** After a known-good run, snapshot its key metrics to a baseline file (counts of the
   things your process produces, plus wall-clock time per unit of work).
2. **Compare.** On each subsequent run, compare against the baseline. Alert when:
   - a **count regresses** (the run produced fewer of something than the baseline), or
   - **time blows up** (this run took more than N× the baseline, e.g. 2×).
3. **New keys don't alert.** Work items with no baseline entry are not regressions — they're new.
4. **Deterministic, $0 tokens.** This is a plain comparison script, not an LLM call. Keep it in CI or
   as a post-run step.

To implement in a project: define your domain's count metrics, write a `<project>/scripts/drift_monitor.py`
that loads `run.json` + `baseline.json` and emits alerts, and record the rationale in your reflector.
See the MS-RIE project's `scripts/drift_monitor.py` for a worked example.

## Wiring the hooks

Copy `hooks/` into your project (or run `install.py <target> --with-hooks`) and merge
`hooks/settings.snippet.json` into your `.claude/settings.json`. Both hooks are non-blocking (exit 0)
and need no venv.
