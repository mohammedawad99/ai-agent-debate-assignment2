"""Protocol data models (docs/PROTOCOL.md §4-8).

Simple dataclasses mirroring the documented schema. No behavior here.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class EvidenceRecord:
    evidence_id: str
    session_id: str
    source_type: str
    title: str
    url: str
    snippet: str
    retrieved_at: str
    query: str
    supports_claim_id: str
    relevance_status: str = "unchecked"
    provider_name: str | None = None
    rank: int | None = None
    cached: bool | None = None
    notes: str | None = None


@dataclass
class DebateMessage:
    message_id: str
    session_id: str
    round_index: int
    turn_index: int
    sender_role: str
    receiver_role: str
    turn_type: str
    protocol_status: str
    content: str
    word_count: int
    created_at: str
    claim_id: str | None = None
    argument: str | None = None
    evidence_refs: list[str] = field(default_factory=list)
    opponent_claim_id: str | None = None
    validation_errors: list[str] = field(default_factory=list)
    regeneration_attempt: int | None = None
    notes: str | None = None


@dataclass
class JudgeScore:
    clarity: int
    responsiveness: int
    evidence_quality: int
    position_consistency: int
    respectful_tone: int
    persuasive_force: int
    total: int
    protocol_violations: int = 0
    regeneration_count: int = 0


@dataclass
class FinalJudgment:
    session_id: str
    winner_role: str
    loser_role: str
    scores: dict[str, JudgeScore]
    tie_break_used: bool
    tie_break_reason: str | None
    reasoning: str
    limitations: str
    created_at: str
