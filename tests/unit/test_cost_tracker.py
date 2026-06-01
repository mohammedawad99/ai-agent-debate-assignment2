"""Unit tests: CostTracker counting + token estimates (deterministic)."""

from __future__ import annotations

import pytest

from agent_debate.results.cost_tracker import CostTracker


def test_counts_provider_calls() -> None:
    tracker = CostTracker()
    tracker.record_provider_call()
    tracker.record_provider_call()
    assert tracker.provider_call_count == 2


def test_counts_search_calls() -> None:
    tracker = CostTracker()
    tracker.record_search_call()
    assert tracker.search_call_count == 1


def test_counts_retries() -> None:
    tracker = CostTracker()
    tracker.record_retry()
    tracker.record_retry()
    assert tracker.retry_count == 2


def test_estimates_tokens_chars_over_4() -> None:
    tracker = CostTracker()
    tracker.record_provider_call("a" * 8, "b" * 4)
    assert tracker.estimated_input_tokens == 2
    assert tracker.estimated_output_tokens == 1
    assert tracker.total_estimated_tokens == 3


def test_summary_labels_estimates() -> None:
    summary = CostTracker().summary()
    assert "ESTIMATES" in summary["note"]
    assert summary["token_basis"] == "chars/4"


def test_runtime_is_deterministic() -> None:
    clock = iter([10.0, 13.5])
    tracker = CostTracker(time_fn=lambda: next(clock))
    tracker.start()
    tracker.stop()
    assert tracker.runtime_seconds == pytest.approx(3.5)


def test_runtime_none_before_stop() -> None:
    assert CostTracker().runtime_seconds is None


def test_invalid_chars_per_token() -> None:
    with pytest.raises(ValueError):
        CostTracker(chars_per_token=0)
