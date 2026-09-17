#!/usr/bin/env python3
"""Build zip release artifacts for both plugins.

Runs `scripts/lwt_build.py` (to refresh vendor/), then both validators, then
zips `plugins/claude/lwt/` and `plugins/codex/lwt/` into
`dist/lwt-claude-<version>.zip` and `dist/lwt-codex-<version>.zip`, where
`<version>` is read from each plugin's own manifest. Refuses to produce an
artifact if a validator fails. Stdlib only.

Usage: python scripts/lwt_release.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = REPO_ROOT / "dist"


def _run(args: list[str]) -> int:
    print(f"$ {' '.join(args)}")
    return subprocess.call([sys.executable, *args], cwd=REPO_ROOT)


def _zip_dir(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(src.rglob("*")):
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if path.is_file():
                zf.write(path, path.relative_to(src.parent))


def main() -> int:
    if _run(["scripts/lwt_build.py"]) != 0:
        print("build.py failed")
        return 1
    if _run(["scripts/lwt_validate_claude_plugin.py"]) != 0:
        print("Claude plugin validation failed — refusing to release")
        return 1
    if _run(["scripts/lwt_validate_codex_plugin.py"]) != 0:
        print("Codex plugin validation failed — refusing to release")
        return 1

    claude_manifest = json.loads(
        (REPO_ROOT / "plugins" / "claude" / "lwt" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    codex_manifest = json.loads(
        (REPO_ROOT / "plugins" / "codex" / "lwt" / ".codex-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )

    claude_version = claude_manifest["version"]
    codex_version = codex_manifest["version"]

    _zip_dir(
        REPO_ROOT / "plugins" / "claude" / "lwt",
        DIST_DIR / f"lwt-claude-{claude_version}.zip",
    )
    _zip_dir(
        REPO_ROOT / "plugins" / "codex" / "lwt",
        DIST_DIR / f"lwt-codex-{codex_version}.zip",
    )
    print(f"wrote {DIST_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
