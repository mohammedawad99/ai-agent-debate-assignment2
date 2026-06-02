"""Unit tests: tolerant-but-strict provider judgment parsing (no real Claude/web)."""

from __future__ import annotations

import pytest

from agent_debate.results.scoring import JudgeError, parse_judgment

VALID = '{"winner_role": "pro", "loser_role": "con", "reasoning": "Pro was clearer."}'
SECOND = '{"winner_role": "con", "loser_role": "pro", "reasoning": "Con wins."}'


def test_direct_json_parses() -> None:
    assert parse_judgment(VALID)["winner_role"] == "pro"


def test_fenced_json_with_lang_parses() -> None:
    assert parse_judgment("```json\n" + VALID + "\n```")["winner_role"] == "pro"


def test_fenced_json_no_lang_parses() -> None:
    assert parse_judgment("```\n" + VALID + "\n```")["loser_role"] == "con"


def test_one_object_amid_prose_parses() -> None:
    assert parse_judgment("Here is my verdict:\n" + VALID + "\nThanks!")["winner_role"] == "pro"


def test_prose_without_json_rejected() -> None:
    with pytest.raises(JudgeError):
        parse_judgment("The winner is clearly Pro. No object here.")


def test_multiple_objects_rejected_as_ambiguous() -> None:
    with pytest.raises(JudgeError):
        parse_judgment(VALID + "\n" + SECOND)


def test_invalid_winner_role_rejected() -> None:
    with pytest.raises(JudgeError):
        parse_judgment('{"winner_role": "maybe", "loser_role": "con", "reasoning": "x"}')


def test_tie_or_same_winner_loser_rejected() -> None:
    with pytest.raises(JudgeError):
        parse_judgment('{"winner_role": "pro", "loser_role": "pro", "reasoning": "x"}')


def test_empty_reasoning_rejected() -> None:
    with pytest.raises(JudgeError):
        parse_judgment('{"winner_role": "pro", "loser_role": "con", "reasoning": ""}')


def test_scores_out_of_range_rejected() -> None:
    raw = (
        '{"winner_role": "pro", "loser_role": "con", "reasoning": "ok",'
        ' "scores": {"pro": {"clarity": 9}}}'
    )
    with pytest.raises(JudgeError):
        parse_judgment(raw)
