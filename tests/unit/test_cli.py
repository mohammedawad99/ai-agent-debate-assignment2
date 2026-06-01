"""Unit tests: thin CLI over the SDK (offline mock mode)."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.cli.main import main
from agent_debate.orchestration.session import DebateSessionResult, RunStatus
from agent_debate.protocol.models import FinalJudgment


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
        judgment = FinalJudgment(
            session_id=session_id,
            winner_role="con",
            loser_role="pro",
            scores={},
            tie_break_used=True,
            tie_break_reason="configured_priority",
            reasoning="r",
            limitations="l",
            created_at="t",
        )
        return DebateSessionResult(
            session_id=session_id, status=RunStatus.SUCCESS, final_judgment=judgment
        )

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
