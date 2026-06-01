"""Unit tests: evidence structural validation + store basics."""

from __future__ import annotations

from typing import Any

from agent_debate.evidence.store import EvidenceStore
from agent_debate.protocol.enums import FailureReason
from agent_debate.validation.evidence_validator import EvidenceValidator

EV = EvidenceValidator()


def _store(evidence_factory: Any, **over: Any) -> EvidenceStore:
    store = EvidenceStore()
    store.add(evidence_factory(**over))
    return store


def test_valid_evidence_ok(message_factory, evidence_factory) -> None:
    assert EV.validate(message_factory(), _store(evidence_factory)).is_valid


def test_no_refs(message_factory, evidence_factory) -> None:
    result = EV.validate(message_factory(evidence_refs=[]), _store(evidence_factory))
    assert result.first_reason is FailureReason.MISSING_EVIDENCE


def test_unknown_ref(message_factory, evidence_factory) -> None:
    result = EV.validate(message_factory(evidence_refs=["zzz"]), _store(evidence_factory))
    assert result.first_reason is FailureReason.MISSING_EVIDENCE


def test_wrong_session(message_factory, evidence_factory) -> None:
    result = EV.validate(message_factory(), _store(evidence_factory, session_id="other"))
    assert result.first_reason is FailureReason.MISSING_EVIDENCE


def test_wrong_claim(message_factory, evidence_factory) -> None:
    result = EV.validate(message_factory(), _store(evidence_factory, supports_claim_id="x"))
    assert result.first_reason is FailureReason.IRRELEVANT_EVIDENCE


def test_irrelevant_status(message_factory, evidence_factory) -> None:
    result = EV.validate(message_factory(), _store(evidence_factory, relevance_status="irrelevant"))
    assert result.first_reason is FailureReason.IRRELEVANT_EVIDENCE


def test_store_basics(evidence_factory) -> None:
    store = EvidenceStore()
    store.add(evidence_factory())
    assert store.exists("e1")
    assert store.get("e1") is not None
    assert len(store) == 1
    assert store.get("missing") is None
