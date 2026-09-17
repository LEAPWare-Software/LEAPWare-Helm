#!/usr/bin/env python3
"""CI check backing the `lwh-portable` job: run the hook EXACTLY as declared.

Reads `plugins/claude/lwh/hooks/hooks.json`, takes the literal `command`
string for the `PreToolUse` / `Agent` hook, substitutes `${CLAUDE_PLUGIN_ROOT}`
the same way Claude Code does (a plain string replace, before the shell ever
sees it), and executes that string through the platform shell exactly as
Claude Code would (`shell=True`: `cmd.exe` on Windows, `sh` elsewhere) —
this is the portable dual-interpreter launch chosen in
`docs/architecture.md#the-hook-launch-method` specifically because it is
safe to test this way, without installing anything beyond a `setup-python`
Python already on `PATH`.

A deny-mode policy (`budget_line: deny`) is pointed at via `LWH_POLICY_PATH`
and a `PreToolUse`/`Agent` fixture with no `BUDGET:` line is fed on stdin,
so a correct run must print `hookSpecificOutput.permissionDecision: "deny"`.

Usage:
    python scripts/lwh_check_hook_launch.py

Stdlib only. Exits 0 and prints "lwh-portable check passed" on success;
otherwise prints the failure and exits 1.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_ROOT / "plugins" / "claude" / "lwh"
HOOKS_JSON = PLUGIN_DIR / "hooks" / "hooks.json"
FIXTURE = REPO_ROOT / "tests" / "adapters" / "fixtures" / "claude" / "pretooluse_agent_no_budget.json"

_DENY_POLICY = {
    "$schema": "./schema.json",
    "rules": {"budget_line": {"mode": "deny", "options": {}}},
}


def _hook_command() -> str:
    hooks = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))
    for entry in hooks["hooks"]["PreToolUse"]:
        if entry.get("matcher") == "Agent":
            for hook in entry["hooks"]:
                return hook["command"]
    raise SystemExit("FAIL: no PreToolUse/Agent hook found in hooks.json")


def main() -> int:
    command = _hook_command().replace("${CLAUDE_PLUGIN_ROOT}", str(PLUGIN_DIR))

    with tempfile.TemporaryDirectory(prefix="lwh-portable-") as tmp:
        policy_path = Path(tmp) / "deny-policy.json"
        policy_path.write_text(json.dumps(_DENY_POLICY), encoding="utf-8")

        import os

        env = dict(os.environ)
        env["LWH_POLICY_PATH"] = str(policy_path)
        env["LWH_LEDGER_PATH"] = str(Path(tmp) / "ledger.jsonl")

        result = subprocess.run(
            command,
            shell=True,
            cwd=REPO_ROOT,
            input=FIXTURE.read_text(encoding="utf-8"),
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )

    if result.returncode != 0:
        print(f"FAIL: hook command exited {result.returncode}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        return 1

    try:
        payload = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as exc:
        print(f"FAIL: hook stdout was not valid JSON: {exc}")
        print(f"stdout: {result.stdout}")
        return 1

    decision = payload.get("hookSpecificOutput", {}).get("permissionDecision")
    if decision != "deny":
        print(f"FAIL: expected permissionDecision 'deny', got {decision!r}: {payload}")
        return 1

    print("lwh-portable check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
