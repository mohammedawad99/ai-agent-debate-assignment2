"""Unit tests: scoring rubric and deterministic tie-break."""

from __future__ import annotations

import pytest

from agent_debate.results import tie_breaker
from agent_debate.results.scoring import build_score

PRIORITY = ["con", "pro"]


def test_total_is_sum() -> None:
    assert build_score(5, 4, 3, 2, 1, 0).total == 15


def test_out_of_range_raises() -> None:
    with pytest.raises(ValueError):
        build_score(6, 0, 0, 0, 0, 0)


def test_total_decides_no_tiebreak() -> None:
    out = tie_breaker.decide(build_score(5, 5, 5, 5, 5, 5), build_score(1, 1, 1, 1, 1, 1), PRIORITY)
    assert out.winner_role == "pro"
    assert out.tie_break_used is False


def test_evidence_quality_breaks_tie() -> None:
    pro = build_score(4, 4, 5, 4, 4, 3)
    con = build_score(4, 4, 3, 4, 4, 5)
    out = tie_breaker.decide(pro, con, PRIORITY)
    assert out.winner_role == "pro"
    assert out.tie_break_reason == "evidence_quality"


def test_responsiveness_breaks_tie() -> None:
    pro = build_score(4, 5, 4, 4, 4, 3)
    con = build_score(4, 3, 4, 4, 4, 5)
    out = tie_breaker.decide(pro, con, PRIORITY)
    assert out.winner_role == "pro"
    assert out.tie_break_reason == "responsiveness"


def test_fewer_violations_breaks_tie() -> None:
    pro = build_score(4, 4, 4, 4, 4, 4, protocol_violations=0)
    con = build_score(4, 4, 4, 4, 4, 4, protocol_violations=2)
    out = tie_breaker.decide(pro, con, PRIORITY)
    assert out.winner_role == "pro"
    assert out.tie_break_reason == "fewer_violations"


def test_regen_count_breaks_tie() -> None:
    pro = build_score(4, 4, 4, 4, 4, 4, regeneration_count=1)
    con = build_score(4, 4, 4, 4, 4, 4, regeneration_count=0)
    assert tie_breaker.decide(pro, con, PRIORITY).winner_role == "con"


def test_configured_priority_on_full_tie() -> None:
    score = build_score(4, 4, 4, 4, 4, 4)
    out = tie_breaker.decide(score, score, PRIORITY)
    assert out.winner_role == "con"
    assert out.tie_break_reason == "configured_priority"


def test_invalid_priority_raises() -> None:
    score = build_score(4, 4, 4, 4, 4, 4)
    with pytest.raises(tie_breaker.TieBreakError):
        tie_breaker.decide(score, score, ["nobody"])
