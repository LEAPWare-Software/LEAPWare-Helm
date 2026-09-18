# HANDOFF

One page. Read this before any other file when starting a new session on
this repo. See `docs/handoff-protocol.md` for the full protocol this file
follows.

## Start of session

- [ ] Read this whole file.
- [ ] Run the commands in "Re-derive state" below — trust their output,
      not this file's prose (except the "In flight" narrative, which is
      the current plan of record).
- [ ] Confirm which CLI you are (Claude Code or Codex) and work only in
      your lane: see `CLAUDE.md` / `AGENTS.md`.
- [ ] If nothing below is in flight, ENTER PLAN MODE and pick up the next
      unchecked step.

## In flight

The plan, in order. Do not skip a step; do not start step *n+1* before
step *n* is done and proven.

1. Work from this repo only. Clone fresh on any machine; no dependence on
   the local environment. **SACRED.**
2. DONE — bootstrap PR #5 (branch `lwt-bootstrap`, containing D0, D1, D2 —
   replaced the earlier #4/`fix/lwt-d0-vendor-committed`, whose history
   was cleaned by owner decision) merged through the merge queue, sha
   `ba4f667d37c55f4c809f843ac70d730e9b961e9a`. The repo is now worked
   from its own Claude session opened in its own folder.
3. NOT STARTED — implement the hosted-runner-only CI check (directive 9
   in `docs/requirements/owner-directives.md`): a CI check that fails on
   any `runs-on` value other than a GitHub-hosted runner, proven by
   breaking it on purpose. This is the next real deliverable, but it is
   blocked behind two owner decisions that are asked and not yet
   answered — see `docs/open-decisions.md` (missing dual-CTO review
   records, and the `other`-path dead zone in `scripts/lwt_lanes.py`).
4. Create the two GitHub Apps (`lwt-claude`, `lwt-codex`) from the
   committed manifests in `.github/apps/`, using a browser-enabled
   session. Install each on this repo only. Store each private key in the
   owner's secrets manager, never in the repo. Record App ids in
   `docs/maintainers/github-apps.md` via PR.
5. ENTER PLAN MODE (each CLI in its own lane) and build the full plan to
   ship lwt 1.0.0, starting with the complete requirements package per
   `docs/requirements/approach.md`, seeded by
   `docs/requirements/owner-directives.md`. Present the plan to the owner
   for approval before building.
6. Every deliverable follows `docs/handoff-protocol.md`: proof record,
   pushed, CI green, alert line `LWT - Alert: <id> DONE ...`.

<!-- lwt-handoff:begin -->

Generated: 2026-09-18 17:55 UTC
main SHA: 07b055e74e9815d1ef603ddc6ae060558fc80615
CLI: claude
Session: docs-session-handoff-durable

Open PRs:
#8 fix(privacy): genericize hard-coded private-name needles (fix/genericize-private-names)
#7 docs(handoff): bootstrap DONE, hosted-runner-only + worktree-location directives (docs/session-handoff)

Deliverable proof state (from proof/):
- LWT-D0: PROVEN (commit a6aa3b74b356e9dd92052d9aa6c66409afaa4ada)
- LWT-D1: PROVEN (commit a6aa3b74b356e9dd92052d9aa6c66409afaa4ada)
- LWT-D2: PROVEN (commit a6aa3b74b356e9dd92052d9aa6c66409afaa4ada)

<!-- lwt-handoff:end -->

## Re-derive state

```
git fetch origin
git status
git log --oneline -10
gh pr list --state open
gh run list --limit 10
gh api repos/LEAPWare-Software/LEAPWare-TokenWise/rulesets
```

`gh` and `git` are the state of record. This file's "In flight" list is
the plan; the commands above are the facts.

## Hard rules

- Python 3.10+ standard library only, everywhere in `core/`, `adapters/`,
  and any shipped plugin script.
- The plugin never reads or depends on `CLAUDE.md` or `AGENTS.md` at
  runtime — those are contributor-only docs.
- Model/agent-type routing, budget lines, and review-tier rules are
  enforced mechanically by the plugin (allow/warn/deny), never by trust.
- No repo settings change, no merge, no force-push, no history rewrite
  without the owner.
- One GitHub App per CLI; no shared credential.

## Traps

- `gh pr list --jq` without `--json` exits 1; use `--json` + `--template`
  or `--jq` with `gh api`.
- A linked worktree's `.git` is a file, not a directory.
- `git diff` omits untracked files; check
  `git ls-files --others --exclude-standard` too.
- Squash-merge only happens through the merge queue — never merge locally
  and push to `main`.
- `scripts/lwt_handoff.py --write` requires `gh` auth for the PR list; it
  degrades to "(unavailable)" rather than failing when `gh` is missing or
  unauthenticated, so a green `--check` does not by itself prove the PR
  list is current — re-read the "Generated" timestamp.
- Root-level files and non-lane `tests/` paths classify as `other` in
  `scripts/lwt_lanes.py` and no agent lane may write them — enforced at
  write time by `scripts/lwt_check_lane_write.py`, not only in CI. See
  `docs/open-decisions.md`.
