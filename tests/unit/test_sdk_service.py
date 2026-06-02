"""Unit tests: SDK offline mock debate service."""

from __future__ import annotations

from pathlib import Path

from agent_debate.providers.mock_provider import MockProvider
from agent_debate.sdk.service import run_configured_debate, run_mock_debate
from agent_debate.search.mock_search import MockSearchTool


def test_returns_successful_result() -> None:
    result = run_mock_debate(turns_per_side=2)
    assert result.is_successful
    assert result.final_judgment is not None
    assert result.final_judgment.winner_role in {"pro", "con"}


def test_no_artifacts_without_output_dir(tmp_path: Path) -> None:
    run_mock_debate(turns_per_side=1)
    # An unrelated directory stays untouched when no output_dir is given.
    assert list(tmp_path.iterdir()) == []


def test_writes_artifacts_only_to_output_dir(tmp_path: Path) -> None:
    run_mock_debate(turns_per_side=1, output_dir=tmp_path)
    assert (tmp_path / "transcript.jsonl").is_file()
    assert (tmp_path / "transcript.md").is_file()
    assert (tmp_path / "cost_report.json").is_file()


def test_session_id_is_passed_through() -> None:
    result = run_mock_debate(session_id="custom-id", turns_per_side=1)
    assert result.session_id == "custom-id"


def test_configured_mock_run_succeeds() -> None:
    result = run_configured_debate(provider="mock", search="mock", turns_per_side=1)
    assert result.is_successful
    assert result.final_judgment is not None


def test_configured_run_accepts_overrides() -> None:
    result = run_configured_debate(
        provider="mock",
        search="mock",
        turns_per_side=1,
        pro_provider=MockProvider(["Pro point."]),
        con_provider=MockProvider(["Con point."]),
        search_tool=MockSearchTool(),
    )
    assert result.is_successful


_JUDGE_VERDICT = '{"winner_role": "pro", "loser_role": "con", "reasoning": "Pro clearer."}'


def test_judge_default_is_deterministic() -> None:
    result = run_configured_debate(provider="mock", search="mock", turns_per_side=1)
    assert result.final_judgment is not None
    assert "Deterministic offline scoring" in result.final_judgment.limitations


def test_judge_provider_override_uses_provider_backed() -> None:
    result = run_configured_debate(
        provider="mock",
        search="mock",
        turns_per_side=1,
        judge_provider_override=MockProvider([_JUDGE_VERDICT]),
    )
    assert result.final_judgment is not None
    assert result.final_judgment.winner_role == "pro"
    assert "Provider-backed" in result.final_judgment.limitations


def test_judge_provider_mock_uses_provider_backed() -> None:
    result = run_configured_debate(
        provider="mock", search="mock", judge_provider="mock", turns_per_side=1
    )
    assert result.final_judgment is not None
    assert result.final_judgment.winner_role in {"pro", "con"}
    assert "Provider-backed" in result.final_judgment.limitations
