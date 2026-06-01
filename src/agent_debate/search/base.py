"""Search tool abstraction (docs/ARCHITECTURE.md AG-5).

Orchestration depends only on this interface. A future DdgsSearchTool will implement
`search` over a no-key web API; it is NOT implemented here. Retrieved content is
untrusted data (SR-3/SR-4). No network/search logic lives in this module.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from agent_debate.protocol.models import EvidenceRecord


class SearchError(RuntimeError):
    """A search call failed (controlled, non-fatal to the suite)."""


class SearchTool(ABC):
    """Minimal contract: return evidence records for a query/claim/session."""

    @abstractmethod
    def search(self, query: str, *, session_id: str, claim_id: str) -> list[EvidenceRecord]:
        """Return evidence records supporting `claim_id` in `session_id`.

        Implementations may raise SearchError.
        """

    @property
    @abstractmethod
    def call_count(self) -> int:
        """Number of search() calls made so far."""
