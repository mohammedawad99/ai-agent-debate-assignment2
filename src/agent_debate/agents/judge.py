"""JudgeAgent (Phase 6.2c / 6.5 / 6.6).

Validates turns via ResponseValidator + DETERMINISTIC offline collapse/drift markers.
`judge()` is **deterministic by default** (fixed scores + configured tie-break). When a
`judge_provider` is supplied it instead renders the final-judgment prompt and asks the
provider for a JSON judgment, which is parsed/validated (exactly one winner, no tie,
0-5 scores). Tests use MockProvider only — **no real Claude call**. The mode used is
disclosed in `FinalJudgment.limitations`.
"""

from __future__ import annotations

from typing import Any

from agent_debate.evidence.store import EvidenceStore
from agent_debate.prompts.templates import render
from agent_debate.protocol.enums import FailureReason
from agent_debate.protocol.models import FinalJudgment
from agent_debate.providers.base import ProviderAdapter
from agent_debate.results import tie_breaker
from agent_debate.results.scoring import DIMENSIONS, build_score, parse_judgment, scores_from_data
from agent_debate.validation.response_validator import ResponseValidator
from agent_debate.validation.result import ValidationResult, fail

AGREEMENT_MARKERS = ("i agree with the opponent", "i concede", "you are right")
DRIFT_MARKERS = ("i will now argue the opposing side", "i switch sides")
CREATED_AT = "2026-01-01T00:00:00Z"
DEFAULT_TOPIC = "Should universities require AI coding agents in software engineering courses?"
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
        topic: str = DEFAULT_TOPIC,
        judge_provider: ProviderAdapter | None = None,
    ) -> None:
        self._validator = ResponseValidator(child_word_limit)
        self._regeneration_template = regeneration_template
        self._final_template = final_template
        self._judge_template = judge_template
        self._topic = topic
        self._judge_provider = judge_provider

    def regeneration_prompt(self, validation_errors: str) -> str:
        return render(self._regeneration_template, validation_errors=validation_errors)

    def final_instructions(self) -> str:
        return render(self._final_template)

    def judge_instructions(self, *, topic: str) -> str:
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

    def judge(
        self,
        session_id: str,
        priority: list[str],
        messages: list[dict[str, Any]] | None = None,
    ) -> FinalJudgment:
        if self._judge_provider is None:
            return self._deterministic(session_id, priority)
        return self._provider_backed(session_id, messages or [])

    def _deterministic(self, session_id: str, priority: list[str]) -> FinalJudgment:
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

    def _provider_backed(self, session_id: str, messages: list[dict[str, Any]]) -> FinalJudgment:
        assert self._judge_provider is not None
        data = parse_judgment(self._judge_provider.generate(self._final_prompt(messages)))
        return FinalJudgment(
            session_id=session_id,
            winner_role=str(data["winner_role"]),
            loser_role=str(data["loser_role"]),
            scores=scores_from_data(data.get("scores")),
            tie_break_used=bool(data.get("tie_break_used", False)),
            tie_break_reason=data.get("tie_break_reason"),
            reasoning=str(data["reasoning"]),
            limitations="Provider-backed final judgment (mock-tested; no real Claude run yet).",
            created_at=CREATED_AT,
        )

    def _final_prompt(self, messages: list[dict[str, Any]]) -> str:
        turns = [f"{m.get('sender_role')}: {str(m.get('argument', ''))[:80]}" for m in messages]
        summary = "; ".join(turns) if turns else "no turns recorded"
        return "\n".join(
            [
                render(self._final_template),
                f"Topic: {self._topic}",
                "Rubric dimensions (0-5): " + ", ".join(DIMENSIONS),
                "Pick exactly one winner (pro|con); no tie; disclose technical tie-break if used.",
                f"Transcript summary: {summary}",
                "Return ONE JSON object: winner_role, loser_role, reasoning, optional scores.",
            ]
        )
