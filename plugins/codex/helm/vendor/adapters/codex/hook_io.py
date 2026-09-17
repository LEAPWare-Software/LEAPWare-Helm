"""Codex adapter: reporting-only, by deliberate decision. See docs/install-codex.md.

As of this scaffold (September 2026) Codex CLI hook support is new,
plugin-bundled hooks require the user to review and trust each hook
definition through `/hooks` before it runs, and the exact plugin.json
`hooks` field shape is not documented in the sources this project could
reach (see docs/install-codex.md for the exact URLs and quotes checked).
That is not a footing Helm ships a DENY-capable gate on: a hook a user must
manually trust per-session, in an undocumented manifest shape, cannot be the
mechanical policy layer this project promises.

So the Codex plugin ships two skills (helm-config, helm-report) and this
adapter, which can turn a neutral `Event` + `Decision` into a ledger line
and a human-readable report string — the same engine, the same rules, but
surfaced through a skill a user invokes rather than a hook that blocks
automatically. `parse_event` exists so the SAME neutral-event fixtures used
for the Claude adapter can be replayed here for the conformance test in
tests/conformance/: proof the engine's decision doesn't change by adapter,
even though only one adapter can currently act on a DENY.

If Codex hook support matures to where a plugin can register a PreToolUse-
equivalent gate without a manual per-session trust step, this module is
where that gate belongs, alongside `render_decision` mirroring
adapters/claude/hook_io.py's.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

from helm_core.config import Policy, load_policy_dict
from helm_core.engine import Decision
from helm_core.events import Event


def parse_event(raw: Mapping[str, Any]) -> Event:
    """Build a neutral `Event` from a Codex-shaped event dict.

    Codex does not ship a documented hook input schema this project could
    cite (see module docstring), so this parser accepts the same neutral
    field names the test fixtures under tests/adapters/fixtures/codex/ use:
    `hook_event_name`, `tool_name`, `tool_input`, `session_id`. This keeps
    the conformance test meaningful without asserting a wire format Codex
    has not published.
    """
    hook_event = str(raw.get("hook_event_name", ""))
    tool_name = raw.get("tool_name")
    tool_input = raw.get("tool_input")
    if not isinstance(tool_input, Mapping):
        tool_input = {}

    prompt: Optional[str] = None
    for key in ("prompt", "description"):
        value = tool_input.get(key)
        if isinstance(value, str):
            prompt = value
            break

    known = {"hook_event_name", "tool_name", "tool_input", "session_id", "transcript_path"}
    extra = {k: v for k, v in raw.items() if k not in known}

    return Event(
        hook_event=hook_event,
        tool_name=tool_name if isinstance(tool_name, str) else None,
        tool_input=tool_input,
        prompt=prompt,
        session_id=raw.get("session_id") if isinstance(raw.get("session_id"), str) else None,
        transcript_path=None,
        extra=extra,
    )


def render_report(decision: Decision) -> str:
    """Human-readable text for the helm-report skill. Reporting only — never blocks."""
    lines = []
    if decision.permit:
        lines.append("helm: would ALLOW under current policy.")
    else:
        lines.append(f"helm: would DENY under current policy — {decision.deny_reason}")
    for warning in decision.warnings:
        lines.append(f"helm: warning — {warning}")
    if not decision.findings:
        lines.append("helm: no rule had an opinion on this event.")
    return "\n".join(lines)


def load_policy(raw: Any) -> Policy:
    return load_policy_dict(raw)
