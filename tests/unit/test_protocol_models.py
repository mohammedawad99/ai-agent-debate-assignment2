"""Unit tests: protocol enums and data models construct correctly."""

from __future__ import annotations

from agent_debate.protocol.enums import FailureReason, ProtocolStatus, Role, TurnType
from agent_debate.protocol.models import (
    DebateMessage,
    EvidenceRecord,
    FinalJudgment,
    JudgeScore,
)


def test_enum_values() -> None:
    assert Role.CON.value == "con"
    assert TurnType.REBUTTAL.value == "rebuttal"
    assert ProtocolStatus.ACCEPTED.value == "accepted"
    assert FailureReason.INVALID_JSON.value == "invalid_json"


def test_models_construct() -> None:
    msg = DebateMessage(
        message_id="m",
        session_id="s",
        round_index=1,
        turn_index=1,
        sender_role="pro",
        receiver_role="judge",
        turn_type="opening_argument",
        protocol_status="accepted",
        content="c",
        word_count=1,
        created_at="t",
    )
    assert msg.evidence_refs == []
    ev = EvidenceRecord(
        evidence_id="e",
        session_id="s",
        source_type="mock",
        title="t",
        url="u",
        snippet="x",
        retrieved_at="t",
        query="q",
        supports_claim_id="c",
    )
    assert ev.relevance_status == "unchecked"
    score = JudgeScore(4, 4, 4, 4, 4, 4, 24)
    fj = FinalJudgment(
        session_id="s",
        winner_role="con",
        loser_role="pro",
        scores={"pro": score, "con": score},
        tie_break_used=True,
        tie_break_reason="configured_priority",
        reasoning="r",
        limitations="technical tie-break",
        created_at="t",
    )
    assert fj.winner_role == "con"
