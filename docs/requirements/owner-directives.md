# Owner directives (setup session, 2026-09-17)

Binding. These are the owner's own directives from the setup session that
created this repo, one numbered line each. Where the owner's wording is
known it is quoted; the requirements package in `approach.md` must trace
every functional requirement back to one of these.

1. Code name LWT; every command, skill, and user-facing entrypoint starts
   with `lwt`.
2. Token-optimization and model-routing policy is enforced **mechanically**
   by the plugin (allow/warn/deny), never by trust.
3. The plugin must not depend on any `CLAUDE.md` or `AGENTS.md` (local,
   project, or global). All policy lives in the plugin.
4. Both a Claude Code plugin and a Codex plugin. Codex supports hooks, so
   full enforcement on both; no reporting-only constraint.
5. Lanes: Codex works only on the Codex part, Claude only on the Claude
   part. Shared parts may be changed by either CLI only after the CTO/CIO
   role on **each** CLI adversarially checks and agrees; the owner is not
   in that loop.
6. Statusline: the plugin independently installs an LWT indicator in the
   statusline, GREEN when running and healthy, RED when not; it must not
   overwrite an existing statusline.
7. Proof of Completion on every deliverable; done = committed AND pushed
   with a proof record and green CI; every proven delivery is announced
   as `LWT - Alert:`.
8. **SACRED**: repo and tooling build, test and deploy
   environment-agnostic for both Codex and Claude; the owner builds and
   tests from different laptops/environments; there must NOT be ANY
   dependence on or tie-in to a local environment.
9. All CI runs in GitHub Actions on hosted runners; no local runners.
10. Open source, public: `github.com/LEAPWare-Software/LEAPWare-TokenWise`,
    Apache-2.0, commit identity `LEAPWare <leapware@outlook.com>`.
11. Runtime: Python 3.10+ standard library only.
12. Repository rulesets (no bypass), merge queue + auto-merge, squash
    merges only; one GitHub App per CLI (`lwt-claude`, `lwt-codex`).
13. A full handoff protocol lives in the repo; the next session runs from
    the repo and first builds, in plan mode, the full plan to ship 1.0.0.
14. Lean: LW-Watchtower became bloated; lwt must stay small, with a size
    budget as a requirement.
15. Candidate rules to specify (from the owner-reviewed table):
    model/agent-type routing per task class; BUDGET line required and
    within class cap; reviews start on the lowest tier, higher only after
    it fails; follow-up within 5 minutes uses SendMessage; one owner per
    issue, no mid-run reassignment; no thin parallel workers; worker
    report ≤40 lines; orchestrator reply length cap; grep before large
    reads; measured targets (start-up tokens, per PR, per review); budget
    overrun handling.
16. Out of scope for lwt: Proof of Completion CI enforcement for other
    repos (separate product).
17. LWT displays and manages the status-line usage segment (context %, 5-hour
    % with time to reset, 7-day % with reset date, e.g. `ctx 33%  5h 10%
    (2h16m)  7d 2% (09/24 1am)`) plus its own GREEN/RED health light, taken
    over from LW-Watchtower. It must stay short, work on any laptop for
    Claude and Codex, and keep producing the usage readings other tools rely
    on (the RUNWAY/LWR gate reads them) so nothing breaks during the move;
    Watchtower's display is removed only after LWT's is proven. LWR shows
    only its own short session tag.
