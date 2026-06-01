"""Protocol enumerations (docs/PROTOCOL.md §3).

String enums so values compare directly to the JSON string values.
"""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    JUDGE = "judge"
    PRO = "pro"
    CON = "con"
    SYSTEM = "system"


class TurnType(StrEnum):
    JUDGE_INSTRUCTION = "judge_instruction"
    OPENING_ARGUMENT = "opening_argument"
    REBUTTAL = "rebuttal"
    REGENERATION_REQUEST = "regeneration_request"
    FINAL_JUDGMENT = "final_judgment"
    PROTOCOL_ERROR = "protocol_error"


class ProtocolStatus(StrEnum):
    GENERATED = "generated"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    REGENERATED = "regenerated"
    FAILED = "failed"


class FailureReason(StrEnum):
    INVALID_JSON = "invalid_json"
    MISSING_REQUIRED_FIELD = "missing_required_field"
    WRONG_ROLE = "wrong_role"
    DIRECT_CHILD_TO_CHILD = "direct_child_to_child"
    MISSING_OPPONENT_REFERENCE = "missing_opponent_reference"
    MISSING_EVIDENCE = "missing_evidence"
    IRRELEVANT_EVIDENCE = "irrelevant_evidence"
    AGREEMENT_COLLAPSE = "agreement_collapse"
    OFF_SIDE_DRIFT = "off_side_drift"
    WORD_LIMIT_EXCEEDED = "word_limit_exceeded"
    PROVIDER_TIMEOUT = "provider_timeout"
    SEARCH_FAILURE = "search_failure"
    AUTH_FAILURE = "auth_failure"
    WATCHDOG_TRIGGER = "watchdog_trigger"
    RETRY_EXHAUSTED = "retry_exhausted"


# Pro and Con are the "child" debater roles (never address each other directly).
CHILD_ROLES = frozenset({Role.PRO, Role.CON})
