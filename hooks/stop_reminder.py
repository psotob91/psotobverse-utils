"""Stop hook: LIGHTWEIGHT checkpoint + meta-learning reminder.

To avoid being noise every turn, it only speaks up when there are UNCOMMITTED changes (unprotected
work). If the tree is clean, it stays silent. Never blocks (exit 0). Stdlib only.

Generic (project-agnostic): wire it as a `Stop` hook in any project's .claude/settings.json.
"""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return 0  # no git or no access: don't get in the way
    if out.returncode == 0 and out.stdout.strip():
        print(
            "[reminder] There are uncommitted changes. Before closing the block: "
            "checkpoint (commit/tag), meta-learn (your learning log) and reflect (your reflector). "
            "See the robust core (robust-cycle, sections b, c, f) bundled with the workflow plugin."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
