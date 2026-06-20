"""Document hygiene: size by type, basic markdown structure, and broken links.

DETECTS (does not fix; correction is the judgment of the /index or /reconcile skill). Stdlib only, so
it can run as a PostToolUse hook on EVERY `.md` without a venv and without latency.

Generic (project-agnostic): wire it as a PostToolUse hook (matcher Write|Edit|MultiEdit|NotebookEdit)
in any project's .claude/settings.json. The size limits below are soft conventions; adjust per project.

Two modes:
  - CLI:  python doc_hygiene.py [paths...]          # check given paths (or --all = every .md)
  - Hook: receives the PostToolUse JSON on stdin; extracts the touched file and checks it.

Exit 0 if no alerts; exit 1 if there are (useful for CI). In hook mode it prints the notice so the
agent sees it, but does not block (exit 0) unless `--strict`.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Line limits by doc type (soft ceiling; over the limit = "consider splitting" alert).
LIMITS = {
    "skill": 250,        # SKILL.md: progressive disclosure; the body shouldn't bloat
    "reference": 300,    # references/*.md: over 300, prefer a TOC or a split
    "plan": 200,         # plans: if it grows, split into a referenced .md (don't truncate)
    "log": 200,          # append-only (LEARNING_LOG, RUNLOG, DRIFT_LOG): nudge to consolidate
    "doc": 400,          # general docs
}
LLMS_TXT_MAX_BYTES = 10240  # ceiling of the navigable index


def _classify(path: Path) -> str:
    name = path.name.lower()
    parts = {p.lower() for p in path.parts}
    if name == "llms.txt":
        return "llms"
    if name == "skill.md":
        return "skill"
    if "references" in parts:
        return "reference"
    if "plans" in parts:
        return "plan"
    if name.endswith("_log.md") or name in {"runlog.md", "drift_log.md", "learning_log.md"}:
        return "log"
    return "doc"


def _check_links(path: Path, text: str) -> list[str]:
    """Markdown links [..](path) whose local target doesn't exist (ignores http and anchors)."""
    out = []
    for m in re.finditer(r"\]\(([^)]+)\)", text):
        raw = m.group(1).strip()
        if not raw or raw.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = re.sub(r":\d+$", "", raw.split("#")[0])  # strip :line suffix, not URLs
        if not (path.parent / target).exists() and not Path(target).exists():
            out.append(f"broken link: {target}")
    return out


def check_file(path: Path) -> list[str]:
    """Return the list of alerts for a file (empty = healthy)."""
    if not path.exists():
        return [f"does not exist: {path}"]
    alerts: list[str] = []
    kind = _classify(path)
    raw = path.read_bytes()

    if kind == "llms":
        if len(raw) > LLMS_TXT_MAX_BYTES:
            alerts.append(f"llms.txt {len(raw)}B > {LLMS_TXT_MAX_BYTES}B (saturates context; split/trim)")
        return alerts  # llms.txt isn't measured by lines or prose structure

    text = raw.decode("utf-8", errors="replace")
    lines = text.splitlines()
    limit = LIMITS.get(kind, LIMITS["doc"])
    if len(lines) > limit:
        verb = "consolidate" if kind == "log" else "split into a referenced .md (don't truncate)"
        alerts.append(f"{len(lines)} lines > {limit} ({kind}); consider {verb}")

    # Minimal structure: a .md should open with an H1 title (except append-only logs).
    if kind != "log":
        first = next((ln for ln in lines if ln.strip()), "")
        if not first.startswith("#") and not first.startswith("---"):
            alerts.append("no H1 title nor frontmatter at the start (weak structure)")

    alerts.extend(_check_links(path, text))
    return alerts


def _iter_all_md() -> list[Path]:
    root = Path(__file__).resolve().parent.parent
    skip = {".git", ".venv", "node_modules", "archive", "__pycache__",
            ".pytest_cache", ".ruff_cache"}
    return [p for p in root.rglob("*.md") if not (skip & set(p.parts))]


def _path_from_hook_stdin() -> Path | None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return None
    ti = payload.get("tool_input", {}) or {}
    fp = ti.get("file_path") or ti.get("path") or ti.get("notebook_path")
    return Path(fp) if fp else None


def main(argv: list[str]) -> int:
    strict = "--strict" in argv
    argv = [a for a in argv if a != "--strict"]

    if "--all" in argv:
        targets = _iter_all_md()
    elif argv:
        targets = [Path(a) for a in argv]
    elif not sys.stdin.isatty():
        p = _path_from_hook_stdin()  # hook mode
        if p is None or p.suffix.lower() not in {".md", ".txt"}:
            return 0
        targets = [p]
    else:
        targets = _iter_all_md()

    total = 0
    for path in targets:
        alerts = check_file(path)
        if alerts:
            total += len(alerts)
            rel = path.name if len(targets) == 1 else path
            print(f"[doc_hygiene] {rel}:")
            for a in alerts:
                print(f"  - {a}")

    if total == 0:
        if "--all" in argv or (argv and sys.stdin.isatty()):
            print("[doc_hygiene] no alerts")
        return 0
    return 1 if strict or "--all" in argv else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
