"""Unit tests: ddgs backend mapping (fake/blocked client; no live web query)."""

from __future__ import annotations

import importlib.util
import sys
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


def test_missing_ddgs_raises_search_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Block the lazy `ddgs` import (sys.modules[...] = None -> ImportError) so the clean
    # SearchError path is exercised WITHOUT building a real client or hitting the web.
    monkeypatch.setitem(sys.modules, "ddgs", None)
    with pytest.raises(SearchError):
        ddgs_search("q", 1)


def test_ddgs_is_installed_import_only() -> None:
    # Phase 6.8: ddgs is now a declared dependency. Import-availability only — no DDGS()
    # instance is created and no query is run (live search is reserved for Phase 7).
    assert importlib.util.find_spec("ddgs") is not None
