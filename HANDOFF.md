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
2. Bootstrap PR (branch `fix/lwh-d0-vendor-committed`, containing D0, D1,
   D2) is not yet merged — the setup session could not merge it. Enable
   auto-merge / add it to the merge queue (squash) once its required
   checks are green. The merge happens through GitHub's merge queue,
   never a local merge.
3. Create the two GitHub Apps (`lwh-claude`, `lwh-codex`) from the
   committed manifests in `.github/apps/`, using a browser-enabled
   session. Install each on this repo only. Store each private key in the
   owner's secrets manager, never in the repo. Record App ids in
   `docs/maintainers/github-apps.md` via PR.
4. ENTER PLAN MODE (each CLI in its own lane) and build the full plan to
   ship lwh 1.0.0, starting with the complete requirements package per
   `docs/requirements/approach.md`, seeded by
   `docs/requirements/owner-directives.md`. Present the plan to the owner
   for approval before building.
5. Every deliverable follows `docs/handoff-protocol.md`: proof record,
   pushed, CI green, alert line `LWH - Alert: <id> DONE ...`.

<!-- lwh-handoff:begin -->

Generated: 2026-09-17 13:32 UTC
main SHA: 6ac5c2b79fbd33bd8d43a59c5d256949022be7ab
CLI: claude
Session: lwh-d1b-20260917T133241Z

Open PRs:
#4 fix(build): commit vendor/ trees, pin line endings via .gitattributes (fix/lwh-d0-vendor-committed)
#3 chore(deps): Bump actions/checkout from 5 to 7 (dependabot/github_actions/actions/checkout-7)
#2 chore(deps): Bump actions/setup-python from 6 to 7 (dependabot/github_actions/actions/setup-python-7)
#1 chore(deps): Bump softprops/action-gh-release from 2 to 3 (dependabot/github_actions/softprops/action-gh-release-3)

Deliverable proof state (from proof/):
(none yet)

<!-- lwh-handoff:end -->

## Re-derive state

```
git fetch origin
git status
git log --oneline -10
gh pr list --state open
gh run list --limit 10
gh api repos/LEAPWare-Software/LEAPWare-Helm/rulesets
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
- `scripts/lwh_handoff.py --write` requires `gh` auth for the PR list; it
  degrades to "(unavailable)" rather than failing when `gh` is missing or
  unauthenticated, so a green `--check` does not by itself prove the PR
  list is current — re-read the "Generated" timestamp.
