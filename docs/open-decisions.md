# Open decisions

Durable analysis behind the current PR #7 / PR #8 blocker. Volatile state
(current SHAs, open PR numbers, CI run status) belongs in `HANDOFF.md`'s
generated block, not here — this file holds the reasoning that doesn't
change from commit to commit.

## Root cause A — missing dual-CTO review records

`scripts/lwt_lanes.py` (`check_lanes`, ~line 182) requires BOTH
`reviews/<pr>/claude-cto.json` and `reviews/<pr>/codex-cto.json`, each
`"verdict": "AGREE"`, for any agent-trailered commit touching a shared
path. Enforced for PR numbers greater than 5. Neither file exists for #7
or #8. `reviews/README.md` also forbids `reviewer_id == commit_author_id`,
so the author of a commit can never review it — a Claude session cannot
produce the codex half on its own.

Verbatim CI failures (evidence, both PRs, `lwt-lanes` step):

```
FAIL: 65201f3aed2d (LWT-Agent: claude): touches '.gitignore', outside the claude lane and not a shared path
FAIL: 65201f3aed2d (LWT-Agent: claude): touches 'tests/core/test_lwt_handoff.py', outside the claude lane and not a shared path
FAIL: 65201f3aed2d (LWT-Agent: claude): touches 'tests/test_lwt_check_env_leak.py', outside the claude lane and not a shared path
FAIL: 65201f3aed2d: missing required review reviews/8/claude-cto.json
FAIL: 65201f3aed2d: missing required review reviews/8/codex-cto.json
FAIL: e8eb4e1ff655: missing required review reviews/7/claude-cto.json
FAIL: e8eb4e1ff655: missing required review reviews/7/codex-cto.json
```

## Root cause B — the `other` dead zone (unresolved design question)

`classify_path()` (`scripts/lwt_lanes.py`, ~lines 62-84) returns one of
`claude` / `codex` / `shared` / `other`. `check_lanes` rejects any file
that is neither `shared` nor the commit's own agent lane — so **`other`
is writable by no agent at all.** It silently captures `.gitignore`,
`pyproject.toml`, `CHANGELOG.md`, `LICENSE`, and every `tests/` file not
under a `claude/`/`codex/` directory and not matching `*_claude_*` /
`*_codex_*`. Only an `LWT-Agent: human` commit can touch them.

This is enforced in two places, not just CI: `scripts/lwt_lanes.py`
(`check_lanes`) is the CI-time gate, and `scripts/lwt_check_lane_write.py`
is a local write-time guard that refuses the write before it ever reaches
a commit. Confirmed empirically 2026-09-18: an attempt to write a
root-level file was refused by the write-time guard with "claude may not
write outside its lane or shared paths."

Whether the dead zone is a bug or intended fail-closed design is an
OWNER DECISION. It has been asked and is **NOT yet answered.**

## Open questions — asked, NOT YET ANSWERED by the owner

**Q1 — how to satisfy the codex-cto review side?**
  (a) Run a Codex session in this repo to write the `codex-cto.json`
      records after a genuine review. Preserves directive 5 as designed.
  (b) Owner commits with an `LWT-Agent: human` trailer, which
      `check_lanes` skips entirely. Fast; bypasses the adversarial review.
  (c) Widen the bootstrap exception so the lane-model fix can land first.

**Q2 — how to close the `other` dead zone?**
  (a) Classify root config + non-lane `tests/` as `shared` — reachable by
      either CLI but only under dual review.
  (b) Keep `other` untouchable on purpose; those paths become owner-only.
  (c) Make unclassified paths default to `shared`.

Both answers change the work materially. The fix for Q2 lives in
`scripts/` — itself a shared path — so it is review-gated too. That
means Q1 must be settled before Q2's fix can land: a bootstrap loop.
