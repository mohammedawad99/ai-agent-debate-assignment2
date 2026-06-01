"""Evidence validation (docs/SCORING_AND_VALIDATION.md §4).

Structural (deterministic) layer: each ref must exist, belong to the same session,
support the current claim, and be marked relevant for an accepted turn.

Untrusted-content rule (SR-3/SR-4): the evidence `snippet` is treated as DATA only.
Validation decisions use the structured fields (ids, session, relevance_status) and
NEVER parse, execute, or obey the snippet text — so an instruction-like snippet
cannot override these rules.
"""

from __future__ import annotations

from typing import Any

from agent_debate.evidence.store import EvidenceStore
from agent_debate.protocol.enums import FailureReason
from agent_debate.validation.result import ValidationResult, fail, ok

ACCEPTABLE_RELEVANCE = {"relevant"}


class EvidenceValidator:
    def validate(self, data: dict[str, Any], store: EvidenceStore) -> ValidationResult:
        mid = str(data.get("message_id", "unknown"))
        claim_id = data.get("claim_id")
        session_id = data.get("session_id")
        refs = data.get("evidence_refs") or []
        if not refs:
            return fail(mid, FailureReason.MISSING_EVIDENCE, "no evidence_refs")
        for ref in refs:
            record = store.get(str(ref))
            if record is None:
                return fail(mid, FailureReason.MISSING_EVIDENCE, f"unknown evidence {ref}")
            if record.session_id != session_id:
                return fail(mid, FailureReason.MISSING_EVIDENCE, f"{ref} wrong session")
            if record.supports_claim_id != claim_id:
                return fail(mid, FailureReason.IRRELEVANT_EVIDENCE, f"{ref} not for {claim_id}")
            if record.relevance_status not in ACCEPTABLE_RELEVANCE:
                detail = f"{ref} status={record.relevance_status}"
                return fail(mid, FailureReason.IRRELEVANT_EVIDENCE, detail)
        return ok(mid)
