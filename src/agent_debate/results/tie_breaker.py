"""Deterministic configured tie-break (docs/SCORING_AND_VALIDATION.md §9).

Order: total -> evidence_quality -> responsiveness -> fewer violations/regenerations
-> configured `final_tie_break_priority`. No LLM call; fully repeatable. The final
configured step is a technical mechanism, NOT a claim of substantive superiority.
"""

from __future__ import annotations

from dataclasses import dataclass

from agent_debate.protocol.models import JudgeScore

FINALISTS = ("pro", "con")


class TieBreakError(ValueError):
    pass


@dataclass
class TieBreakOutcome:
    winner_role: str
    loser_role: str
    tie_break_used: bool
    tie_break_reason: str | None


def _other(role: str) -> str:
    return "con" if role == "pro" else "pro"


def decide(pro: JudgeScore, con: JudgeScore, priority: list[str]) -> TieBreakOutcome:
    higher = [
        (None, pro.total, con.total),
        ("evidence_quality", pro.evidence_quality, con.evidence_quality),
        ("responsiveness", pro.responsiveness, con.responsiveness),
    ]
    for reason, p, c in higher:
        if p != c:
            winner = "pro" if p > c else "con"
            return TieBreakOutcome(winner, _other(winner), reason is not None, reason)
    lower = [
        (pro.protocol_violations, con.protocol_violations),
        (pro.regeneration_count, con.regeneration_count),
    ]
    for p, c in lower:
        if p != c:
            winner = "pro" if p < c else "con"
            return TieBreakOutcome(winner, _other(winner), True, "fewer_violations")
    return _configured(priority)


def _configured(priority: list[str]) -> TieBreakOutcome:
    for role in priority:
        if role in FINALISTS:
            return TieBreakOutcome(role, _other(role), True, "configured_priority")
    raise TieBreakError(f"final_tie_break_priority {priority} has no valid finalist")
