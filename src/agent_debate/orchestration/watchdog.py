"""Watchdog — protect whole-run progress (PLAN §14, ARCHITECTURE §6/§8).

Run-level guard, distinct from per-call timeouts. Tracks round/turn progress,
stalled-check count, retry-loop count, and an optional max runtime via an injectable
time source — so tests are deterministic and never sleep. `check()` raises
WatchdogError when a trigger condition is met; `triggered_reason()` returns the
reason without raising.
"""

from __future__ import annotations

import time
from collections.abc import Callable


class WatchdogError(RuntimeError):
    """The run-level watchdog tripped (stalled / runaway retries / over time)."""


class Watchdog:
    def __init__(
        self,
        *,
        max_stalled_checks: int = 3,
        max_retry_loops: int = 5,
        max_runtime_seconds: float | None = None,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        self._max_stalled = max_stalled_checks
        self._max_retries = max_retry_loops
        self._max_runtime = max_runtime_seconds
        self._time_fn = time_fn
        self._start = time_fn()
        self._last_marker = -1
        self._stalled = 0
        self._retries = 0

    def record_progress(self, marker: int) -> None:
        if marker > self._last_marker:
            self._last_marker = marker
            self._stalled = 0
        else:
            self._stalled += 1

    def record_retry(self) -> None:
        self._retries += 1

    def _elapsed(self) -> float:
        return self._time_fn() - self._start

    def triggered_reason(self) -> str | None:
        if self._stalled >= self._max_stalled:
            return f"stalled progress ({self._stalled} checks without advance)"
        if self._retries > self._max_retries:
            return f"excessive retry loop ({self._retries} > {self._max_retries})"
        if self._max_runtime is not None and self._elapsed() > self._max_runtime:
            return f"max runtime exceeded ({self._max_runtime}s)"
        return None

    def check(self) -> None:
        reason = self.triggered_reason()
        if reason is not None:
            raise WatchdogError(reason)
