"""Shared helpers for the conditional-routing hooks (stdlib only, no PyYAML).

The routing layer is OPT-IN per project: a project ships
`$CLAUDE_PROJECT_DIR/.claude/policy/routing.yml`. Absent file -> the hooks no-op
(so the plugin never nags unrelated repos). Everything FAILS OPEN.

routing.yml is a small, regular subset of YAML (see the template factory's
routing.yml.jinja). We parse only that subset: a `rules:` list whose items carry
`id`, a `signal:` block with inline-list `prompt:`/`path_glob:`, plus scalar
`next_policy`/`bypass_if`/`mode` and an inline-list `requires_first`.
"""
from __future__ import annotations

import fnmatch
import json
import os
from pathlib import Path

ROUTING = (".claude", "policy", "routing.yml")


def project_root() -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def _scalar(v: str) -> str:
    v = v.strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        return v[1:-1]
    return v


def _list(v: str) -> list:
    v = v.strip()
    if v.startswith("["):
        try:
            return [str(x) for x in json.loads(v)]
        except Exception:
            return [_scalar(x) for x in v.strip("[]").split(",") if x.strip()]
    return []


def parse_rules(text: str) -> list[dict]:
    rules: list[dict] = []
    cur: dict | None = None
    for raw in text.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("- id:"):
            cur = {"id": _scalar(s[5:]), "prompt": [], "path_glob": [],
                   "requires_first": [], "next_policy": "", "bypass_if": "",
                   "mode": "remind"}
            rules.append(cur)
            continue
        if cur is None or ":" not in s:
            continue
        k, _, v = s.partition(":")
        k = k.strip()
        if k == "prompt":
            cur["prompt"] = _list(v)
        elif k == "path_glob":
            cur["path_glob"] = _list(v)
        elif k == "requires_first":
            cur["requires_first"] = _list(v)
        elif k in ("next_policy", "bypass_if", "mode"):
            cur[k] = _scalar(v)
    return rules


def load_rules() -> list[dict]:
    """Parsed rules, or [] if not opted in / unreadable (fail-open)."""
    try:
        text = Path(project_root(), *ROUTING).read_text(encoding="utf-8")
    except OSError:
        return []
    try:
        return parse_rules(text)
    except Exception:
        return []


def match_prompt(rule: dict, prompt: str) -> bool:
    low = prompt.lower()
    return any(kw and kw.lower() in low for kw in rule.get("prompt", []))


def _posix(path: str) -> str:
    return str(path).replace("\\", "/")


def match_path(rule: dict, target: str) -> bool:
    tp = _posix(target)
    base = tp.rsplit("/", 1)[-1]
    for g in rule.get("path_glob", []):
        gp = _posix(g)
        if fnmatch.fnmatch(tp, gp) or fnmatch.fnmatch(base, gp.rsplit("/", 1)[-1]):
            return True
    return False


def sibling_satisfied(rule: dict, target: str) -> bool:
    """True if a `requires_first` artifact exists near the target (or none required)."""
    req = rule.get("requires_first", [])
    if not req:
        return True
    try:
        d = Path(target).resolve().parent
        names = [p.name for p in d.iterdir()] if d.is_dir() else []
    except OSError:
        return True  # cannot check -> do not block (fail open)
    for pat in req:
        pat = pat if ("*" in pat or "?" in pat) else f"*{pat}*"
        if any(fnmatch.fnmatch(n.lower(), pat.lower()) for n in names):
            return True
    return False
