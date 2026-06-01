"""Provider adapter abstraction (docs/ARCHITECTURE.md AG-4 / DR-6).

Orchestration depends only on this interface, never a concrete provider. A future
ClaudeCliProvider will implement `generate` over a subprocess; it is NOT implemented
here. No network/LLM/subprocess logic lives in this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(RuntimeError):
    """A provider call failed (controlled, non-fatal to the suite)."""


class ProviderTimeoutError(ProviderError):
    """A provider call exceeded its allotted time."""


class ProviderAdapter(ABC):
    """Minimal contract: turn a prompt into model text under provider control."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Return the provider's text response for `prompt`.

        Implementations may raise ProviderError / ProviderTimeoutError.
        """

    @property
    @abstractmethod
    def call_count(self) -> int:
        """Number of generate() calls made so far."""
