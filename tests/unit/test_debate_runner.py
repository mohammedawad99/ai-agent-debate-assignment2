"""Unit tests: DebateRunner offline orchestration (mocks only, deterministic)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.agents.debate_agent import ConAgent, ProAgent
from agent_debate.agents.judge import JudgeAgent
from agent_debate.orchestration.runner import DebateRunner
from agent_debate.orchestration.watchdog import Watchdog
from agent_debate.providers.mock_provider import MockProvider
from agent_debate.quality.gatekeeper import Gatekeeper
from agent_debate.results.cost_tracker import CostTracker
from agent_debate.results.scoring import JudgeError
from agent_debate.search.mock_search import MockSearchTool

VALID_JUDGMENT = (
    '{"winner_role": "pro", "loser_role": "con", "reasoning": "Pro was clearer.",'
    ' "scores": {"pro": {"clarity": 5}, "con": {"clarity": 3}}}'
)

CLEAN = "AI coding agents help students learn faster."
COLLAPSE = "I agree with the opponent completely."


def make_runner(pro_r, con_r, *, pro_timeout=False, watchdog=None, judge_provider=None):  # noqa: ANN001
    cost = CostTracker()
    search = MockSearchTool()
    pro = ProAgent(MockProvider(pro_r, raise_timeout=pro_timeout), search)
    con = ConAgent(MockProvider(con_r), search)
    gate = Gatekeeper(cost, max_provider_calls=100, max_search_calls=100, max_retries=100)
    return DebateRunner(
        pro,
        con,
        JudgeAgent(160, judge_provider=judge_provider),
        cost_tracker=cost,
        gatekeeper=gate,
        watchdog=watchdog or Watchdog(),
    )


def _run(runner, turns=2, output_dir=None):  # noqa: ANN001
    return runner.run(
        session_id="s1",
        turns_per_side=turns,
        retry_cap=2,
        tie_break_priority=["con", "pro"],
        output_dir=output_dir,
    )


def test_success_returns_one_winner() -> None:
    result = _run(make_runner([CLEAN, CLEAN], [CLEAN, CLEAN]))
    assert result.is_successful
    judgment = result.final_judgment
    assert judgment is not None
    assert judgment.winner_role in {"pro", "con"}
    assert judgment.loser_role != judgment.winner_role


def test_provider_backed_judge_via_runner() -> None:
    verdict = '{"winner_role": "con", "loser_role": "pro", "reasoning": "Con was sharper."}'
    runner = make_runner([CLEAN], [CLEAN], judge_provider=MockProvider([verdict]))
    result = _run(runner, turns=1)
    assert result.is_successful
    assert result.final_judgment is not None
    assert result.final_judgment.winner_role == "con"
    assert "Provider-backed" in result.final_judgment.limitations


def test_judge_deterministic_is_default() -> None:
    judgment = JudgeAgent(160).judge("s1", ["con", "pro"])
    assert judgment.winner_role in {"pro", "con"}
    assert judgment.loser_role != judgment.winner_role
    assert "Deterministic offline scoring" in judgment.limitations


def test_judge_provider_backed_valid_judgment() -> None:
    judge = JudgeAgent(160, judge_provider=MockProvider([VALID_JUDGMENT]))
    judgment = judge.judge("s1", ["con", "pro"], messages=[{"sender_role": "pro", "argument": "x"}])
    assert judgment.winner_role == "pro"
    assert judgment.loser_role == "con"
    assert judgment.reasoning == "Pro was clearer."
    assert "Provider-backed" in judgment.limitations


@pytest.mark.parametrize(
    "verdict",
    [
        "{not json",
        '{"winner_role": "maybe", "loser_role": "con", "reasoning": "x"}',
        '{"winner_role": "pro", "loser_role": "pro", "reasoning": "x"}',
        '{"winner_role": "pro", "loser_role": "con", "reasoning": ""}',
    ],
)
def test_judge_provider_backed_invalid_rejected(verdict: str) -> None:
    judge = JudgeAgent(160, judge_provider=MockProvider([verdict]))
    with pytest.raises(JudgeError):
        judge.judge("s1", ["con", "pro"], messages=[])


def test_invalid_first_response_regenerates() -> None:
    result = _run(make_runner([COLLAPSE, CLEAN], [CLEAN]), turns=1)
    assert result.is_successful
    assert result.cost_summary is not None
    assert result.cost_summary["retry_count"] >= 1


def test_retry_exhaustion_fails() -> None:
    result = _run(make_runner([COLLAPSE, COLLAPSE, COLLAPSE], [CLEAN]), turns=1)
    assert not result.is_successful
    assert result.errors


def test_provider_timeout_fails() -> None:
    result = _run(make_runner([CLEAN], [CLEAN], pro_timeout=True), turns=1)
    assert not result.is_successful
    assert any("Timeout" in error for error in result.errors)


def test_watchdog_failure_fails() -> None:
    runner = make_runner([CLEAN, CLEAN], [CLEAN, CLEAN], watchdog=Watchdog(max_stalled_checks=0))
    result = _run(runner)
    assert not result.is_successful
    assert any("stalled" in error.lower() for error in result.errors)


def test_artifacts_written_only_under_tmp_path(tmp_path: Path) -> None:
    _run(make_runner([CLEAN, CLEAN], [CLEAN, CLEAN]), output_dir=tmp_path)
    assert (tmp_path / "transcript.jsonl").is_file()
    assert (tmp_path / "transcript.md").is_file()
    assert (tmp_path / "cost_report.json").is_file()
