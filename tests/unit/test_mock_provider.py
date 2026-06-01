"""Unit tests: deterministic offline MockProvider."""

from __future__ import annotations

import pytest

from agent_debate.providers.base import ProviderError, ProviderTimeoutError
from agent_debate.providers.mock_provider import MockProvider


def test_returns_scripted_responses_in_order() -> None:
    provider = MockProvider(["first", "second"])
    assert provider.generate("p1") == "first"
    assert provider.generate("p2") == "second"


def test_call_count_increments() -> None:
    provider = MockProvider(["a", "b"])
    assert provider.call_count == 0
    provider.generate("x")
    provider.generate("y")
    assert provider.call_count == 2


def test_raises_timeout_deterministically() -> None:
    provider = MockProvider(["unused"], raise_timeout=True)
    with pytest.raises(ProviderTimeoutError):
        provider.generate("x")
    assert provider.call_count == 1


def test_raises_error_deterministically() -> None:
    provider = MockProvider(["unused"], raise_error=True)
    with pytest.raises(ProviderError):
        provider.generate("x")


def test_runs_out_of_scripted_responses() -> None:
    provider = MockProvider(["only"])
    provider.generate("x")
    with pytest.raises(ProviderError):
        provider.generate("y")


def test_timeout_is_a_provider_error() -> None:
    # ProviderTimeoutError is a subclass of ProviderError (catchable together).
    assert issubclass(ProviderTimeoutError, ProviderError)
