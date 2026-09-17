#!/usr/bin/env python3
"""Apply (create or update) this repo's GitHub repository rulesets from JSON.

Reads every `*.json` file in `.github/rulesets/` and, for each one, either
creates a new ruleset (POST) or updates the existing one by name (PUT), via
`gh api`. `gh` carries the caller's auth, so this needs no token of its own
and works unchanged from any machine that has `gh auth login`'d.

Usage:
    python scripts/apply_rulesets.py                 # apply every ruleset
    python scripts/apply_rulesets.py --dry-run        # print the JSON, do nothing
    python scripts/apply_rulesets.py --repo OWNER/REPO --dry-run

Stdlib only (subprocess + json); shells out to the `gh` CLI, never to a
bare `curl`/token, so PAT scoping and 2FA stay exactly what `gh auth`
already enforces.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULESETS_DIR = REPO_ROOT / ".github" / "rulesets"
DEFAULT_REPO = "LEAPWare-Software/LEAPWare-Helm"


def _load_rulesets(rulesets_dir: Path) -> list[tuple[Path, dict]]:
    loaded = []
    for path in sorted(rulesets_dir.glob("*.json")):
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        if "name" not in data:
            raise ValueError(f"{path}: ruleset JSON is missing required key 'name'")
        loaded.append((path, data))
    return loaded


def _run_gh(argv: list[str], input_json: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["gh", *argv],
        input=input_json,
        capture_output=True,
        text=True,
    )


def _existing_ruleset_id(repo: str, name: str) -> int | None:
    result = _run_gh(["api", f"repos/{repo}/rulesets", "--jq", ".[] | select(.name==\"%s\") | .id" % name])
    if result.returncode != 0:
        raise RuntimeError(f"gh api repos/{repo}/rulesets failed: {result.stderr.strip()}")
    output = result.stdout.strip()
    if not output:
        return None
    # If more than one id came back (shouldn't happen), take the first.
    return int(output.splitlines()[0])


def _apply_one(repo: str, path: Path, data: dict, dry_run: bool) -> None:
    body = json.dumps(data)
    if dry_run:
        print(f"--- {path.name} ({data['name']}) ---")
        print(json.dumps(data, indent=2))
        return

    existing_id = _existing_ruleset_id(repo, data["name"])
    if existing_id is None:
        argv = ["api", "--method", "POST", f"repos/{repo}/rulesets", "--input", "-"]
        action = "created"
    else:
        argv = ["api", "--method", "PUT", f"repos/{repo}/rulesets/{existing_id}", "--input", "-"]
        action = "updated"

    result = _run_gh(argv, input_json=body)
    if result.returncode != 0:
        print(f"FAILED applying {path.name}: {result.stderr.strip()}", file=sys.stderr)
        raise SystemExit(1)
    print(f"OK: ruleset '{data['name']}' {action} ({path.name})")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=DEFAULT_REPO, help="owner/repo (default: %(default)s)")
    parser.add_argument(
        "--dry-run", action="store_true", help="print each ruleset's JSON; call nothing"
    )
    args = parser.parse_args()

    if not RULESETS_DIR.is_dir():
        print(f"no rulesets directory at {RULESETS_DIR}", file=sys.stderr)
        return 1

    rulesets = _load_rulesets(RULESETS_DIR)
    if not rulesets:
        print(f"no *.json rulesets found in {RULESETS_DIR}", file=sys.stderr)
        return 1

    for path, data in rulesets:
        _apply_one(args.repo, path, data, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
