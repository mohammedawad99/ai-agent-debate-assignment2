"""Scoring rubric + provider-judgment parsing (docs/SCORING_AND_VALIDATION.md §7-9).

Six 0-5 dimensions, equal weight. `parse_judgment` tolerantly extracts then strictly
validates a provider final-judgment JSON object (code fence / one object amid prose; no eval).
"""

from __future__ import annotations

import json
from typing import Any

from agent_debate.protocol.models import JudgeScore

DIMENSIONS = (
    "clarity",
    "responsiveness",
    "evidence_quality",
    "position_consistency",
    "respectful_tone",
    "persuasive_force",
)
SCALE_MIN = 0
SCALE_MAX = 5
FINALISTS = ("pro", "con")


class JudgeError(ValueError):
    """A provider-backed final judgment was missing or malformed."""


def _check(name: str, value: int) -> None:
    if not (SCALE_MIN <= value <= SCALE_MAX):
        raise ValueError(f"{name}={value} out of range {SCALE_MIN}-{SCALE_MAX}")


def build_score(
    clarity: int,
    responsiveness: int,
    evidence_quality: int,
    position_consistency: int,
    respectful_tone: int,
    persuasive_force: int,
    protocol_violations: int = 0,
    regeneration_count: int = 0,
) -> JudgeScore:
    dims = {
        "clarity": clarity,
        "responsiveness": responsiveness,
        "evidence_quality": evidence_quality,
        "position_consistency": position_consistency,
        "respectful_tone": respectful_tone,
        "persuasive_force": persuasive_force,
    }
    for name, value in dims.items():
        _check(name, value)
    return JudgeScore(
        clarity=clarity,
        responsiveness=responsiveness,
        evidence_quality=evidence_quality,
        position_consistency=position_consistency,
        respectful_tone=respectful_tone,
        persuasive_force=persuasive_force,
        total=sum(dims.values()),
        protocol_violations=protocol_violations,
        regeneration_count=regeneration_count,
    )


def _extract_json_object(raw: str) -> Any:
    """Tolerate a code fence or one JSON object amid prose; reject 0 or >1 (no eval)."""
    text = raw.strip()
    if text.startswith("```"):
        body = text.splitlines()[1:]
        if body and body[-1].strip() == "```":
            body = body[:-1]
        text = "\n".join(body).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    decoder = json.JSONDecoder()
    found: list[Any] = []
    i = 0
    while i < len(text):
        if text[i] == "{":
            try:
                obj, end = decoder.raw_decode(text, i)
                found.append(obj)
                i = end
                continue
            except json.JSONDecodeError:
                pass
        i += 1
    if not found:
        raise JudgeError("judge output contains no parseable JSON object")
    if len(found) > 1:
        raise JudgeError("judge output is ambiguous (multiple JSON objects)")
    return found[0]


def parse_judgment(raw: str) -> dict[str, Any]:
    """Parse + validate a provider final-judgment JSON object (tolerant). Raises JudgeError."""
    data = _extract_json_object(raw)
    if not isinstance(data, dict):
        raise JudgeError("judge output is not a JSON object")
    winner = data.get("winner_role")
    if winner not in FINALISTS:
        raise JudgeError(f"winner_role must be 'pro' or 'con', got {winner!r}")
    if data.get("loser_role") != ("con" if winner == "pro" else "pro"):
        raise JudgeError("loser_role must be the opposite of winner_role")
    if not str(data.get("reasoning", "")).strip():
        raise JudgeError("reasoning is required")
    _check_dimension_scores(data.get("scores"))
    return data


def _check_dimension_scores(scores: Any) -> None:
    if not isinstance(scores, dict):
        return
    for side in scores.values():
        if not isinstance(side, dict):
            continue
        for dim in DIMENSIONS:
            value = side.get(dim)
            if isinstance(value, int) and not (SCALE_MIN <= value <= SCALE_MAX):
                raise JudgeError(f"score {dim}={value} out of {SCALE_MIN}-{SCALE_MAX}")


def scores_from_data(scores: Any) -> dict[str, JudgeScore]:
    by_side = scores if isinstance(scores, dict) else {}
    return {side: _one_score(by_side.get(side)) for side in FINALISTS}


def _one_score(side: Any) -> JudgeScore:
    def value(key: str) -> int:
        raw = side.get(key) if isinstance(side, dict) else None
        return raw if isinstance(raw, int) and SCALE_MIN <= raw <= SCALE_MAX else 3

    return build_score(
        value("clarity"),
        value("responsiveness"),
        value("evidence_quality"),
        value("position_consistency"),
        value("respectful_tone"),
        value("persuasive_force"),
    )
