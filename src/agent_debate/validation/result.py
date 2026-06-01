"""ValidationResult model and helpers (docs/PROTOCOL.md §6)."""

from __future__ import annotations

from dataclasses import dataclass, field

from agent_debate.protocol.enums import FailureReason


@dataclass
class ValidationError:
    reason: FailureReason
    detail: str = ""


@dataclass
class ValidationResult:
    message_id: str
    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    required_action: str = "accept"
    regeneration_prompt_summary: str | None = None

    @property
    def first_reason(self) -> FailureReason | None:
        return self.errors[0].reason if self.errors else None


def ok(message_id: str) -> ValidationResult:
    return ValidationResult(message_id=message_id, is_valid=True, required_action="accept")


def fail(message_id: str, reason: FailureReason, detail: str = "") -> ValidationResult:
    summary = f"Fix: {reason.value}" + (f" ({detail})" if detail else "")
    return ValidationResult(
        message_id=message_id,
        is_valid=False,
        errors=[ValidationError(reason, detail)],
        required_action="regenerate",
        regeneration_prompt_summary=summary,
    )
