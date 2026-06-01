"""Search factory (Phase 6.3d).

Builds a SearchTool from search config. Supported `active` modes: `mock`
(MockSearchTool, used by default) and `ddgs`/`real_search` (RealSearchTool with the
lazy `ddgs_search` backend). Construction performs NO web call — the ddgs backend
imports `ddgs` only when actually invoked. Raises SearchConfigError on unsupported
names.
"""

from __future__ import annotations

from typing import Any

from agent_debate.search.base import SearchTool
from agent_debate.search.ddgs_backend import ddgs_search
from agent_debate.search.mock_search import MockSearchTool
from agent_debate.search.real_search import RealSearchTool, SearchBackend


class SearchConfigError(ValueError):
    """Search config is unsupported or malformed."""


def build_search(config: dict[str, Any], *, backend: SearchBackend | None = None) -> SearchTool:
    name = config.get("active")
    if name == "mock":
        return MockSearchTool()
    if name in ("ddgs", "real_search"):
        spec = config.get("providers", {}).get("ddgs", {})
        chosen: SearchBackend = backend or ddgs_search
        return RealSearchTool(
            chosen,
            provider_name=str(spec.get("provider_name", "ddgs")),
            max_results=int(spec.get("max_results", 5)),
        )
    raise SearchConfigError(f"unsupported search provider: {name!r}")
