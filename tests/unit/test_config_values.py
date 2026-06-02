"""Quality tests: config files parse and key values match approved decisions.

No business logic — these assert the configuration templates only. Values mirror
the decisions in docs/PRD.md, docs/PLAN.md, and docs/SCORING_AND_VALIDATION.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"


def _load(name: str) -> dict[str, Any]:
    return json.loads((CONFIG / name).read_text(encoding="utf-8"))


def test_all_config_json_parse() -> None:
    files = sorted(CONFIG.glob("*.json"))
    assert files, "no config json found"
    for path in files:
        json.loads(path.read_text(encoding="utf-8"))


def test_final_tie_break_priority() -> None:
    assert _load("debate.json")["final_tie_break_priority"] == ["con", "pro"]


def test_retry_cap_is_two() -> None:
    assert _load("debate.json")["retry_cap"] == 2


def test_child_word_limit_is_220() -> None:
    # Raised 160 -> 220 in Phase 7.4 after the first real run failed on word_limit_exceeded.
    assert _load("debate.json")["word_limits"]["child_turn_max_words"] == 220


def test_judge_word_limit_is_400() -> None:
    assert _load("debate.json")["word_limits"]["judge_decision_max_words"] == 400


def test_target_turns_per_side_is_10() -> None:
    assert _load("debate.json")["turns_per_side"]["full"] == 10
