"""Unit tests: Gatekeeper limit enforcement (independent of real providers)."""

from __future__ import annotations

import pytest

from agent_debate.quality.gatekeeper import Gatekeeper, GatekeeperError
from agent_debate.results.cost_tracker import CostTracker


def _gate(tracker: CostTracker, **over: int | None) -> Gatekeeper:
    limits: dict[str, int | None] = {
        "max_provider_calls": 2,
        "max_search_calls": 2,
        "max_retries": 2,
        "max_estimated_tokens": None,
    }
    limits.update(over)
    return Gatekeeper(tracker, **limits)  # type: ignore[arg-type]


def test_allows_within_limits() -> None:
    tracker = CostTracker()
    gate = _gate(tracker)
    gate.check_provider_call()  # count 0 < 2 -> ok
    gate.check_search_call()
    gate.check_retry()


def test_blocks_provider_over_limit() -> None:
    tracker = CostTracker()
    tracker.record_provider_call()
    tracker.record_provider_call()
    with pytest.raises(GatekeeperError):
        _gate(tracker).check_provider_call()


def test_blocks_search_over_limit() -> None:
    tracker = CostTracker()
    tracker.record_search_call()
    tracker.record_search_call()
    with pytest.raises(GatekeeperError):
        _gate(tracker).check_search_call()


def test_blocks_retries_over_limit() -> None:
    tracker = CostTracker()
    tracker.record_retry()
    tracker.record_retry()
    with pytest.raises(GatekeeperError):
        _gate(tracker).check_retry()


def test_blocks_tokens_over_limit() -> None:
    tracker = CostTracker()
    tracker.record_provider_call("x" * 40, "y" * 40)  # ~20 tokens
    with pytest.raises(GatekeeperError):
        _gate(tracker, max_estimated_tokens=1).check_tokens()


def test_tokens_unlimited_when_none() -> None:
    tracker = CostTracker()
    tracker.record_provider_call("x" * 40, "y" * 40)
    _gate(tracker).check_tokens()  # max_estimated_tokens None -> no raise
