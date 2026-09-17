#!/usr/bin/env python3
"""Validate plugins/codex/tokenwise against the shape this project's Codex plugin uses.

Checks (stdlib only):
  - .codex-plugin/plugin.json exists, is valid JSON, has name/version/description.
  - skills/tokenwise-config/SKILL.md and skills/tokenwise-report/SKILL.md exist.
  - hooks/README.md exists and no hooks/hooks.json is present (this plugin
    is reporting-only by deliberate decision; see docs/install-codex.md).
  - vendor/tokenwise_core and vendor/adapters/codex exist (scripts/build.py has
    been run — this does NOT itself run build.py).
  - .agents/plugins/marketplace.json references this plugin's path.

Exits 0 and prints "validation passed" on success; otherwise prints every
failure found (not just the first) and exits 1.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_ROOT / "plugins" / "codex" / "tokenwise"


def _read_json(path: Path, errors: list[str]):
    if not path.is_file():
        errors.append(f"missing file: {path}")
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path}: {exc}")
        return None


def validate() -> list[str]:
    errors: list[str] = []

    manifest = _read_json(PLUGIN_DIR / ".codex-plugin" / "plugin.json", errors)
    if isinstance(manifest, dict):
        for field in ("name", "version", "description"):
            if not manifest.get(field):
                errors.append(f"plugin.json missing required field: {field}")
        if "hooks" in manifest:
            errors.append(
                "plugin.json declares a 'hooks' field — this plugin is reporting-only, "
                "see docs/install-codex.md"
            )

    for skill in ("tokenwise-config", "tokenwise-report"):
        skill_path = PLUGIN_DIR / "skills" / skill / "SKILL.md"
        if not skill_path.is_file():
            errors.append(f"missing {skill_path}")

    if not (PLUGIN_DIR / "hooks" / "README.md").is_file():
        errors.append("missing plugins/codex/tokenwise/hooks/README.md")
    if (PLUGIN_DIR / "hooks" / "hooks.json").exists():
        errors.append(
            "plugins/codex/tokenwise/hooks/hooks.json exists — this plugin ships "
            "reporting-only, remove it or update docs/install-codex.md and this validator"
        )

    vendor_core = PLUGIN_DIR / "vendor" / "tokenwise_core"
    vendor_adapter = PLUGIN_DIR / "vendor" / "adapters" / "codex"
    if not vendor_core.is_dir():
        errors.append(f"missing {vendor_core} — run scripts/build.py")
    if not vendor_adapter.is_dir():
        errors.append(f"missing {vendor_adapter} — run scripts/build.py")

    marketplace = _read_json(REPO_ROOT / ".agents" / "plugins" / "marketplace.json", errors)
    if isinstance(marketplace, dict):
        paths = [
            p.get("source", {}).get("path")
            for p in marketplace.get("plugins", [])
            if isinstance(p, dict) and isinstance(p.get("source"), dict)
        ]
        if "./plugins/codex/tokenwise" not in paths:
            errors.append(
                "root .agents/plugins/marketplace.json does not list path "
                "'./plugins/codex/tokenwise'"
            )

    return errors


def main() -> int:
    errors = validate()
    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        return 1
    print("Codex plugin validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
