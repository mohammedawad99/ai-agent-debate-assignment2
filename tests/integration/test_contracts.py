"""Behavioral contract tests (TDD placeholders).

Each test documents a REQUIRED future behavior taken from the design docs
(PROTOCOL.md, SCORING_AND_VALIDATION.md, ARCHITECTURE.md). The behavior is NOT
implemented yet (Phase 6), so each is marked `xfail` with a clear reason — the
suite still passes (xfail = expected failure). These tests must NOT call LLMs/web
and must NOT create real evidence/results; they only raise NotImplementedError to
record the contract until Phase 6 wires the real assertion.
"""

from __future__ import annotations

import pytest

P6 = "Phase 6: not implemented yet"


def _pending(contract: str) -> None:
    raise NotImplementedError(f"{P6} — {contract}")


@pytest.mark.xfail(reason=P6, strict=True)
def test_no_direct_pro_con_routing() -> None:
    """Pro and Con may never message each other directly; only the Judge routes."""
    _pending("no direct Pro<->Con routing (PROTOCOL RR-4/RR-5)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_judge_selects_exactly_one_winner() -> None:
    """The final judgment names exactly one winner; a tie is forbidden."""
    _pending("exactly one winner, no tie (FR-13)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_invalid_json_triggers_regeneration() -> None:
    """Malformed JSON from an agent is rejected and regeneration is requested."""
    _pending("invalid_json -> regenerate (SCORING pipeline step 1)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_missing_opponent_claim_id_rejected() -> None:
    """A rebuttal without opponent_claim_id is rejected."""
    _pending("missing_opponent_reference -> regenerate (FR-09)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_missing_evidence_rejected() -> None:
    """A substantive turn with no evidence_refs is rejected."""
    _pending("missing_evidence -> regenerate (FR-12)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_irrelevant_evidence_rejected() -> None:
    """Evidence that does not support the claim is rejected (Judge relevance)."""
    _pending("irrelevant_evidence -> regenerate (SCORING §4)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_agreement_collapse_rejected() -> None:
    """A turn that concedes/agrees with the opponent's core position is rejected."""
    _pending("agreement_collapse -> regenerate (SCORING §5)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_off_side_drift_rejected() -> None:
    """A turn arguing the wrong side is rejected."""
    _pending("off_side_drift -> regenerate (SCORING §6)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_retry_exhaustion_marks_failed_run() -> None:
    """Exhausting the 2 regenerations marks the run a failed protocol run."""
    _pending("retry_exhausted -> failed protocol run (FR-11)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_technical_tie_break_uses_configured_priority() -> None:
    """A full tie is broken by final_tie_break_priority (default con before pro)."""
    _pending("configured_priority tie-break (SCORING §9)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_prompt_injection_snippet_cannot_override_rules() -> None:
    """An instruction-like search snippet is treated as data, never as rules."""
    _pending("untrusted search content (ARCHITECTURE SR-4)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_provider_timeout_handled_and_logged() -> None:
    """A hung/slow provider call is aborted at the timeout and logged."""
    _pending("provider_timeout handling (ARCHITECTURE §8, §14)")


@pytest.mark.xfail(reason=P6, strict=True)
def test_watchdog_failure_marks_failed_run() -> None:
    """A stalled run / runaway retry loop trips the Watchdog -> failed run."""
    _pending("watchdog_trigger -> failed protocol run (PLAN §14)")
