"""Unit tests: prompt renderer + required protocol terms in templates."""

from __future__ import annotations

from pathlib import Path

import pytest

from agent_debate.prompts.loader import PromptError, load_prompt
from agent_debate.prompts.templates import render

PROMPTS = Path(__file__).resolve().parents[2] / "prompts"


def test_render_fills_placeholders() -> None:
    assert render("Topic {topic}, role={role}", topic="X", role="pro") == "Topic X, role=pro"


def test_render_no_placeholders_unchanged() -> None:
    assert render("plain text with no tokens") == "plain text with no tokens"


def test_render_missing_value_raises() -> None:
    with pytest.raises(PromptError):
        render("Hello {name}")


def test_render_ignores_json_like_braces() -> None:
    # A JSON-ish brace (not a bare {word}) is left untouched.
    assert render('{"k": 1} and {topic}', topic="T") == '{"k": 1} and T'


def test_judge_prompt_has_required_terms() -> None:
    text = load_prompt("agents/judge.md", PROMPTS)
    for term in (
        "JSON",
        "evidence_refs",
        "opponent_claim_id",
        "exactly one winner",
        "tie is not allowed",
        "untrusted",
        "tie-break",
    ):
        assert term in text


def test_pro_and_con_prompts_have_required_terms() -> None:
    pro = load_prompt("agents/pro.md", PROMPTS)
    con = load_prompt("agents/con.md", PROMPTS)
    for text in (pro, con):
        assert "JSON" in text
        assert "evidence_refs" in text
        assert "opponent_claim_id" in text
        assert "respectful" in text
        assert "Do not agree" in text


def test_regeneration_prompt_has_required_terms() -> None:
    text = load_prompt("protocol/regeneration.md", PROMPTS)
    assert "validation_errors" in text
    assert "corrected JSON" in text
    assert "assigned role and side" in text


def test_final_judgment_prompt_has_required_terms() -> None:
    text = load_prompt("protocol/final_judgment.md", PROMPTS)
    assert "rubric" in text
    assert "exactly one winner" in text
    assert "no tie" in text
    assert "tie-break" in text
