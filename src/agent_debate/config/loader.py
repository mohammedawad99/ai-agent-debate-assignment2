"""Config loading (docs/CONFIGURATION.md).

JSON only, relative paths, no secrets. Loads the debate parameters used by the
offline core slice and validates the values it relies on.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_CONFIG_DIR = Path("config")


class ConfigError(ValueError):
    pass


@dataclass
class DebateConfig:
    topic: str
    turns_per_side: dict[str, int]
    child_word_limit: int
    judge_word_limit: int
    retry_cap: int
    final_tie_break_priority: list[str]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ConfigError(f"missing config file: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc


def load_raw_config(name: str, config_dir: Path | None = None) -> dict[str, Any]:
    """Load a config JSON file (e.g. 'providers.json') from the config dir."""
    base = config_dir or DEFAULT_CONFIG_DIR
    return _read_json(base / name)


def load_debate_config(config_dir: Path | None = None) -> DebateConfig:
    base = config_dir or DEFAULT_CONFIG_DIR
    data = _read_json(base / "debate.json")
    try:
        cfg = DebateConfig(
            topic=str(data["topic"]),
            turns_per_side={k: int(v) for k, v in data["turns_per_side"].items()},
            child_word_limit=int(data["word_limits"]["child_turn_max_words"]),
            judge_word_limit=int(data["word_limits"]["judge_decision_max_words"]),
            retry_cap=int(data["retry_cap"]),
            final_tie_break_priority=list(data["final_tie_break_priority"]),
        )
    except (KeyError, TypeError, ValueError) as exc:
        raise ConfigError(f"invalid debate.json structure: {exc}") from exc
    _validate(cfg)
    return cfg


def _validate(cfg: DebateConfig) -> None:
    if cfg.child_word_limit <= 0 or cfg.judge_word_limit <= 0:
        raise ConfigError("word limits must be positive")
    if cfg.retry_cap < 0:
        raise ConfigError("retry_cap must be >= 0")
    if not cfg.final_tie_break_priority:
        raise ConfigError("final_tie_break_priority must be non-empty")
    if "full" not in cfg.turns_per_side:
        raise ConfigError("turns_per_side.full required")
