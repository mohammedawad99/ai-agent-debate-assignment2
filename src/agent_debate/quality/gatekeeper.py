"""Gatekeeper — enforce configurable resource limits (E-08 / FR-15).

Reads counters from a CostTracker and raises GatekeeperError when a limit would be
exceeded. It does NOT call providers/search itself and contains no billing logic;
limits come from config (e.g. config/rate_limits.json). Call the relevant `check_*`
before performing the corresponding action.
"""

from __future__ import annotations

from agent_debate.results.cost_tracker import CostTracker


class GatekeeperError(RuntimeError):
    """A configured resource limit was exceeded."""


class Gatekeeper:
    def __init__(
        self,
        tracker: CostTracker,
        *,
        max_provider_calls: int,
        max_search_calls: int,
        max_retries: int,
        max_estimated_tokens: int | None = None,
    ) -> None:
        self._tracker = tracker
        self.max_provider_calls = max_provider_calls
        self.max_search_calls = max_search_calls
        self.max_retries = max_retries
        self.max_estimated_tokens = max_estimated_tokens

    def check_provider_call(self) -> None:
        if self._tracker.provider_call_count >= self.max_provider_calls:
            raise GatekeeperError(f"provider call limit reached ({self.max_provider_calls})")

    def check_search_call(self) -> None:
        if self._tracker.search_call_count >= self.max_search_calls:
            raise GatekeeperError(f"search call limit reached ({self.max_search_calls})")

    def check_retry(self) -> None:
        if self._tracker.retry_count >= self.max_retries:
            raise GatekeeperError(f"retry limit reached ({self.max_retries})")

    def check_tokens(self) -> None:
        limit = self.max_estimated_tokens
        if limit is not None and self._tracker.total_estimated_tokens > limit:
            raise GatekeeperError(f"estimated token budget exceeded ({limit})")
