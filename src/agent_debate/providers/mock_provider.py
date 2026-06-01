"""Deterministic offline MockProvider (tests/dev only).

Returns scripted responses in order and can deterministically raise a controlled
error/timeout. It NEVER sleeps, and NEVER calls a real CLI, network, or LLM. Timeout
is simulated by raising ProviderTimeoutError immediately — fast and reproducible.
"""

from __future__ import annotations

from collections.abc import Sequence

from agent_debate.providers.base import (
    ProviderAdapter,
    ProviderError,
    ProviderTimeoutError,
)


class MockProvider(ProviderAdapter):
    def __init__(
        self,
        responses: Sequence[str] | None = None,
        *,
        raise_timeout: bool = False,
        raise_error: bool = False,
    ) -> None:
        self._responses = list(responses or [])
        self._raise_timeout = raise_timeout
        self._raise_error = raise_error
        self._call_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def generate(self, prompt: str) -> str:
        self._call_count += 1
        if self._raise_timeout:
            raise ProviderTimeoutError("mock provider timeout (deterministic)")
        if self._raise_error:
            raise ProviderError("mock provider error (deterministic)")
        index = self._call_count - 1
        if index >= len(self._responses):
            raise ProviderError(f"no scripted response for call #{self._call_count}")
        return self._responses[index]
