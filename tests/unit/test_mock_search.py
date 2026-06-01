"""Unit tests: deterministic offline MockSearchTool."""

from __future__ import annotations

import pytest

from agent_debate.search.base import SearchError
from agent_debate.search.mock_search import INJECTION_SNIPPET, MockSearchTool

SESSION = "s1"
CLAIM = "c-pro-1"


def test_returns_relevant_evidence() -> None:
    records = MockSearchTool(mode="relevant").search("q", session_id=SESSION, claim_id=CLAIM)
    assert len(records) == 1
    assert records[0].relevance_status == "relevant"


def test_returns_irrelevant_evidence() -> None:
    records = MockSearchTool(mode="irrelevant").search("q", session_id=SESSION, claim_id=CLAIM)
    assert records[0].relevance_status == "irrelevant"


def test_evidence_has_session_and_claim() -> None:
    record = MockSearchTool().search("q", session_id=SESSION, claim_id=CLAIM)[0]
    assert record.session_id == SESSION
    assert record.supports_claim_id == CLAIM


def test_malicious_snippet_is_plain_data() -> None:
    record = MockSearchTool(mode="malicious").search("q", session_id=SESSION, claim_id=CLAIM)[0]
    # The instruction-like text is stored verbatim as DATA; it carries no authority.
    assert record.snippet == INJECTION_SNIPPET
    assert record.relevance_status == "relevant"


def test_call_count_increments() -> None:
    tool = MockSearchTool()
    assert tool.call_count == 0
    tool.search("q", session_id=SESSION, claim_id=CLAIM)
    tool.search("q2", session_id=SESSION, claim_id=CLAIM)
    assert tool.call_count == 2


def test_raises_search_error_deterministically() -> None:
    tool = MockSearchTool(raise_error=True)
    with pytest.raises(SearchError):
        tool.search("q", session_id=SESSION, claim_id=CLAIM)


def test_unknown_mode_rejected() -> None:
    with pytest.raises(ValueError):
        MockSearchTool(mode="bogus")
