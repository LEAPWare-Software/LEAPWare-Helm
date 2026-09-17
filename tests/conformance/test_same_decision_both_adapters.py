"""Conformance test: the same neutral event yields the same Decision through
both adapters' `parse_event`, for every hook shape Codex's parser also
supports.

This is the test the walking-skeleton pipeline is built to satisfy: helm's
engine must not silently branch on which host produced the event. Where
Codex's fixture set has no equivalent of a Claude-only field (e.g.
`transcript_path`), the test only asserts on the fields both adapters
populate — `hook_event`, `tool_name`, `prompt` — since those are the only
fields `budget_line` (or any rule in the registry) reads.
"""

import json
from pathlib import Path

from adapters.claude.hook_io import parse_event as claude_parse_event
from adapters.codex.hook_io import parse_event as codex_parse_event
from lwh_core.config import Policy, RuleConfig, RuleMode
from lwh_core.engine import evaluate

CLAUDE_FIXTURES = Path(__file__).parent.parent / "adapters" / "fixtures" / "claude"
CODEX_FIXTURES = Path(__file__).parent.parent / "adapters" / "fixtures" / "codex"

# (claude fixture name, codex fixture name) pairs describing the SAME
# logical event in each host's native shape.
PAIRED_FIXTURES = [
    ("pretooluse_agent_no_budget.json", "pretooluse_agent_no_budget.json"),
    ("pretooluse_agent_with_budget.json", "pretooluse_agent_with_budget.json"),
]

DENY_POLICY = Policy(rules={"budget_line": RuleConfig(mode=RuleMode.DENY)})


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_paired_fixtures_produce_identical_decisions():
    for claude_name, codex_name in PAIRED_FIXTURES:
        claude_event = claude_parse_event(_load(CLAUDE_FIXTURES / claude_name))
        codex_event = codex_parse_event(_load(CODEX_FIXTURES / codex_name))

        assert claude_event.hook_event == codex_event.hook_event
        assert claude_event.tool_name == codex_event.tool_name
        assert claude_event.prompt == codex_event.prompt

        claude_decision = evaluate(claude_event, DENY_POLICY)
        codex_decision = evaluate(codex_event, DENY_POLICY)

        assert claude_decision.permit == codex_decision.permit
        assert claude_decision.deny_reason == codex_decision.deny_reason
        assert [f.rule_id for f in claude_decision.findings] == [
            f.rule_id for f in codex_decision.findings
        ]
