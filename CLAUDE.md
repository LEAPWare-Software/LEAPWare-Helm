# CLAUDE.md — contributor instructions for Claude Code

These are instructions for building this repo, not runtime config. The
lwh plugin itself must never read or depend on this file at runtime.

- Read `HANDOFF.md` first, every session.
- Your lane: `plugins/claude/`, `adapters/claude/`, `tests/**/claude/`.
  Codex's lane (`plugins/codex/`, `adapters/codex/`, `tests/**/codex/`) is
  not yours to edit.
- A shared path (`core/`, `docs/`, root config) needs adversarial review
  by the CTO role on *both* CLIs, in agreement, before it lands.
- Every deliverable needs a Proof of Completion: committed, pushed, CI
  green, announced as `LWH - Alert: <id> DONE ...`. See
  `docs/handoff-protocol.md`.
