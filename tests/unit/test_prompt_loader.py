"""Unit tests: project-local prompt loader + config references."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_debate.prompts.loader import PromptError, load_prompt

ROOT = Path(__file__).resolve().parents[2]
PROMPTS = ROOT / "prompts"
PROMPT_FILES = [
    "agents/judge.md",
    "agents/pro.md",
    "agents/con.md",
    "protocol/regeneration.md",
    "protocol/final_judgment.md",
]


def test_loads_local_prompt() -> None:
    assert "Judge" in load_prompt("agents/judge.md", PROMPTS)


@pytest.mark.parametrize("path", PROMPT_FILES)
def test_all_prompt_files_exist(path: str) -> None:
    assert load_prompt(path, PROMPTS).strip()


def test_absolute_path_rejected() -> None:
    with pytest.raises(PromptError):
        load_prompt("/etc/passwd", PROMPTS)


def test_path_traversal_rejected() -> None:
    with pytest.raises(PromptError):
        load_prompt("../config/agents.json", PROMPTS)


def test_missing_prompt_raises() -> None:
    with pytest.raises(PromptError):
        load_prompt("agents/missing.md", PROMPTS)


def test_config_references_existing_prompts() -> None:
    agents = json.loads((ROOT / "config" / "agents.json").read_text(encoding="utf-8"))
    base = ROOT / agents["prompts_dir"]
    referenced = [role["prompt_template"] for role in agents["roles"].values()]
    referenced += list(agents["protocol_prompts"].values())
    for rel in referenced:
        assert not Path(rel).is_absolute()
        assert (base / rel).is_file(), rel
