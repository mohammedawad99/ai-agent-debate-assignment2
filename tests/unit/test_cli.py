"""Unit tests: thin CLI over the SDK (offline mock mode)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.cli.main import main
from agent_debate.orchestration.session import DebateSessionResult, RunStatus
from agent_debate.protocol.models import FinalJudgment


def _success(session_id: str = "x") -> DebateSessionResult:
    return DebateSessionResult(
        session_id=session_id,
        status=RunStatus.SUCCESS,
        final_judgment=FinalJudgment(
            session_id=session_id,
            winner_role="con",
            loser_role="pro",
            scores={},
            tie_break_used=True,
            tie_break_reason="configured_priority",
            reasoning="r",
            limitations="l",
            created_at="t",
        ),
    )


def test_mock_run_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["mock-run", "--turns-per-side", "1"])
    assert code == 0
    out = capsys.readouterr().out
    assert "OFFLINE MOCK MODE" in out
    assert "winner:" in out


def test_mock_run_writes_only_under_output_dir(tmp_path: Path) -> None:
    code = main(["mock-run", "--turns-per-side", "1", "--output-dir", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "transcript.jsonl").is_file()


def test_cli_delegates_to_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: dict[str, object] = {}

    def fake_run(
        *, session_id: str, turns_per_side: int, output_dir: object
    ) -> DebateSessionResult:
        calls["session_id"] = session_id
        calls["turns_per_side"] = turns_per_side
        return _success(session_id)

    monkeypatch.setattr("agent_debate.cli.main.run_mock_debate", fake_run)
    code = main(["mock-run", "--session-id", "abc", "--turns-per-side", "3"])
    assert code == 0
    assert calls == {"session_id": "abc", "turns_per_side": 3}


def test_failed_run_exits_nonzero(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(**_kwargs: object) -> DebateSessionResult:
        return DebateSessionResult(
            session_id="x", status=RunStatus.FAILED_PROTOCOL, errors=["WatchdogError: stalled"]
        )

    monkeypatch.setattr("agent_debate.cli.main.run_mock_debate", fake_run)
    assert main(["mock-run"]) == 1


def test_run_mock_mode_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["run", "--provider", "mock", "--search", "mock", "--turns-per-side", "1"])
    assert code == 0
    out = capsys.readouterr().out
    assert "MOCK MODE" in out
    assert "provider: mock | search: mock" in out


def test_run_real_mode_delegates_and_warns(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: dict[str, object] = {}

    def fake_run(*, provider: str, search: str, **_kwargs: object) -> DebateSessionResult:
        calls["provider"] = provider
        calls["search"] = search
        return _success()

    monkeypatch.setattr("agent_debate.cli.main.run_configured_debate", fake_run)
    code = main(["run", "--provider", "claude_cli", "--search", "ddgs"])
    assert code == 0
    assert calls == {"provider": "claude_cli", "search": "ddgs"}
    assert "REAL MODE" in capsys.readouterr().out


def test_run_default_judge_is_none(capsys: pytest.CaptureFixture[str]) -> None:
    code = main(["run", "--provider", "mock", "--search", "mock", "--turns-per-side", "1"])
    assert code == 0
    out = capsys.readouterr().out
    assert "judge: none" in out
    assert "WARNING" not in out


def test_run_judge_mock_exits_zero(capsys: pytest.CaptureFixture[str]) -> None:
    args = ["run", "--provider", "mock", "--search", "mock", "--judge-provider", "mock"]
    code = main([*args, "--turns-per-side", "1"])
    assert code == 0
    out = capsys.readouterr().out
    assert "judge: mock" in out
    assert "MOCK MODE" in out


def test_run_judge_claude_cli_warns_without_real_call(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    calls: dict[str, object] = {}

    def fake_run(*, judge_provider: str, **_kwargs: object) -> DebateSessionResult:
        calls["judge_provider"] = judge_provider
        return _success()

    monkeypatch.setattr("agent_debate.cli.main.run_configured_debate", fake_run)
    code = main(["run", "--provider", "mock", "--search", "mock", "--judge-provider", "claude_cli"])
    assert code == 0
    assert calls == {"judge_provider": "claude_cli"}
    out = capsys.readouterr().out
    assert "WARNING: judge-provider claude_cli" in out
    assert "REAL MODE" in out
