"""RealSearchTool (Phase 6.3c) — real search provider behind SearchTool.

Converts raw web-search results into EvidenceRecord objects. It depends on an
INJECTED `backend` callable (query, max_results) -> list[dict], rather than importing
a web library directly. This keeps the adapter real while staying fully offline-
testable (tests inject a fake backend) and avoids a heavy/network dependency in the
test environment. A concrete `ddgs`-backed backend is wired in a later phase.

Retrieved content is UNTRUSTED evidence data (SR-3/SR-4): it is stored as data only
and never interpreted as instructions. relevance_status is set conservatively to
"relevant" (it was returned for the claim query); deeper relevance is Judge-level.
"""

from __future__ import annotations

import datetime
from collections.abc import Callable
from typing import Any

from agent_debate.protocol.models import EvidenceRecord
from agent_debate.search.base import SearchError, SearchTool

SearchBackend = Callable[[str, int], list[dict[str, Any]]]


def _utc_now() -> str:
    return datetime.datetime.now(datetime.UTC).isoformat()


class RealSearchTool(SearchTool):
    def __init__(
        self,
        backend: SearchBackend,
        *,
        provider_name: str = "ddgs",
        max_results: int = 5,
        clock: Callable[[], str] = _utc_now,
    ) -> None:
        self._backend = backend
        self._provider_name = provider_name
        self._max_results = max_results
        self._clock = clock
        self._call_count = 0

    @property
    def call_count(self) -> int:
        return self._call_count

    def search(self, query: str, *, session_id: str, claim_id: str) -> list[EvidenceRecord]:
        self._call_count += 1
        try:
            raw = self._backend(query, self._max_results)
        except Exception as exc:  # wrap any backend failure as a controlled SearchError
            raise SearchError(f"search backend failed: {exc}") from exc
        return [
            self._to_record(item, rank, query, session_id, claim_id)
            for rank, item in enumerate(raw, start=1)
        ]

    def _to_record(
        self, item: dict[str, Any], rank: int, query: str, session_id: str, claim_id: str
    ) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=f"ev-{self._call_count}-{rank}",
            session_id=session_id,
            source_type="web",
            title=str(item.get("title", "")),
            url=str(item.get("href") or item.get("url") or ""),
            snippet=str(item.get("body") or item.get("snippet") or ""),
            retrieved_at=self._clock(),
            query=query,
            supports_claim_id=claim_id,
            relevance_status="relevant",
            provider_name=self._provider_name,
            rank=rank,
        )
