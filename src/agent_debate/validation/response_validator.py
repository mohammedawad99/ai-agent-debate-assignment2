"""Response validation coordinator (basic).

Parses raw JSON, then runs structural protocol validation, then (for child argument
turns, when an EvidenceStore is supplied) evidence validation. Semantic checks
(agreement collapse, off-side drift) are Judge-level and arrive in a later phase.
"""

from __future__ import annotations

import json
from typing import Any

from agent_debate.evidence.store import EvidenceStore
from agent_debate.protocol.enums import CHILD_ROLES, FailureReason, TurnType
from agent_debate.validation.evidence_validator import EvidenceValidator
from agent_debate.validation.protocol_validator import ProtocolValidator
from agent_debate.validation.result import ValidationResult, fail

_CHILD = {r.value for r in CHILD_ROLES}
_ARG_TURNS = {TurnType.OPENING_ARGUMENT.value, TurnType.REBUTTAL.value}


class ResponseValidator:
    def __init__(self, child_word_limit: int) -> None:
        self._protocol = ProtocolValidator(child_word_limit)
        self._evidence = EvidenceValidator()

    def validate_raw(self, raw: str, store: EvidenceStore | None = None) -> ValidationResult:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            return fail("unknown", FailureReason.INVALID_JSON, str(exc))
        if not isinstance(data, dict):
            return fail("unknown", FailureReason.INVALID_JSON, "not a JSON object")
        return self.validate_data(data, store)

    def validate_data(
        self, data: dict[str, Any], store: EvidenceStore | None = None
    ) -> ValidationResult:
        result = self._protocol.validate(data)
        if not result.is_valid:
            return result
        is_child_arg = data["sender_role"] in _CHILD and data["turn_type"] in _ARG_TURNS
        if store is not None and is_child_arg:
            return self._evidence.validate(data, store)
        return result
