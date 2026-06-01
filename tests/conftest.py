"""Shared test fixtures/helpers (Phase 6.1).

Provides factories for a baseline-valid debate message (as a JSON object/dict) and
a baseline-valid evidence record, so tests can override single fields. Helpers only
— no project business logic, no LLM/web calls.
"""

from __future__ import annotations

from typing import Any

import pytest

from agent_debate.protocol.models import EvidenceRecord


def make_message(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "message_id": "m1",
        "session_id": "s1",
        "round_index": 1,
        "turn_index": 1,
        "sender_role": "pro",
        "receiver_role": "judge",
        "turn_type": "opening_argument",
        "protocol_status": "generated",
        "claim_id": "c-pro-1",
        "argument": "Requiring AI coding agents builds industry-relevant skills.",
        "evidence_refs": ["e1"],
        "content": "Requiring AI coding agents builds industry-relevant skills.",
        "word_count": 7,
        "created_at": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


def make_evidence(**overrides: Any) -> EvidenceRecord:
    base: dict[str, Any] = {
        "evidence_id": "e1",
        "session_id": "s1",
        "source_type": "mock",
        "title": "Example source",
        "url": "https://example.org/x",
        "snippet": "A neutral, relevant snippet.",
        "retrieved_at": "2026-01-01T00:00:00Z",
        "query": "ai coding agents in education",
        "supports_claim_id": "c-pro-1",
        "relevance_status": "relevant",
    }
    base.update(overrides)
    return EvidenceRecord(**base)


@pytest.fixture
def message_factory():
    return make_message


@pytest.fixture
def evidence_factory():
    return make_evidence
