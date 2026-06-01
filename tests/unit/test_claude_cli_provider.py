"""Unit tests: ClaudeCliProvider with subprocess.run mocked (no real CLI/LLM)."""

from __future__ import annotations

import subprocess
from typing import Any

import pytest

from agent_debate.providers.base import ProviderError, ProviderTimeoutError
from agent_debate.providers.claude_cli_provider import ClaudeCliProvider

RUN_PATH = "agent_debate.providers.claude_cli_provider.subprocess.run"


def _completed(argv: list[str], *, returncode: int = 0, stdout: str = "", stderr: str = ""):
    return subprocess.CompletedProcess(argv, returncode, stdout=stdout, stderr=stderr)


def _record(monkeypatch: pytest.MonkeyPatch, result: object) -> list[dict[str, Any]]:
    calls: list[dict[str, Any]] = []

    def fake_run(argv: list[str], **kwargs: Any) -> object:
        calls.append({"argv": list(argv), "input": kwargs.get("input")})
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(RUN_PATH, fake_run)
    return calls


def test_stdin_mode_returns_stdout(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record(monkeypatch, _completed(["claude", "-p"], stdout="  hi there \n"))
    provider = ClaudeCliProvider(["claude", "-p"], input_mode="stdin")
    assert provider.generate("prompt-x") == "hi there"
    assert calls[0]["input"] == "prompt-x"
    assert "prompt-x" not in calls[0]["argv"]


def test_argument_mode_appends_prompt(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = _record(monkeypatch, _completed(["claude"], stdout="answer"))
    provider = ClaudeCliProvider(["claude"], input_mode="argument")
    assert provider.generate("PROMPT") == "answer"
    assert calls[0]["argv"][-1] == "PROMPT"
    assert calls[0]["input"] is None


def test_nonzero_exit_raises_provider_error(monkeypatch: pytest.MonkeyPatch) -> None:
    _record(monkeypatch, _completed(["claude"], returncode=2, stdout="x"))
    with pytest.raises(ProviderError):
        ClaudeCliProvider(["claude"]).generate("p")


def test_empty_stdout_with_stderr_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    _record(monkeypatch, _completed(["claude"], stdout="   ", stderr="boom"))
    with pytest.raises(ProviderError):
        ClaudeCliProvider(["claude"]).generate("p")


def test_timeout_raises_provider_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    _record(monkeypatch, subprocess.TimeoutExpired(cmd=["claude"], timeout=1.0))
    with pytest.raises(ProviderTimeoutError):
        ClaudeCliProvider(["claude"], timeout_seconds=1.0).generate("p")


def test_call_count_increments(monkeypatch: pytest.MonkeyPatch) -> None:
    _record(monkeypatch, _completed(["claude"], stdout="ok"))
    provider = ClaudeCliProvider(["claude"])
    provider.generate("a")
    provider.generate("b")
    assert provider.call_count == 2


def test_command_list_not_mutated(monkeypatch: pytest.MonkeyPatch) -> None:
    command = ["claude", "-p"]
    _record(monkeypatch, _completed(command, stdout="ok"))
    provider = ClaudeCliProvider(command, input_mode="argument")
    provider.generate("p1")
    provider.generate("p2")
    assert command == ["claude", "-p"]


def test_invalid_input_mode_raises() -> None:
    with pytest.raises(ValueError):
        ClaudeCliProvider(["claude"], input_mode="bogus")


def test_empty_command_raises() -> None:
    with pytest.raises(ValueError):
        ClaudeCliProvider([])
