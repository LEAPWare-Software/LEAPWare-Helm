---
name: tokenwise-report
description: Run tokenwise's policy engine over a described action and report what it WOULD decide (Codex side, reporting-only — no enforcing hook ships here, see docs/install-codex.md).
---

# tokenwise-report (Codex)

The Codex plugin does not ship an enforcing hook (see
`docs/install-codex.md` for why). This skill is the substitute: given a
description of an action (e.g. a sub-task dispatch and its prompt), it runs
the same `tokenwise_core.engine.evaluate` used by the Claude Code plugin, via
`adapters/codex/hook_io.py`, and reports the decision in plain language
using `render_report`.

## Usage

1. Build a neutral event: `hook_event_name`, `tool_name`, and `tool_input`
   (at minimum a `prompt` key for a dispatch-shaped action).
2. Load the active policy the same way tokenwise-config does.
3. Run `adapters.codex.hook_io.parse_event`, then `tokenwise_core.engine.evaluate`,
   then `adapters.codex.hook_io.render_report`.
4. Present the report verbatim; do not soften a reported DENY into a
   suggestion — say plainly that this action would have been blocked under
   the Claude Code plugin's equivalent hook, and is not blocked here.
