"""Structural JSON/protocol validation (docs/PROTOCOL.md §4, §9-10).

Operates on an already-parsed JSON object (dict). Returns a ValidationResult with
the first blocking failure_reason, or an accepting result.
"""

from __future__ import annotations

from typing import Any

from agent_debate.protocol.enums import CHILD_ROLES, FailureReason, Role, TurnType
from agent_debate.validation.result import ValidationResult, fail, ok

REQUIRED_FIELDS = (
    "message_id",
    "session_id",
    "round_index",
    "turn_index",
    "sender_role",
    "receiver_role",
    "turn_type",
    "protocol_status",
    "content",
    "word_count",
    "created_at",
)
_ROLES = {r.value for r in Role}
_TURNS = {t.value for t in TurnType}
_CHILD = {r.value for r in CHILD_ROLES}
_CHILD_ARG_TURNS = {TurnType.OPENING_ARGUMENT.value, TurnType.REBUTTAL.value}


class ProtocolValidator:
    def __init__(self, child_word_limit: int) -> None:
        self.child_word_limit = child_word_limit

    def validate(self, data: dict[str, Any]) -> ValidationResult:
        mid = str(data.get("message_id", "unknown"))
        missing = [f for f in REQUIRED_FIELDS if f not in data]
        if missing:
            return fail(mid, FailureReason.MISSING_REQUIRED_FIELD, ", ".join(missing))
        sender, receiver = data["sender_role"], data["receiver_role"]
        if sender not in _ROLES or receiver not in _ROLES:
            return fail(mid, FailureReason.WRONG_ROLE, f"{sender}->{receiver}")
        if data["turn_type"] not in _TURNS:
            return fail(mid, FailureReason.WRONG_ROLE, f"turn_type={data['turn_type']}")
        route = self._check_route(mid, sender, receiver)
        if route is not None:
            return route
        if sender in _CHILD and data["turn_type"] in _CHILD_ARG_TURNS:
            return self._check_child_turn(mid, data)
        return ok(mid)

    def _check_route(self, mid: str, sender: str, receiver: str) -> ValidationResult | None:
        if sender in _CHILD and receiver != Role.JUDGE.value:
            if receiver in _CHILD:
                return fail(mid, FailureReason.DIRECT_CHILD_TO_CHILD, f"{sender}->{receiver}")
            return fail(mid, FailureReason.WRONG_ROLE, f"child must address judge, not {receiver}")
        return None

    def _check_child_turn(self, mid: str, data: dict[str, Any]) -> ValidationResult:
        if not data.get("claim_id") or not data.get("argument"):
            return fail(mid, FailureReason.MISSING_REQUIRED_FIELD, "claim_id/argument")
        if data["turn_type"] == TurnType.REBUTTAL.value and not data.get("opponent_claim_id"):
            return fail(mid, FailureReason.MISSING_OPPONENT_REFERENCE, "opponent_claim_id")
        if not data.get("evidence_refs"):
            return fail(mid, FailureReason.MISSING_EVIDENCE, "evidence_refs empty")
        words = len(str(data["argument"]).split())
        if words > self.child_word_limit:
            return fail(mid, FailureReason.WORD_LIMIT_EXCEEDED, f"{words}>{self.child_word_limit}")
        return ok(mid)
