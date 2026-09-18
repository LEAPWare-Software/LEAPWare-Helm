# Sequenced plan as of 2026-09-18

Read `HANDOFF.md` first, then this file. Re-derive state with the
commands in `HANDOFF.md`'s "Re-derive state" section before acting on
anything below — this plan is the sequence of work, not a substitute for
current facts. Steps are ordered: step *n+1* does not start before step
*n* is done and proven.

## Step 0 — BLOCKED ON OWNER. Gates everything below.

Two questions in `docs/open-decisions.md` are unanswered: Q1 (how the
`codex-cto.json` review side gets satisfied) and Q2 (whether the
`classify_path` "other" dead zone is a bug or intended fail-closed
design). No agent may decide either. Exit criterion: the owner states
both routes. Q1 gates Q2, because the Q2 fix lives in `scripts/`, itself
a shared path.

## Step 1 — Unblock PRs #7 and #8. Depends on Q1.

Produce `reviews/7/claude-cto.json`, `reviews/7/codex-cto.json`,
`reviews/8/claude-cto.json`, `reviews/8/codex-cto.json` per the chosen
route, each `"verdict": "AGREE"`, `reviewer_agent` matching the filename,
and `reviewer_id` genuinely different from `commit_author_id` (see
`reviews/README.md`). PR #8 additionally needs Q2 settled: it touches
`.gitignore`, `tests/core/test_lwt_handoff.py` and
`tests/test_lwt_check_env_leak.py`, all of which classify as `other`.
Exit criterion: all 6 required `test` matrix jobs green on both PRs.
Merging is squash-via-merge-queue and is an OWNER action — no agent
merges or enables auto-merge.

## Step 2 — Close the lane dead zone. Depends on Q1 + Q2, only if Q2 chooses a fix.

Edit `classify_path` in `scripts/lwt_lanes.py` per the chosen option,
with tests covering root-level config files and non-lane `tests/` paths.
`scripts/` is shared, so this change needs its own dual-CTO review. The
write-time guard `scripts/lwt_check_lane_write.py` enforces the same
classification, so both must agree.

## Step 3 — Hosted-runner-only CI check. Owner directive 9. Depends on step 1.

A CI check that fails on any `runs-on` value that is not a GitHub-hosted
runner, scanning `.github/workflows/*.yml`. Prove it by breaking it on
purpose: temporarily point a job at a self-hosted runner, confirm the
check goes red, revert, confirm green. Record that in the proof. Touches
`scripts/` and `.github/`, both shared, so dual-CTO review applies.

## Step 4 — GitHub Apps `lwt-claude` and `lwt-codex`. Owner directive 12.

App creation is an owner-only click-through action; no agent can perform
it. The full runbook already exists at `docs/maintainers/github-apps.md`
and must be followed rather than rewritten.

**Owner performs:** create each App matching its manifest in
`.github/apps/` exactly — permissions `contents: write`,
`pull_requests: write`, `checks: read`, `metadata: read`, no
organization permissions, webhook inactive, not public; download the
private key at creation time, which GitHub shows exactly once and which
is unrecoverable afterward; install each App on
`LEAPWare-Software/LEAPWare-TokenWise` ONLY, never "all repositories";
note the App ID and Installation ID for each; store both private keys in
the org's existing secrets manager — never the repo, never a `.env` even
locally, never pasted into a chat transcript.

**Agent performs afterward:** record the App IDs and Installation IDs in
`docs/maintainers/github-apps.md` via PR. IDs are not secrets; private
keys must never appear in the repo in any form. That file is a shared
path, so dual-CTO review applies.

**Verification:** each App installed on exactly one repository;
permission set matches the manifest exactly; no org-level permission
granted. **Security gate:** if a key is ever committed, logged or pasted
anywhere, revoke it immediately from the App's settings page and
generate a replacement — revocation is instant and does not require
deleting the App.

## Step 5 — Full 1.0.0 plan in plan mode. Owner directive 13. Depends on steps 1-4.

Each CLI works in its own lane. Build the complete requirements package
per `docs/requirements/approach.md`, seeded by
`docs/requirements/owner-directives.md`, with every functional
requirement traced to a numbered directive. Present to the owner for
approval BEFORE building anything.

## Standing rules

Proof of Completion per `docs/handoff-protocol.md` — committed, pushed,
CI green, proof record, announced as `LWT - Alert: <id> DONE ...`. No
agent merges a PR, enables auto-merge, or changes repo settings or
rulesets. Python 3.10+ standard library only in `core/`, `adapters/` and
shipped plugin scripts. Worktrees only under `<repo>/.worktrees/<branch>`.
Write a handoff before ending any session, at any rate-limit or context
warning, and after each deliverable lands.
