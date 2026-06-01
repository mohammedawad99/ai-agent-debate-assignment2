"""TranscriptWriter (Phase 6.2c).

Writes run artifacts ONLY to an explicit output directory (tests pass `tmp_path`).
It never writes to results/ or logs/ by default — the DebateRunner calls it only when
an output_dir is supplied. No committed artifacts are produced here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_debate.orchestration.session import DebateSessionResult


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
            parts.append(f"\n## Winner: {result.final_judgment.winner_role}")
        path.write_text("\n".join(parts) + "\n", encoding="utf-8")
