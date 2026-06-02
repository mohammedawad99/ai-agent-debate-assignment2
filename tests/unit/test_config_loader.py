"""Unit tests: config loading and validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_debate.config.loader import ConfigError, load_debate_config

ROOT = Path(__file__).resolve().parents[2]


def test_load_real_config() -> None:
    cfg = load_debate_config(ROOT / "config")
    assert cfg.turns_per_side["full"] == 10
    assert cfg.child_word_limit == 220  # raised 160 -> 220 in Phase 7.4
    assert cfg.judge_word_limit == 400
    assert cfg.retry_cap == 2
    assert cfg.final_tie_break_priority == ["con", "pro"]


def test_missing_file_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_debate_config(tmp_path)


def _write(tmp_path: Path, payload: object) -> Path:
    (tmp_path / "debate.json").write_text(json.dumps(payload), encoding="utf-8")
    return tmp_path


def test_invalid_structure_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigError):
        load_debate_config(_write(tmp_path, {"topic": "t"}))


def test_bad_values_raise(tmp_path: Path) -> None:
    payload = {
        "topic": "t",
        "turns_per_side": {"full": 10},
        "word_limits": {"child_turn_max_words": 0, "judge_decision_max_words": 400},
        "retry_cap": 2,
        "final_tie_break_priority": ["con", "pro"],
    }
    with pytest.raises(ConfigError):
        load_debate_config(_write(tmp_path, payload))


def test_invalid_json_raises(tmp_path: Path) -> None:
    (tmp_path / "debate.json").write_text("{bad", encoding="utf-8")
    with pytest.raises(ConfigError):
        load_debate_config(tmp_path)


def _valid_payload() -> dict[str, object]:
    return {
        "topic": "t",
        "turns_per_side": {"full": 10},
        "word_limits": {"child_turn_max_words": 160, "judge_decision_max_words": 400},
        "retry_cap": 2,
        "final_tie_break_priority": ["con", "pro"],
    }


def test_negative_retry_cap_raises(tmp_path: Path) -> None:
    payload = _valid_payload() | {"retry_cap": -1}
    with pytest.raises(ConfigError):
        load_debate_config(_write(tmp_path, payload))


def test_empty_priority_raises(tmp_path: Path) -> None:
    payload = _valid_payload() | {"final_tie_break_priority": []}
    with pytest.raises(ConfigError):
        load_debate_config(_write(tmp_path, payload))


def test_missing_full_turns_raises(tmp_path: Path) -> None:
    payload = _valid_payload() | {"turns_per_side": {"dev": 3}}
    with pytest.raises(ConfigError):
        load_debate_config(_write(tmp_path, payload))
