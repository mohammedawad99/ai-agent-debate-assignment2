"""ddgs search backend (Phase 6.3d) — lazy, optional, no project dependency.

Adapts results from the optional `ddgs` library into the {title, url, snippet} dicts
that RealSearchTool expects. `ddgs` is imported LAZILY inside `_default_client` and is
NOT a declared dependency; if it is missing, a clear SearchError is raised. Tests
inject a fake `client_factory`, so they exercise the mapping with no `ddgs` and no web.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from agent_debate.search.base import SearchError

ClientFactory = Callable[[], Any]


def _default_client() -> Any:
    try:
        from ddgs import DDGS
    except ImportError as exc:
        raise SearchError("ddgs is not installed; install it to use real search") from exc
    return DDGS()  # pragma: no cover - requires the optional dependency


def ddgs_search(
    query: str, max_results: int, *, client_factory: ClientFactory | None = None
) -> list[dict[str, Any]]:
    factory = client_factory or _default_client
    client = factory()
    raw = client.text(query, max_results=max_results)
    return [
        {
            "title": item.get("title", ""),
            "url": item.get("href") or item.get("url") or "",
            "snippet": item.get("body") or item.get("snippet") or "",
        }
        for item in raw
    ]
