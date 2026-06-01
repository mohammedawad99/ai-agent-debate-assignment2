"""JudgeAgent (Phase 6.2c).

Validates each turn via ResponseValidator (structural + evidence) and then applies
DETERMINISTIC offline checks for agreement collapse / off-side drift. These are
simple marker-based heuristics — a reproducible stand-in for tests, NOT real semantic
analysis. The Judge also produces the final judgment using fixed offline scores and
the configured deterministic tie-break (so exactly one winner is always selected).
"""

from __future__ import annotations

from typing import Any

from agent_debate.evidence.store import EvidenceStore
from agent_debate.protocol.enums import FailureReason
from agent_debate.protocol.models import FinalJudgment
from agent_debate.results import tie_breaker
from agent_debate.results.scoring import build_score
from agent_debate.validation.response_validator import ResponseValidator
from agent_debate.validation.result import ValidationResult, fail

AGREEMENT_MARKERS = ("i agree with the opponent", "i concede", "you are right")
DRIFT_MARKERS = ("i will now argue the opposing side", "i switch sides")
CREATED_AT = "2026-01-01T00:00:00Z"


class JudgeAgent:
    def __init__(self, child_word_limit: int) -> None:
        self._validator = ResponseValidator(child_word_limit)

    def review(self, message: dict[str, Any], store: EvidenceStore) -> ValidationResult:
        structural = self._validator.validate_data(message, store)
        if not structural.is_valid:
            return structural
        mid = str(message.get("message_id", "unknown"))
        text = str(message.get("argument", "")).lower()
        if any(marker in text for marker in AGREEMENT_MARKERS):
            return fail(mid, FailureReason.AGREEMENT_COLLAPSE, "agent agreed with opponent")
        if any(marker in text for marker in DRIFT_MARKERS):
            return fail(mid, FailureReason.OFF_SIDE_DRIFT, "agent argued the wrong side")
        return structural

    def judge(self, session_id: str, priority: list[str]) -> FinalJudgment:
        pro = build_score(4, 4, 4, 4, 4, 4)
        con = build_score(4, 4, 4, 4, 4, 4)
        outcome = tie_breaker.decide(pro, con, priority)
        limitations = "Deterministic offline scoring."
        if outcome.tie_break_used:
            limitations += " Winner via configured technical tie-break (not substantive)."
        return FinalJudgment(
            session_id=session_id,
            winner_role=outcome.winner_role,
            loser_role=outcome.loser_role,
            scores={"pro": pro, "con": con},
            tie_break_used=outcome.tie_break_used,
            tie_break_reason=outcome.tie_break_reason,
            reasoning="Both sides argued within the rules; see per-dimension scores.",
            limitations=limitations,
            created_at=CREATED_AT,
        )
