"""Base debate agent (Phase 6.2c).

Lightweight: holds a ProviderAdapter and a SearchTool only — **no reference to the
opponent** (DR-5). `produce()` gathers evidence (stored in the shared EvidenceStore),
asks the provider for an argument, and returns a protocol message dict for the Judge
to validate. created_at is a fixed string for deterministic offline runs.
"""

from __future__ import annotations

from typing import Any

from agent_debate.evidence.store import EvidenceStore
from agent_debate.providers.base import ProviderAdapter
from agent_debate.search.base import SearchTool

CREATED_AT = "2026-01-01T00:00:00Z"


class DebateAgent:
    role = "agent"

    def __init__(self, provider: ProviderAdapter, search: SearchTool) -> None:
        self._provider = provider
        self._search = search

    def produce(
        self,
        *,
        session_id: str,
        round_index: int,
        turn_index: int,
        claim_id: str,
        opponent_claim_id: str | None,
        store: EvidenceStore,
    ) -> dict[str, Any]:
        records = self._search.search(claim_id, session_id=session_id, claim_id=claim_id)
        for record in records:
            store.add(record)
        argument = self._provider.generate(f"Argue as {self.role}: {claim_id}")
        turn_type = "opening_argument" if opponent_claim_id is None else "rebuttal"
        message: dict[str, Any] = {
            "message_id": f"m-{self.role}-{turn_index}",
            "session_id": session_id,
            "round_index": round_index,
            "turn_index": turn_index,
            "sender_role": self.role,
            "receiver_role": "judge",
            "turn_type": turn_type,
            "protocol_status": "generated",
            "claim_id": claim_id,
            "argument": argument,
            "evidence_refs": [r.evidence_id for r in records],
            "content": argument,
            "word_count": len(argument.split()),
            "created_at": CREATED_AT,
        }
        if opponent_claim_id is not None:
            message["opponent_claim_id"] = opponent_claim_id
        return message
