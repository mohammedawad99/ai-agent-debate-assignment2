"""ClaudeCliProvider (Phase 6.3b) — real provider behind ProviderAdapter.

Invokes a configurable, login-based CLI (e.g. the Claude CLI) via `subprocess.run`.
This is the ONLY production module permitted to import `subprocess` in this phase.
It holds no secrets, hardcodes no user paths, applies a timeout, and never prints the
environment. Tests mock `subprocess.run`; no real CLI/LLM is invoked by the suite.
"""

from __future__ import annotations

import subprocess

from agent_debate.providers.base import (
    ProviderAdapter,
    ProviderError,
    ProviderTimeoutError,
)

INPUT_MODES = ("stdin", "argument")


class ClaudeCliProvider(ProviderAdapter):
    def __init__(
        self,
        command: list[str],
        *,
        timeout_seconds: float = 120.0,
        input_mode: str = "stdin",
    ) -> None:
        if not command:
            raise ValueError("command must be a non-empty list")
        if input_mode not in INPUT_MODES:
            raise ValueError(f"input_mode must be one of {INPUT_MODES}, got {input_mode!r}")
        # Copy so the caller's list is never mutated across calls.
        self._command = list(command)
        self._timeout_seconds = timeout_seconds
        self._input_mode = input_mode
        self._call_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def generate(self, prompt: str) -> str:
        self._call_count += 1
        argv = list(self._command)
        stdin_text: str | None = None
        if self._input_mode == "argument":
            argv.append(prompt)
        else:
            stdin_text = prompt
        try:
            completed = subprocess.run(
                argv,
                input=stdin_text,
                text=True,
                capture_output=True,
                timeout=self._timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise ProviderTimeoutError(
                f"provider timed out after {self._timeout_seconds}s"
            ) from exc
        return self._handle(completed)

    def _handle(self, completed: subprocess.CompletedProcess[str]) -> str:
        if completed.returncode != 0:
            raise ProviderError(f"provider exited with code {completed.returncode}")
        stdout = (completed.stdout or "").strip()
        if not stdout:
            if (completed.stderr or "").strip():
                raise ProviderError("provider produced no stdout (stderr present)")
            raise ProviderError("provider produced empty output")
        return stdout
