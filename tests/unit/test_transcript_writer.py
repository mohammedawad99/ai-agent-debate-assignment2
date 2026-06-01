"""Unit tests: TranscriptWriter writes only under the given output dir (tmp_path)."""

from __future__ import annotations

from pathlib import Path

from agent_debate.orchestration.session import DebateSessionResult, RunStatus
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
