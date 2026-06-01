"""Provider factory (Phase 6.3d).

Builds a ProviderAdapter from provider config. Supported `active` modes: `mock`
(MockProvider, used by default) and `claude_cli` (ClaudeCliProvider). It combines
config `command` + `args` into the command list and never executes Claude during
construction. Raises ProviderConfigError on unsupported names or invalid config.
"""

from __future__ import annotations

from typing import Any

from agent_debate.providers.base import ProviderAdapter
from agent_debate.providers.claude_cli_provider import ClaudeCliProvider
from agent_debate.providers.mock_provider import MockProvider


class ProviderConfigError(ValueError):
    """Provider config is unsupported or malformed."""


def build_provider(
    config: dict[str, Any], *, responses: list[str] | None = None
) -> ProviderAdapter:
    name = config.get("active")
    if name == "mock":
        return MockProvider(responses or [])
    if name == "claude_cli":
        try:
            spec = config["providers"]["claude_cli"]
            command = list(spec["command"]) + list(spec.get("args", []))
        except (KeyError, TypeError) as exc:
            raise ProviderConfigError(f"invalid claude_cli config: {exc}") from exc
        if not command:
            raise ProviderConfigError("claude_cli command must be non-empty")
        return ClaudeCliProvider(
            command,
            timeout_seconds=float(spec.get("timeout_seconds", 120)),
            input_mode=str(spec.get("input_mode", "stdin")),
        )
    raise ProviderConfigError(f"unsupported provider: {name!r}")
