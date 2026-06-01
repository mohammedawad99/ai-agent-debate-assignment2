"""EvidenceStore (docs/PROTOCOL.md §5).

In-memory store of evidence records keyed by id. Supports reuse (look up an
existing item by id across turns). No network/IO here.
"""

from __future__ import annotations

from agent_debate.protocol.models import EvidenceRecord


class EvidenceStore:
    def __init__(self) -> None:
        self._items: dict[str, EvidenceRecord] = {}

    def add(self, record: EvidenceRecord) -> None:
        self._items[record.evidence_id] = record

    def get(self, evidence_id: str) -> EvidenceRecord | None:
        return self._items.get(evidence_id)

    def exists(self, evidence_id: str) -> bool:
        return evidence_id in self._items

    def __len__(self) -> int:
        return len(self._items)
