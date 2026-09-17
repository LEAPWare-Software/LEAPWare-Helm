# Architecture

## The pure core / impure edges split

```
                event (native JSON)
                      |
                      v
            +-------------------+
            |  adapter.parse_event()  |   adapters/claude/hook_io.py
            +-------------------+        adapters/codex/hook_io.py
                      |
                      v
                Event (neutral)          core/helm_core/events.py
                      |
                      v
            +-------------------+
            |  engine.evaluate()  |      core/helm_core/engine.py
            +-------------------+
                 /            \
        Policy (loaded)   RULES (registry)
     core/helm_core/config.py   core/helm_core/rules/__init__.py
                      |
                      v
                Decision (neutral)       core/helm_core/engine.py
                      |
                      v
            +----------------------+
            | adapter.render_*()   |     adapters/claude/hook_io.py: render_decision
            +----------------------+     adapters/codex/hook_io.py: render_report
                      |
                      v
              host-native output
```

`core/helm_core` does **no I/O**: no file reads, no stdin, no environment
variables, no clock. Every function in it is `(data in) -> (data out)`.
This is what the mutation test in `tests/core/test_engine_mutation.py` and
the conformance test in `tests/conformance/` rely on: the same `Event`
through the same `Policy` always produces the same `Decision`, regardless of
which adapter built the `Event` or what will be done with the `Decision`.

Everything that touches the outside world — reading stdin, resolving a
policy file path, appending a ledger line, writing stdout, setting an exit
code — lives in an adapter or a plugin's `bin/` script
(`plugins/claude/helm/bin/helm_hook.py`).

## Why two adapters, one core

Claude Code and Codex CLI have different hook JSON shapes, different
manifest formats, and (per `docs/install-codex.md`) different levels of
hook support today. Rather than writing the `budget_line` rule twice, or
writing a Claude-specific engine, every rule is written once against the
neutral `Event`/`Decision` shapes, and each host gets a thin adapter that
translates its native format at the edges.

## The vendoring step

A Claude Code plugin (and a Codex plugin) is distributed as its own
self-contained directory — it cannot import a sibling package from outside
that directory at install time. `scripts/build.py` copies `core/helm_core`,
`core/policy`, and the matching `adapters/<host>` into
`plugins/<host>/helm/vendor/` before a plugin is installed or released.
`scripts/build.py --check` (run in CI) fails if a committed `vendor/`
directory — during local development, not committed per `.gitignore` — has
drifted from its source. Nobody should hand-edit anything under `vendor/`.

## Fail-open, everywhere

Three independent layers all fail open, each documented at its own layer
rather than assumed:

1. `helm_core.config.load_policy_dict`: a missing or malformed policy
   dict resolves every unmentioned or misconfigured rule to `off`. See
   `docs/policy.md#fail-open`.
2. `helm_core.engine.evaluate`: an exception raised inside a single rule is
   caught and downgraded to a `warn`-shaped finding rather than propagating
   or defaulting to `deny`.
3. `plugins/claude/helm/bin/helm_hook.py`: a policy file that cannot be
   read or parsed at all is treated as `None`, which layer 1 above then
   treats as an all-`off` policy. A ledger write failure is swallowed
   rather than blocking the decision from being returned.

The engine never turns "something went wrong" into "block the action" on
its own; only an explicit, successfully-loaded `deny`-mode rule blocks
anything.
