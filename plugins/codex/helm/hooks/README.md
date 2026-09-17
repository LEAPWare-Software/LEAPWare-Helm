# No hooks ship here — deliberately

This directory exists only to document their absence. The Claude Code
plugin (`plugins/claude/helm/hooks/hooks.json`) registers an enforcing
PreToolUse hook. This Codex plugin does not.

## Why

As of this scaffold (September 2026), Codex CLI hook support:

- Requires a user to review and trust each hook definition through `/hooks`
  before it can run — a hook cannot enforce silently the way a Claude Code
  plugin hook does on install.
- Documents plugin-bundled hook discovery in prose ("Codex can also
  discover hooks bundled with enabled plugins... Plugin hooks use the same
  event schema as other hooks") but the exact `plugin.json` manifest field
  shape for declaring them was not found in the sources this project could
  reach.
- Reporting on the feature's platform/default-enablement status was
  inconsistent between an initial web search and the fetched canonical docs
  page (`https://developers.openai.com/codex/hooks`, redirecting to
  `https://learn.chatgpt.com/docs/hooks`) during this project's recon — see
  `docs/install-codex.md` for both readings, quoted, with the discrepancy
  stated rather than resolved by guessing.

Given the owner's standing decision ("if Codex plugins cannot register
hooks, the Codex plugin ships reporting-only"), and given the trust-gate
friction plus the unresolved manifest-shape question above, this plugin
ships reporting-only: `skills/helm-config` and `skills/helm-report`, both
backed by `adapters/codex/hook_io.py` and the same `helm_core` engine the
Claude Code plugin's hook uses.

## Revisiting this

If a future Codex release documents the plugin-hook manifest shape
concretely and removes (or this project can otherwise satisfy) the
per-session manual trust step, an enforcing `hooks/hooks.json` belongs in
this directory, and `adapters/codex/hook_io.py` should gain a
`render_decision` mirroring `adapters/claude/hook_io.py`'s.
