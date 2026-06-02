"""TranscriptWriter (Phase 6.2c / 7.14).

Writes run artifacts ONLY to an explicit output directory (tests pass `tmp_path`).
It never writes to results/ or logs/ by default — the DebateRunner calls it only when
an output_dir is supplied. On a successful run with a final judgment it also persists the
Judge's reasoning + per-side scores (`transcript.md` section + `final_judgment.json`).
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_debate.orchestration.session import DebateSessionResult
    from agent_debate.protocol.models import FinalJudgment


class TranscriptWriter:
    def write(self, result: DebateSessionResult, output_dir: Path) -> None:
        output_dir.mkdir(parents=True, exist_ok=True)
        self._write_jsonl(result, output_dir / "transcript.jsonl")
        self._write_markdown(result, output_dir / "transcript.md")
        if result.errors:
            report = "# Error Report\n\n" + "\n".join(f"- {e}" for e in result.errors)
            (output_dir / "error_report.md").write_text(report + "\n", encoding="utf-8")
        if result.cost_summary is not None:
            text = json.dumps(result.cost_summary, indent=2)
            (output_dir / "cost_report.json").write_text(text + "\n", encoding="utf-8")
        if result.final_judgment is not None:
            # Machine-readable judgment, written ONLY when a judgment exists (success).
            verdict = json.dumps(asdict(result.final_judgment), indent=2)
            (output_dir / "final_judgment.json").write_text(verdict + "\n", encoding="utf-8")

    def _write_jsonl(self, result: DebateSessionResult, path: Path) -> None:
        lines = [json.dumps(message) for message in result.messages]
        path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")

    def _write_markdown(self, result: DebateSessionResult, path: Path) -> None:
        parts = [
            f"# Debate Transcript ({result.session_id})",
            f"Status: {result.status}",
        ]
        for message in result.messages:
            parts.append(f"\n## Turn {message['turn_index']} — {message['sender_role']}")
            parts.append(str(message.get("argument", "")))
        if result.final_judgment is not None:
            parts.extend(_judgment_md(result.final_judgment))
        path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def _judgment_md(judgment: FinalJudgment) -> list[str]:
    lines = [
        "\n## Final Judgment",
        f"- Winner: {judgment.winner_role}",
        f"- Loser: {judgment.loser_role}",
        f"- Tie-break used: {judgment.tie_break_used}",
    ]
    if judgment.tie_break_reason:
        lines.append(f"- Tie-break reason: {judgment.tie_break_reason}")
    lines.append(f"- Reasoning: {judgment.reasoning}")
    lines.append(f"- Limitations: {judgment.limitations}")
    for side, score in judgment.scores.items():
        lines.append(f"- Scores ({side}): {asdict(score)}")
    return lines
