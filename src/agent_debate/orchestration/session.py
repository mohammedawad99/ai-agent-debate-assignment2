"""Debate session result types (Phase 6.2c)."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from agent_debate.protocol.models import FinalJudgment


class RunStatus(StrEnum):
    SUCCESS = "success"
    FAILED_PROTOCOL = "failed_protocol"


class ProtocolFailure(RuntimeError):
    """Raised internally when a turn cannot be accepted within the retry cap."""


@dataclass
class DebateSessionResult:
    session_id: str
    status: RunStatus
    messages: list[dict[str, Any]] = field(default_factory=list)
    final_judgment: FinalJudgment | None = None
    errors: list[str] = field(default_factory=list)
    cost_summary: dict[str, Any] | None = None

    @property
    def is_successful(self) -> bool:
        return self.status == RunStatus.SUCCESS
