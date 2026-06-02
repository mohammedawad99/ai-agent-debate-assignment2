"""Base debate agent (Phase 6.2c / 6.5).

Holds a ProviderAdapter, a SearchTool, and a **project-local prompt template** + topic.
`produce()` renders the assigned-side prompt (filling `{topic}`) and appends a per-turn
context block (role/side, claim_id, opponent_claim_id, available evidence_refs, JSON
instruction), sends that to the provider, and returns a protocol message dict. The agent
holds **no reference to the opponent** (DR-5). Mocks ignore the prompt, so offline
behavior is unchanged; a real provider receives the meaningful rendered prompt.
"""

from __future__ import annotations

from typing import Any

from agent_debate.evidence.store import EvidenceStore
from agent_debate.prompts.templates import render
from agent_debate.providers.base import ProviderAdapter
from agent_debate.search.base import SearchTool

CREATED_AT = "2026-01-01T00:00:00Z"
DEFAULT_TOPIC = "Should universities require AI coding agents in software engineering courses?"
DEFAULT_TEMPLATE = "Argue your assigned side, respond to the opponent, and cite evidence."


class DebateAgent:
    role = "agent"

    def __init__(
        self,
        provider: ProviderAdapter,
        search: SearchTool,
        *,
        prompt_template: str = DEFAULT_TEMPLATE,
        topic: str = DEFAULT_TOPIC,
    ) -> None:
        self._provider = provider
        self._search = search
        self._prompt_template = prompt_template
        self._topic = topic

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
        evidence_refs = [r.evidence_id for r in records]
        prompt = self._build_prompt(claim_id, opponent_claim_id, evidence_refs)
        argument = self._provider.generate(prompt)
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
            "evidence_refs": evidence_refs,
            "content": argument,
            "word_count": len(argument.split()),
            "created_at": CREATED_AT,
        }
        if opponent_claim_id is not None:
            message["opponent_claim_id"] = opponent_claim_id
        return message

    def _build_prompt(
        self, claim_id: str, opponent_claim_id: str | None, evidence_refs: list[str]
    ) -> str:
        base = render(self._prompt_template, topic=self._topic)
        lines = [
            base,
            "",
            "## This turn",
            f"- your role/side: {self.role}",
            f"- claim_id: {claim_id}",
        ]
        if opponent_claim_id is not None:
            lines.append(f"- opponent_claim_id to reference: {opponent_claim_id}")
        available = ", ".join(evidence_refs) if evidence_refs else "none"
        lines.append(f"- evidence_refs available: {available}")
        lines.append("Reply with exactly one JSON debate message.")
        return "\n".join(lines)
