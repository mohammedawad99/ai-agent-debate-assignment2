"""JudgeAgent (Phase 6.2c / 6.5).

Validates each turn via ResponseValidator (structural + evidence) and applies
DETERMINISTIC offline checks for agreement collapse / off-side drift (marker-based
stand-ins — NOT real semantic analysis). Holds the project-local regeneration /
final-judgment / judge templates and exposes render helpers for them. Final scoring is
still **deterministic/offline** (fixed scores + configured tie-break) — disclosed in
`FinalJudgment.limitations`. A real, content-derived Judge is future work.
"""

from __future__ import annotations

from typing import Any

from agent_debate.evidence.store import EvidenceStore
from agent_debate.prompts.templates import render
from agent_debate.protocol.enums import FailureReason
from agent_debate.protocol.models import FinalJudgment
from agent_debate.results import tie_breaker
from agent_debate.results.scoring import build_score
from agent_debate.validation.response_validator import ResponseValidator
from agent_debate.validation.result import ValidationResult, fail

AGREEMENT_MARKERS = ("i agree with the opponent", "i concede", "you are right")
DRIFT_MARKERS = ("i will now argue the opposing side", "i switch sides")
CREATED_AT = "2026-01-01T00:00:00Z"
DEFAULT_REGEN = (
    "Your previous output violated the protocol:\n{validation_errors}\n"
    "Return corrected JSON only; keep your assigned role and side."
)
DEFAULT_FINAL = "Apply the 0-5 rubric and name exactly one winner; no tie."


class JudgeAgent:
    def __init__(
        self,
        child_word_limit: int,
        *,
        regeneration_template: str = DEFAULT_REGEN,
        final_template: str = DEFAULT_FINAL,
        judge_template: str = "",
    ) -> None:
        self._validator = ResponseValidator(child_word_limit)
        self._regeneration_template = regeneration_template
        self._final_template = final_template
        self._judge_template = judge_template

    def regeneration_prompt(self, validation_errors: str) -> str:
        """Render the project-local regeneration request for a rejected turn."""
        return render(self._regeneration_template, validation_errors=validation_errors)

    def final_instructions(self) -> str:
        """Render the project-local final-judgment instructions."""
        return render(self._final_template)

    def judge_instructions(self, *, topic: str) -> str:
        """Render the project-local Judge moderation/review instructions.

        Rendered text only — this does NOT call a provider/LLM and does not change the
        deterministic offline scoring used by `judge()`.
        """
        return render(self._judge_template, topic=topic)

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
        limitations = "Deterministic offline scoring (fixed scores, not content-derived)."
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
