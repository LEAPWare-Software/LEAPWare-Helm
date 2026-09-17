---
name: helm-config
description: Read or edit helm's token-policy configuration for this session or project (Codex side, reporting-only — see docs/install-codex.md for why this plugin ships no enforcing hook).
---

# helm-config (Codex)

Identical policy format and file to the Claude Code plugin: see
`core/policy/schema.json` and `core/policy/default.json` in the helm
repository. This skill reads and edits that same file; it does not enforce
anything itself, because the Codex plugin ships reporting-only (see
`docs/install-codex.md`).

## Reading the active policy

1. Check `HELM_POLICY_PATH` in the environment; if set, that file is active.
2. Otherwise the vendored `core/policy/default.json` is active.
3. List every configured rule's id and mode plainly.

## Changing a rule's mode

1. Edit only the named rule's `mode` (and `options`, if any).
2. Validate the result against `core/policy/schema.json` before reporting
   the change as live.
3. Remind the user explicitly: on Codex, a `deny` mode is not currently
   enforced by a hook — see helm-report for how to see what WOULD have been
   denied.
