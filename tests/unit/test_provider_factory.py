"""Unit tests: provider factory (no Claude execution)."""

from __future__ import annotations

import pytest

from agent_debate.providers.claude_cli_provider import ClaudeCliProvider
from agent_debate.providers.factory import ProviderConfigError, build_provider
from agent_debate.providers.mock_provider import MockProvider

CLAUDE_CFG = {
    "active": "claude_cli",
    "providers": {
        "claude_cli": {
            "command": ["claude"],
            "args": ["-p"],
            "input_mode": "stdin",
            "timeout_seconds": 30,
        }
    },
}


def test_mock_builds_mock_provider() -> None:
    provider = build_provider({"active": "mock", "providers": {}}, responses=["x"])
    assert isinstance(provider, MockProvider)


def test_claude_cli_combines_command_and_args() -> None:
    provider = build_provider(CLAUDE_CFG)
    assert isinstance(provider, ClaudeCliProvider)
    # Combined command list, not executed.
    assert provider._command == ["claude", "-p"]


def test_unsupported_provider_raises() -> None:
    with pytest.raises(ProviderConfigError):
        build_provider({"active": "wat", "providers": {}})


def test_invalid_claude_cli_config_raises() -> None:
    with pytest.raises(ProviderConfigError):
        build_provider({"active": "claude_cli", "providers": {"claude_cli": {}}})
