"""Unit tests: structural protocol validation branches."""

from __future__ import annotations

from agent_debate.protocol.enums import FailureReason
from agent_debate.validation.protocol_validator import ProtocolValidator

V = ProtocolValidator(child_word_limit=160)


def test_valid_opening_ok(message_factory) -> None:
    assert V.validate(message_factory()).is_valid


def test_missing_required_field(message_factory) -> None:
    data = message_factory()
    del data["created_at"]
    assert V.validate(data).first_reason is FailureReason.MISSING_REQUIRED_FIELD


def test_unknown_role(message_factory) -> None:
    assert V.validate(message_factory(sender_role="alien")).first_reason is FailureReason.WRONG_ROLE


def test_unknown_turn_type(message_factory) -> None:
    assert V.validate(message_factory(turn_type="speech")).first_reason is FailureReason.WRONG_ROLE


def test_direct_child_to_child(message_factory) -> None:
    result = V.validate(message_factory(sender_role="pro", receiver_role="con"))
    assert result.first_reason is FailureReason.DIRECT_CHILD_TO_CHILD


def test_child_to_system_is_wrong_role(message_factory) -> None:
    result = V.validate(message_factory(sender_role="pro", receiver_role="system"))
    assert result.first_reason is FailureReason.WRONG_ROLE


def test_missing_claim_or_argument(message_factory) -> None:
    result = V.validate(message_factory(argument=""))
    assert result.first_reason is FailureReason.MISSING_REQUIRED_FIELD


def test_rebuttal_requires_opponent(message_factory) -> None:
    result = V.validate(message_factory(turn_type="rebuttal"))
    assert result.first_reason is FailureReason.MISSING_OPPONENT_REFERENCE


def test_missing_evidence(message_factory) -> None:
    result = V.validate(message_factory(evidence_refs=[]))
    assert result.first_reason is FailureReason.MISSING_EVIDENCE


def test_word_limit_exceeded(message_factory) -> None:
    result = V.validate(message_factory(argument="word " * 200))
    assert result.first_reason is FailureReason.WORD_LIMIT_EXCEEDED


def test_judge_instruction_ok(message_factory) -> None:
    data = message_factory(sender_role="judge", receiver_role="pro", turn_type="judge_instruction")
    assert V.validate(data).is_valid
