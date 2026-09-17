## Summary

<!-- What changed and why. -->

## Checklist

- [ ] `py -3.12 -m pytest -q` passes
- [ ] `py -3.12 scripts/build.py --check` passes (or `scripts/build.py` was
      run and the resulting `vendor/` diff is included, if this PR is
      expected to change it)
- [ ] `py -3.12 scripts/validate_claude_plugin.py` passes
- [ ] `py -3.12 scripts/validate_codex_plugin.py` passes
- [ ] No third-party runtime import added under `core/` or `adapters/`
- [ ] If a rule was added or changed: unit tests cover `off`/`warn`/`deny`
      and a non-applicable-event case, and `docs/rules/` was updated
