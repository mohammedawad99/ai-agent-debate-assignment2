"""Unit tests: ddgs backend mapping (fake client; no ddgs install, no web)."""

from __future__ import annotations

from typing import Any

import pytest

from agent_debate.search.base import SearchError
from agent_debate.search.ddgs_backend import ddgs_search


class _FakeClient:
    def __init__(self, items: list[dict[str, Any]]) -> None:
        self._items = items

    def text(self, query: str, max_results: int) -> list[dict[str, Any]]:
        return self._items


def test_maps_ddgs_fields_to_dict_shape() -> None:
    items = [{"title": "Title", "href": "https://x.example", "body": "Body text."}]
    result = ddgs_search("q", 5, client_factory=lambda: _FakeClient(items))
    assert result == [{"title": "Title", "url": "https://x.example", "snippet": "Body text."}]


def test_missing_ddgs_raises_search_error() -> None:
    # No client_factory -> lazy import of `ddgs`, which is not installed -> SearchError.
    with pytest.raises(SearchError):
        ddgs_search("q", 1)
