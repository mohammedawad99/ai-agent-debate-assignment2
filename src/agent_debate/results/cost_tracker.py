"""CostTracker — per-run resource accounting (FR-17 / CR-03).

Counts provider/search calls and retries, and estimates tokens as characters/4.
Token figures are ESTIMATES, never exact provider billing. No file writing here;
`summary()` returns a JSON-ready dict consumed by a writer in a later phase. Runtime
uses an injectable time source so tests stay deterministic (no real clock needed).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

DEFAULT_CHARS_PER_TOKEN = 4


class CostTracker:
    def __init__(
        self,
        *,
        chars_per_token: int = DEFAULT_CHARS_PER_TOKEN,
        time_fn: Callable[[], float] = time.monotonic,
    ) -> None:
        if chars_per_token <= 0:
            raise ValueError("chars_per_token must be positive")
        self._chars_per_token = chars_per_token
        self._time_fn = time_fn
        self.provider_call_count = 0
        self.search_call_count = 0
        self.retry_count = 0
        self.estimated_input_tokens = 0
        self.estimated_output_tokens = 0
        self._start: float | None = None
        self._end: float | None = None

    def _estimate(self, text: str) -> int:
        return len(text) // self._chars_per_token

    def record_provider_call(self, prompt: str = "", response: str = "") -> None:
        self.provider_call_count += 1
        self.estimated_input_tokens += self._estimate(prompt)
        self.estimated_output_tokens += self._estimate(response)

    def record_search_call(self) -> None:
        self.search_call_count += 1

    def record_retry(self) -> None:
        self.retry_count += 1

    def start(self) -> None:
        self._start = self._time_fn()

    def stop(self) -> None:
        self._end = self._time_fn()

    @property
    def total_estimated_tokens(self) -> int:
        return self.estimated_input_tokens + self.estimated_output_tokens

    @property
    def runtime_seconds(self) -> float | None:
        if self._start is None or self._end is None:
            return None
        return self._end - self._start

    def summary(self) -> dict[str, Any]:
        return {
            "provider_call_count": self.provider_call_count,
            "search_call_count": self.search_call_count,
            "retry_count": self.retry_count,
            "estimated_input_tokens": self.estimated_input_tokens,
            "estimated_output_tokens": self.estimated_output_tokens,
            "estimated_total_tokens": self.total_estimated_tokens,
            "runtime_seconds": self.runtime_seconds,
            "token_basis": f"chars/{self._chars_per_token}",
            "note": "token counts are ESTIMATES, not exact provider billing",
        }
