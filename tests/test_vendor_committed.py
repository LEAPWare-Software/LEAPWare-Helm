"""Vendor trees must be committed, not gitignored.

A marketplace/plugin install pulls the repo from git with no build step
run afterward (scripts/build.py never executes on the install path), so
plugins/*/tokenwise/vendor/ must ship as real, tracked files. This test fails
if `git ls-files` does not see them — it would have caught #LWT-D0's
first CI break, where vendor/ was gitignored and CI's checkout simply
had no vendor tree to check against.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

VENDOR_DIRS = [
    "plugins/claude/tokenwise/vendor",
    "plugins/codex/tokenwise/vendor",
]


def _tracked_files(relative_dir: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", relative_dir],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def test_vendor_trees_are_tracked_by_git():
    for vendor_dir in VENDOR_DIRS:
        tracked = _tracked_files(vendor_dir)
        assert tracked, (
            f"{vendor_dir} has no files tracked by git (git ls-files returned "
            f"nothing) -- vendor/ must be committed, not gitignored, or an "
            f"install from git ships with no vendor tree"
        )


def test_vendor_dirs_not_gitignored():
    for vendor_dir in VENDOR_DIRS:
        result = subprocess.run(
            ["git", "check-ignore", "-q", vendor_dir],
            cwd=REPO_ROOT,
        )
        assert result.returncode != 0, f"{vendor_dir} is gitignored"


if __name__ == "__main__":
    sys.exit(0)
