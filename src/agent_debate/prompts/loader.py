"""Project-local prompt loader (Phase 6.4).

Loads prompt templates from the project-relative `prompts/` directory. Absolute paths
and `..` traversal are rejected; a clear PromptError is raised when a prompt is
missing. No code execution, no network, no secrets.
"""

from __future__ import annotations

from pathlib import Path

DEFAULT_PROMPTS_DIR = Path("prompts")


class PromptError(ValueError):
    """A prompt could not be loaded or rendered."""


def load_prompt(relative_path: str, prompts_dir: Path | None = None) -> str:
    """Load a prompt template by a path relative to the prompts directory."""
    base = prompts_dir or DEFAULT_PROMPTS_DIR
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise PromptError(f"absolute prompt paths are not allowed: {relative_path}")
    if ".." in candidate.parts:
        raise PromptError(f"path traversal is not allowed: {relative_path}")
    full = base / candidate
    if not full.is_file():
        raise PromptError(f"missing prompt template: {relative_path}")
    return full.read_text(encoding="utf-8")
