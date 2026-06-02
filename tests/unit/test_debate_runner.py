"""Unit tests: DebateRunner offline orchestration (mocks only, deterministic)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.agents.debate_agent import ConAgent, ProAgent
from agent_debate.agents.judge import JudgeAgent
from agent_debate.orchestration.runner import DebateRunner
from agent_debate.orchestration.watchdog import Watchdog
from agent_debate.providers.base import ProviderAdapter
from agent_debate.providers.mock_provider import MockProvider
from agent_debate.quality.gatekeeper import Gatekeeper
from agent_debate.results.cost_tracker import CostTracker
from agent_debate.results.scoring import JudgeError
from agent_debate.search.mock_search import MockSearchTool

VALID_JUDGMENT = (
    '{"winner_role": "pro", "loser_role": "con", "reasoning": "Pro was clearer.",'
    ' "scores": {"pro": {"clarity": 5}, "con": {"clarity": 3}}}'
)
BAD_VERDICTS = [
    "{not json",
    '{"winner_role": "maybe", "loser_role": "con", "reasoning": "x"}',
    '{"winner_role": "pro", "loser_role": "pro", "reasoning": "x"}',
    '{"winner_role": "pro", "loser_role": "con", "reasoning": ""}',
]
CLEAN = "AI coding agents help students learn faster."
COLLAPSE = "I agree with the opponent completely."
LIMIT = 160


class _Rec(ProviderAdapter):
    """Records every prompt; returns a fixed response sequence (last repeats)."""

    def __init__(self, responses: list[str]) -> None:
        self.responses, self.prompts, self._n = responses, [], 0

    @property
    def call_count(self) -> int:
        return self._n

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        self._n += 1
        return self.responses[min(self._n - 1, len(self.responses) - 1)]


def make_runner(pro_r, con_r, *, pro_timeout=False, watchdog=None, judge_provider=None, prov=None):  # noqa: ANN001, E501
    cost = CostTracker()
    search = MockSearchTool()
    pro = ProAgent(prov or MockProvider(pro_r, raise_timeout=pro_timeout), search, word_limit=LIMIT)
    con = ConAgent(MockProvider(con_r), search, word_limit=LIMIT)
    gate = Gatekeeper(cost, max_provider_calls=100, max_search_calls=100, max_retries=100)
    judge = JudgeAgent(LIMIT, judge_provider=judge_provider)
    return DebateRunner(
        pro, con, judge, cost_tracker=cost, gatekeeper=gate, watchdog=watchdog or Watchdog()
    )  # noqa: E501


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
    assert result.is_successful and result.final_judgment is not None
    j = result.final_judgment
    assert j.winner_role in {"pro", "con"} and j.loser_role != j.winner_role


def test_provider_backed_judge_via_runner() -> None:
    verdict = '{"winner_role": "con", "loser_role": "pro", "reasoning": "Con was sharper."}'
    result = _run(make_runner([CLEAN], [CLEAN], judge_provider=MockProvider([verdict])), turns=1)
    assert result.is_successful and result.final_judgment is not None
    assert result.final_judgment.winner_role == "con"
    assert "Provider-backed" in result.final_judgment.limitations


def test_judge_deterministic_is_default() -> None:
    j = JudgeAgent(160).judge("s1", ["con", "pro"])
    assert j.winner_role in {"pro", "con"} and j.loser_role != j.winner_role
    assert "Deterministic offline scoring" in j.limitations


def test_judge_provider_backed_valid_judgment() -> None:
    judge = JudgeAgent(160, judge_provider=MockProvider([VALID_JUDGMENT]))
    j = judge.judge("s1", ["con", "pro"], messages=[{"sender_role": "pro", "argument": "x"}])
    assert j.winner_role == "pro" and j.loser_role == "con"
    assert "Provider-backed" in j.limitations


@pytest.mark.parametrize("verdict", BAD_VERDICTS)
def test_judge_provider_backed_invalid_rejected(verdict: str) -> None:
    judge = JudgeAgent(160, judge_provider=MockProvider([verdict]))
    with pytest.raises(JudgeError):
        judge.judge("s1", ["con", "pro"], messages=[])


def test_runner_retry_sends_error_aware_regeneration_prompt() -> None:
    # Over-limit first attempt, then a short one: the runner must send a CHANGED, error-aware
    # prompt on retry (not the identical original), and recover to an accepted turn.
    pro = _Rec([" ".join(["w"] * (LIMIT + 40)), "Short valid pro argument."])
    runner = make_runner([], ["Short valid con argument."], prov=pro)
    result = _run(runner, turns=1)
    assert result.is_successful and pro.call_count == 2
    assert "Correction required" not in pro.prompts[0]  # first attempt is the normal prompt
    assert pro.prompts[0] != pro.prompts[1]
    assert all(t in pro.prompts[1] for t in ("word_limit_exceeded", str(LIMIT)))
    assert "JSON" not in pro.prompts[1]


def test_invalid_first_response_regenerates() -> None:
    result = _run(make_runner([COLLAPSE, CLEAN], [CLEAN]), turns=1)
    assert result.is_successful and result.cost_summary is not None
    assert result.cost_summary["retry_count"] >= 1


def test_retry_exhaustion_fails() -> None:
    result = _run(make_runner([COLLAPSE, COLLAPSE, COLLAPSE], [CLEAN]), turns=1)
    assert not result.is_successful and result.errors


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
