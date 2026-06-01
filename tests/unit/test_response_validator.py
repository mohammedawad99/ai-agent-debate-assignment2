"""Unit tests: ResponseValidator coordinator (parse + protocol + evidence)."""

from __future__ import annotations

import json

from agent_debate.evidence.store import EvidenceStore
from agent_debate.protocol.enums import FailureReason
from agent_debate.validation.response_validator import ResponseValidator

RV = ResponseValidator(child_word_limit=160)


def test_valid_raw_with_store_ok(message_factory, evidence_factory) -> None:
    store = EvidenceStore()
    store.add(evidence_factory())
    result = RV.validate_raw(json.dumps(message_factory()), store)
    assert result.is_valid


def test_raw_non_object_is_invalid_json() -> None:
    result = RV.validate_raw("123")
    assert result.first_reason is FailureReason.INVALID_JSON


def test_data_with_store_rejects_bad_evidence(message_factory, evidence_factory) -> None:
    store = EvidenceStore()
    store.add(evidence_factory(relevance_status="irrelevant"))
    result = RV.validate_data(message_factory(), store)
    assert result.first_reason is FailureReason.IRRELEVANT_EVIDENCE


def test_protocol_failure_short_circuits(message_factory) -> None:
    store = EvidenceStore()
    result = RV.validate_data(message_factory(sender_role="alien"), store)
    assert result.first_reason is FailureReason.WRONG_ROLE
