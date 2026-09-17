# Installing tokenwise on Codex CLI

**This plugin ships reporting-only. It registers no enforcing hook.** It
installs `skills/tokenwise-config` and `skills/tokenwise-report`, both backed by the
same `tokenwise_core` engine and policy format the Claude Code plugin uses, via
`adapters/codex/hook_io.py`.

## Why reporting-only — the recon this decision rests on

The owner's standing instruction for this project: *"if Codex plugins
cannot register hooks, the Codex plugin ships reporting-only (skills +
ledger), and says so plainly in docs."* This section is that plain
statement, with sources.

### What Codex CLI hook support looks like today (checked September 2026)

`codex` is not installed on the machine this scaffold was built on
(`which codex` / `codex --help` both failed), so this could not be verified
against a running CLI. Two web sources were checked instead, and they did
not fully agree:

**A general web search** returned a summary describing Codex hook support
as: added via PR
[`openai/codex#19705`](https://github.com/openai/codex/pull/19705)
("Discover hooks bundled with plugins"); gated behind a `plugin_hooks`
feature flag; **experimental, disabled by default, and "not available on
Windows"** per that summary's characterization of the underlying hooks
feature (first shipped v0.114, March 2026). It also states: *"Installing or
enabling a plugin doesn't automatically trust its hooks; Codex skips
plugin-bundled hooks until you review and trust the current hook
definition. ... Use `/hooks` in the CLI to inspect hook sources, review new
or changed hooks, trust hooks, or disable individual non-managed hooks."*
Related: [`openai/codex#16430`](https://github.com/openai/codex/issues/16430)
documents an earlier gap where plugin-local `hooks/hooks.json` was
advertised but not actually loaded by the runtime, since fixed by the PR
above.

**A direct fetch of the canonical docs page**
(`https://developers.openai.com/codex/hooks`, which 308-redirects to
`https://learn.chatgpt.com/docs/hooks`) returned a **different picture**:
hooks (canonical flag `hooks`, with `codex_hooks` kept as a deprecated
alias) are **"enabled by default"**, and the page states the feature "works
on Windows" with platform-specific overrides (`commandWindows`,
`windows_managed_dir`) for managed hooks. It also confirms plugin-bundled
hook discovery: *"Codex can load lifecycle hooks from that plugin alongside
user, project, and managed hooks."*

**These two readings disagree on default-enablement and Windows support,
and this project could not resolve the disagreement independently** (no
local `codex` binary, no second corroborating source checked). What both
readings agree on:

1. Plugin-bundled hooks are a genuinely new capability, not something
   stably available across the period this ecosystem has existed.
2. A plugin-bundled hook is **not auto-trusted** — a human must review and
   trust each hook definition via `/hooks` before Codex will run it, at
   least for "non-managed" hooks (which a locally-installed plugin's would
   be). That is fundamentally different from a Claude Code plugin's hook,
   which runs on install with no separate per-hook trust step.
3. **The exact `plugin.json` manifest field shape for declaring hooks was
   not found in either source.** A direct fetch of
   `https://developers.openai.com/codex/plugins` (redirecting to
   `https://learn.chatgpt.com/docs/plugins`) explicitly could not locate a
   documented schema for it.

### The decision this recon supports

Given (1) a mandatory manual per-hook trust step that defeats "mechanical,
no-prompting enforcement" as a design goal, (2) an unresolved and
undocumented manifest shape, and (3) conflicting evidence on default
platform support — this project ships **no `hooks/hooks.json`** for Codex.
See `plugins/codex/tokenwise/hooks/README.md` for the same reasoning kept next
to the empty directory it explains, and `scripts/validate_codex_plugin.py`,
which actively fails if a `hooks/hooks.json` is ever added without this
decision being revisited.

### Sources checked

- https://github.com/openai/codex/pull/19705
- https://github.com/openai/codex/issues/16430
- https://developers.openai.com/codex/hooks (redirects to
  https://learn.chatgpt.com/docs/hooks)
- https://developers.openai.com/codex/plugins (redirects to
  https://learn.chatgpt.com/docs/plugins)

## What IS installed

- `skills/tokenwise-config/SKILL.md` — read/edit the active policy file (same
  format as Claude Code's, see `docs/policy.md`).
- `skills/tokenwise-report/SKILL.md` — run the same engine over a described
  action and report what it WOULD have decided, via
  `adapters/codex/hook_io.render_report`. This never blocks anything; it is
  Codex's substitute for the enforcing hook Claude Code gets.

## Revisiting this

If a future Codex release resolves the trust-gate friction and documents
the manifest shape, `adapters/codex/hook_io.py` should gain a
`render_decision` mirroring `adapters/claude/hook_io.py`'s, and
`plugins/codex/tokenwise/hooks/hooks.json` should be added — see the note at the
end of `plugins/codex/tokenwise/hooks/README.md`.
