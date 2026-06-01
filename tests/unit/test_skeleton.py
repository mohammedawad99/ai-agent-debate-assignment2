"""Skeleton import test.

This ONLY verifies that the package skeleton imports cleanly. It deliberately does
NOT assert that any debate/agent/provider/search functionality exists — none does
yet (Phase 4). Behavioral tests arrive in Phase 5 (TDD).
"""

from __future__ import annotations

import importlib

import pytest

SUBPACKAGES = [
    "agent_debate",
    "agent_debate.cli",
    "agent_debate.sdk",
    "agent_debate.orchestration",
    "agent_debate.agents",
    "agent_debate.protocol",
    "agent_debate.validation",
    "agent_debate.providers",
    "agent_debate.search",
    "agent_debate.evidence",
    "agent_debate.config",
    "agent_debate.logging",
    "agent_debate.results",
    "agent_debate.quality",
]


@pytest.mark.parametrize("module_name", SUBPACKAGES)
def test_subpackage_imports(module_name: str) -> None:
    """Every declared subpackage imports without error."""
    assert importlib.import_module(module_name) is not None


def test_version_is_exposed() -> None:
    """The package exposes a version string."""
    import agent_debate

    assert isinstance(agent_debate.__version__, str)


def test_cli_entrypoint_is_wired() -> None:
    """The CLI entry point exists and is wired to argparse (Phase 6.3a).

    With no subcommand, argparse exits (SystemExit) — confirming the real CLI
    rather than the old placeholder. Behavior is covered in tests/unit/test_cli.py.
    """
    from agent_debate.cli.main import main

    with pytest.raises(SystemExit):
        main([])
