#!/usr/bin/env python3
"""Validate and regenerate the "In flight" block of HANDOFF.md.

HANDOFF.md is the repo's own re-derivable state file (see
docs/handoff-protocol.md). This script is the ONLY thing that writes the
generated block; everything else in HANDOFF.md is prose a human/agent
wrote by hand and this script never touches.

Usage:
    python scripts/lwh_handoff.py --check   # validate HANDOFF.md, exit 1 on failure
    python scripts/lwh_handoff.py --write   # regenerate the generated block in place

Stdlib only. Cross-platform (no shell strings, argv lists to subprocess).
No network calls other than what `gh` itself performs; --check never
shells out at all, so it is safe to run offline / in CI without `gh` auth
for read-only validation of the file shape.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HANDOFF_PATH = REPO_ROOT / "HANDOFF.md"

SIZE_CAP_BYTES = 6000

BEGIN_MARKER = "<!-- lwh-handoff:begin -->"
END_MARKER = "<!-- lwh-handoff:end -->"

REQUIRED_SECTIONS = [
    "# HANDOFF",
    "## Start of session",
    "## In flight",
    "## Re-derive state",
    "## Hard rules",
    "## Traps",
]

# Patterns that must never appear in a committed HANDOFF.md: an absolute
# path (POSIX or a Windows drive letter) or a real person's name/account
# fragment. This keeps the file honest about SACRED (no local-environment
# dependence) and keeps a human identity out of a machine-read file.
FORBIDDEN_PATTERNS = [
    re.compile(r"[A-Za-z]:\\"),  # Windows drive letter, e.g. C:\
    re.compile(r"(?<!\w)/(?:Users|home)/\w+"),  # POSIX home directory
]

FORBIDDEN_SUBSTRINGS = [
    "manny",
    "ramos",
    "followoz",
    "leapware-cpt",
    "leapware-financial",
]


class ValidationError(Exception):
    """Raised by _validate() with a human-readable reason."""


def _run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip()


def _run_gh(args: list[str]) -> str:
    try:
        result = subprocess.run(
            ["gh", *args],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def _utc_now_iso() -> str:
    import datetime

    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def _generate_block() -> str:
    """Build the text between BEGIN_MARKER and END_MARKER from git/gh state.

    Every value here is re-derived live; nothing is carried over from a
    previous run. gh calls degrade to "unavailable" rather than failing
    the whole regeneration, since --write may run without gh auth.
    """
    main_sha = _run_git(["rev-parse", "origin/main"]) or _run_git(["rev-parse", "main"]) or "unknown"
    generated_at = _utc_now_iso()

    pr_list = _run_gh(
        [
            "pr",
            "list",
            "--state",
            "open",
            "--json",
            "number,title,headRefName,statusCheckRollup",
            "--template",
            "{{range .}}#{{.number}} {{.title}} ({{.headRefName}})\n{{end}}",
        ]
    )
    if not pr_list:
        pr_list = "(unavailable: no `gh` auth in this environment, or no open PRs)"

    lines = [
        BEGIN_MARKER,
        "",
        f"Generated: {generated_at}",
        f"main SHA: {main_sha}",
        "",
        "Open PRs:",
        pr_list.strip() if pr_list.strip() else "(none)",
        "",
        END_MARKER,
    ]
    return "\n".join(lines) + "\n"


def _validate(text: str) -> list[str]:
    errors: list[str] = []

    size = len(text.encode("utf-8"))
    if size > SIZE_CAP_BYTES:
        errors.append(f"HANDOFF.md is {size} bytes, over the {SIZE_CAP_BYTES}-byte cap")

    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"missing required section heading: {section!r}")

    begin_count = text.count(BEGIN_MARKER)
    end_count = text.count(END_MARKER)
    if begin_count != 1:
        errors.append(f"expected exactly one {BEGIN_MARKER!r}, found {begin_count}")
    if end_count != 1:
        errors.append(f"expected exactly one {END_MARKER!r}, found {end_count}")
    if begin_count == 1 and end_count == 1:
        begin_idx = text.index(BEGIN_MARKER)
        end_idx = text.index(END_MARKER)
        if end_idx < begin_idx:
            errors.append("end marker appears before begin marker")

    for pattern in FORBIDDEN_PATTERNS:
        if pattern.search(text):
            errors.append(f"forbidden pattern found (absolute path): {pattern.pattern!r}")

    lowered = text.lower()
    for needle in FORBIDDEN_SUBSTRINGS:
        if needle in lowered:
            errors.append(f"forbidden substring found: {needle!r}")

    return errors


def cmd_check() -> int:
    if not HANDOFF_PATH.exists():
        print(f"FAIL: {HANDOFF_PATH} does not exist", file=sys.stderr)
        return 1
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    errors = _validate(text)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print(f"OK: {HANDOFF_PATH} passes all checks ({len(text.encode('utf-8'))} bytes)")
    return 0


def cmd_write() -> int:
    if not HANDOFF_PATH.exists():
        print(f"FAIL: {HANDOFF_PATH} does not exist; cannot regenerate a block into nothing", file=sys.stderr)
        return 1
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        print("FAIL: HANDOFF.md must already contain exactly one begin/end marker pair to regenerate", file=sys.stderr)
        return 1
    begin_idx = text.index(BEGIN_MARKER)
    end_idx = text.index(END_MARKER) + len(END_MARKER)
    new_block = _generate_block().rstrip("\n")
    new_text = text[:begin_idx] + new_block + text[end_idx:]
    HANDOFF_PATH.write_text(new_text, encoding="utf-8", newline="\n")
    errors = _validate(new_text)
    if errors:
        for error in errors:
            print(f"WARN after write: {error}", file=sys.stderr)
        return 1
    print(f"OK: wrote regenerated block to {HANDOFF_PATH}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true", help="validate HANDOFF.md, exit 1 on failure")
    group.add_argument("--write", action="store_true", help="regenerate the generated block in place")
    args = parser.parse_args(argv)

    if args.check:
        return cmd_check()
    return cmd_write()


if __name__ == "__main__":
    sys.exit(main())
