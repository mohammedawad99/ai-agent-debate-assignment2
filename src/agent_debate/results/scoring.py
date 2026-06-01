"""Scoring rubric (docs/SCORING_AND_VALIDATION.md §7-8).

Six dimensions on a 0-5 integer scale, equal weight, total = sum (max 30).
"""

from __future__ import annotations

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
