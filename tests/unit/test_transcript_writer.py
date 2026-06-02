"""Unit tests: TranscriptWriter writes only under the given output dir (tmp_path)."""

from __future__ import annotations

import json
from pathlib import Path

from agent_debate.orchestration.session import DebateSessionResult, RunStatus
from agent_debate.protocol.models import FinalJudgment
from agent_debate.results.scoring import build_score
from agent_debate.results.transcript_writer import TranscriptWriter

MESSAGES = [
    {"turn_index": 0, "sender_role": "pro", "argument": "Opening point."},
    {"turn_index": 1, "sender_role": "con", "argument": "Rebuttal point."},
]


def _success(**over: object) -> DebateSessionResult:
    base = {
        "session_id": "s1",
        "status": RunStatus.SUCCESS,
        "messages": MESSAGES,
        "cost_summary": {"provider_call_count": 2},
    }
    base.update(over)
    return DebateSessionResult(**base)  # type: ignore[arg-type]


def _judgment() -> FinalJudgment:
    return FinalJudgment(
        session_id="s1",
        winner_role="con",
        loser_role="pro",
        scores={"pro": build_score(4, 4, 4, 4, 4, 4), "con": build_score(5, 5, 5, 5, 5, 5)},
        tie_break_used=False,
        tie_break_reason=None,
        reasoning="Con was more responsive.",
        limitations="Provider-backed final judgment.",
        created_at="t",
    )


def test_writes_jsonl_md_and_cost(tmp_path: Path) -> None:
    TranscriptWriter().write(_success(), tmp_path)
    assert (tmp_path / "transcript.jsonl").is_file()
    assert (tmp_path / "transcript.md").is_file()
    assert (tmp_path / "cost_report.json").is_file()
    assert not (tmp_path / "error_report.md").exists()


def test_jsonl_has_one_line_per_message(tmp_path: Path) -> None:
    TranscriptWriter().write(_success(), tmp_path)
    lines = (tmp_path / "transcript.jsonl").read_text().strip().splitlines()
    assert len(lines) == len(MESSAGES)


def test_error_report_written_when_errors(tmp_path: Path) -> None:
    result = _success(status=RunStatus.FAILED_PROTOCOL, errors=["WatchdogError: stalled"])
    TranscriptWriter().write(result, tmp_path)
    assert (tmp_path / "error_report.md").is_file()
    assert "stalled" in (tmp_path / "error_report.md").read_text()


def test_success_with_judgment_writes_final_judgment_json(tmp_path: Path) -> None:
    TranscriptWriter().write(_success(final_judgment=_judgment()), tmp_path)
    data = json.loads((tmp_path / "final_judgment.json").read_text())
    assert data["winner_role"] == "con" and data["loser_role"] == "pro"
    assert data["reasoning"] == "Con was more responsive."
    assert "limitations" in data
    assert data["scores"]["con"]["total"] == 30


def test_transcript_md_includes_judge_reasoning_and_winner(tmp_path: Path) -> None:
    TranscriptWriter().write(_success(final_judgment=_judgment()), tmp_path)
    md = (tmp_path / "transcript.md").read_text()
    assert "## Final Judgment" in md
    assert "Winner: con" in md
    assert "Con was more responsive." in md


def test_failed_run_writes_no_final_judgment_json(tmp_path: Path) -> None:
    result = _success(status=RunStatus.FAILED_PROTOCOL, errors=["JudgeError: bad"])
    TranscriptWriter().write(result, tmp_path)
    assert not (tmp_path / "final_judgment.json").exists()
    assert (tmp_path / "error_report.md").is_file()
    # transcript.jsonl still streams the accepted child turns.
    lines = (tmp_path / "transcript.jsonl").read_text().strip().splitlines()
    assert len(lines) == len(MESSAGES)
