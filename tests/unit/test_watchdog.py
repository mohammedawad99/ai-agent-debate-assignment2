"""Unit tests: Watchdog run-level triggers (deterministic, no sleep)."""

from __future__ import annotations

import pytest

from agent_debate.orchestration.watchdog import Watchdog, WatchdogError


def test_accepts_forward_progress() -> None:
    dog = Watchdog(max_stalled_checks=2)
    dog.record_progress(0)
    dog.record_progress(1)
    dog.record_progress(2)
    assert dog.triggered_reason() is None
    dog.check()  # no raise


def test_triggers_on_stalled_progress() -> None:
    dog = Watchdog(max_stalled_checks=2)
    dog.record_progress(5)
    dog.record_progress(5)  # stalled 1
    dog.record_progress(5)  # stalled 2 -> >= max
    with pytest.raises(WatchdogError) as exc:
        dog.check()
    assert "stalled" in str(exc.value)


def test_triggers_on_excessive_retries() -> None:
    dog = Watchdog(max_retry_loops=2)
    dog.record_retry()
    dog.record_retry()
    dog.record_retry()  # 3 > 2
    with pytest.raises(WatchdogError) as exc:
        dog.check()
    assert "retry" in str(exc.value)


def test_triggers_on_max_runtime() -> None:
    clock = iter([0.0, 50.0])  # start=0, elapsed=50
    dog = Watchdog(max_runtime_seconds=10.0, time_fn=lambda: next(clock))
    with pytest.raises(WatchdogError) as exc:
        dog.check()
    assert "runtime" in str(exc.value)


def test_reason_is_clear_string() -> None:
    dog = Watchdog(max_stalled_checks=1)
    dog.record_progress(0)
    dog.record_progress(0)
    assert isinstance(dog.triggered_reason(), str)
