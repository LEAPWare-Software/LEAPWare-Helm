"""Tests for adapters/codex/hook_io.py (reporting-only) against fixtures."""

import json
from pathlib import Path

from adapters.codex.hook_io import parse_event, render_report
from helm_core.config import Policy, RuleConfig, RuleMode
from helm_core.engine import evaluate

FIXTURES = Path(__file__).parent / "fixtures" / "codex"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_parse_event_extracts_prompt():
    event = parse_event(_load("pretooluse_agent_no_budget.json"))
    assert event.tool_name == "Agent"
    assert event.prompt and "example_module" in event.prompt


def test_render_report_states_would_deny():
    policy = Policy(rules={"budget_line": RuleConfig(mode=RuleMode.DENY)})
    event = parse_event(_load("pretooluse_agent_no_budget.json"))
    decision = evaluate(event, policy)
    report = render_report(decision)
    assert "would DENY" in report
    assert "BUDGET" in report


def test_render_report_states_would_allow_with_budget_line():
    policy = Policy(rules={"budget_line": RuleConfig(mode=RuleMode.DENY)})
    event = parse_event(_load("pretooluse_agent_with_budget.json"))
    decision = evaluate(event, policy)
    report = render_report(decision)
    assert "would ALLOW" in report
