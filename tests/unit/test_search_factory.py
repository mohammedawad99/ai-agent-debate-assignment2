"""Unit tests: search factory (no web during construction)."""

from __future__ import annotations

from typing import Any

import pytest

from agent_debate.search.factory import SearchConfigError, build_search
from agent_debate.search.mock_search import MockSearchTool
from agent_debate.search.real_search import RealSearchTool

DDGS_CFG = {"active": "ddgs", "providers": {"ddgs": {"provider_name": "ddgs", "max_results": 3}}}


def _fake_backend(query: str, max_results: int) -> list[dict[str, Any]]:
    return [{"title": "T", "url": "u", "snippet": "s"}]


def test_mock_builds_mock_search() -> None:
    assert isinstance(build_search({"active": "mock"}), MockSearchTool)


def test_ddgs_builds_real_search_with_injected_backend() -> None:
    tool = build_search(DDGS_CFG, backend=_fake_backend)
    assert isinstance(tool, RealSearchTool)
    # Using the injected backend performs no web call.
    records = tool.search("q", session_id="s1", claim_id="c1")
    assert records[0].title == "T"


def test_unsupported_search_raises() -> None:
    with pytest.raises(SearchConfigError):
        build_search({"active": "nope"})
