#!/usr/bin/env python3
"""CI check `lwh-env-leak`: no local-environment or private-project leak.

SACRED (owner directive 8): this repo's build/test/deploy must not depend
on, or leak, anything about the machine or private projects it was built
on. Scans every git-tracked, non-binary file for:

  - a Windows drive letter (`C:\\...`)
  - a POSIX home directory (`/Users/<name>` or `/home/<name>`)
  - a hard-coded interpreter invocation: `py -3`, `py -3.NN`, or an
    absolute path to a `python`/`python3`/`python.exe` binary
  - a private-project name leak: `leapware-cpt`, `leapware-financial`,
    `followoz`, or the owner's personal name fragments (`manny`, `ramos`),
    case-insensitive

Allow-listed: this script's own pattern data (it necessarily names the
patterns it looks for) and files under `tests/**/fixtures/**` whose
filename or path makes clear they are synthetic (contain `fixture`).

Usage:
    python scripts/lwh_check_env_leak.py

Stdlib only. Exits 0 and prints "lwh-env-leak check passed" on success;
otherwise prints every finding (file:line) and exits 1.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SELF_PATH = Path(__file__).resolve()

DRIVE_LETTER = re.compile(r"\b[A-Za-z]:\\[\w][\w.\- ]")
POSIX_HOME = re.compile(r"(?<!\w)/(?:Users|home)/[\w.\-]+")
PY_DASH3 = re.compile(r"\bpy\s+-3(\.\d+)?\b")
HARDCODED_INTERPRETER = re.compile(
    r"(?:[A-Za-z]:\\|/)(?:[\w.\-]+[\\/])*python3?(?:\.exe)?(?=[\s\"'`]|$)"
)

PRIVATE_NAME_SUBSTRINGS = [
    "leapware-cpt",
    "leapware-financial",
    "followoz",
    "manny",
    "ramos",
]

_BINARY_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".zip", ".pyc"}


def _tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [REPO_ROOT / line for line in result.stdout.splitlines() if line]


# Files that necessarily carry this scanner's own pattern data (or, for a
# test file, synthetic needles that exercise it) rather than a real leak.
_PATTERN_DATA_EXEMPT = {
    "scripts/lwh_check_env_leak.py",
    "scripts/lwh_handoff.py",
    "tests/core/test_lwh_handoff.py",
}


def _is_exempt(path: Path) -> bool:
    if path == SELF_PATH:
        return True
    posix = path.relative_to(REPO_ROOT).as_posix()
    if posix in _PATTERN_DATA_EXEMPT:
        return True
    if "fixture" in posix.lower():
        return True
    return False


def check() -> list[str]:
    findings: list[str] = []
    for path in _tracked_files():
        if not path.is_file() or path.suffix.lower() in _BINARY_SUFFIXES:
            continue
        if _is_exempt(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        for lineno, line in enumerate(text.splitlines(), start=1):
            if DRIVE_LETTER.search(line):
                findings.append(f"{rel}:{lineno}: Windows drive letter")
            if POSIX_HOME.search(line):
                findings.append(f"{rel}:{lineno}: POSIX home directory path")
            if PY_DASH3.search(line):
                findings.append(f"{rel}:{lineno}: hard-coded 'py -3' interpreter launch")
            if HARDCODED_INTERPRETER.search(line):
                findings.append(f"{rel}:{lineno}: absolute path to a python interpreter")
            lowered = line.lower()
            for needle in PRIVATE_NAME_SUBSTRINGS:
                if needle in lowered:
                    findings.append(f"{rel}:{lineno}: private-project name leak ('{needle}')")
    return findings


def main() -> int:
    findings = check()
    if findings:
        for f in findings:
            print(f"FAIL: {f}")
        return 1
    print("lwh-env-leak check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
