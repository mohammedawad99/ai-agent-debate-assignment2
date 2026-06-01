"""Unit tests: DebateSessionResult / RunStatus."""

from __future__ import annotations

from agent_debate.orchestration.session import DebateSessionResult, RunStatus


def test_success_result_is_successful() -> None:
    result = DebateSessionResult(session_id="s1", status=RunStatus.SUCCESS)
    assert result.is_successful is True


def test_failed_result_not_successful() -> None:
    result = DebateSessionResult(session_id="s1", status=RunStatus.FAILED_PROTOCOL)
    assert result.is_successful is False


def test_failed_result_preserves_context() -> None:
    result = DebateSessionResult(
        session_id="s1",
        status=RunStatus.FAILED_PROTOCOL,
        messages=[{"turn_index": 0}],
        errors=["ProviderTimeoutError: boom"],
        cost_summary={"provider_call_count": 1},
    )
    assert result.messages
    assert result.errors
    assert result.cost_summary is not None
    assert not result.is_successful
