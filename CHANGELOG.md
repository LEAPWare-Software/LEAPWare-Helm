# Changelog

All notable changes to this project are documented in this file. The format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning
follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Initial scaffold: `tokenwise_core` pure engine (`Event` -> `Decision`), the
  `budget_line` walking-skeleton rule, the Claude Code adapter and plugin
  (enforcing `PreToolUse` hook), the Codex adapter and plugin
  (reporting-only — see `docs/install-codex.md`), `scripts/build.py`
  (vendoring), both plugin validators, and the unit / adapter / conformance
  test suite.
