"""Unit tests: Pro/Con agents build valid turns and do not reference each other."""

from __future__ import annotations

from agent_debate.agents.debate_agent import ConAgent, ProAgent
from agent_debate.evidence.store import EvidenceStore
from agent_debate.providers.mock_provider import MockProvider
from agent_debate.search.mock_search import MockSearchTool


def _pro() -> ProAgent:
    return ProAgent(MockProvider(["Pro argument text here."]), MockSearchTool())


def test_roles() -> None:
    assert ProAgent(MockProvider([]), MockSearchTool()).role == "pro"
    assert ConAgent(MockProvider([]), MockSearchTool()).role == "con"


def test_produce_opening_has_no_opponent_ref() -> None:
    store = EvidenceStore()
    msg = _pro().produce(
        session_id="s1",
        round_index=0,
        turn_index=0,
        claim_id="c-pro-0",
        opponent_claim_id=None,
        store=store,
    )
    assert msg["turn_type"] == "opening_argument"
    assert "opponent_claim_id" not in msg
    assert msg["evidence_refs"] and len(store) == 1


def test_produce_rebuttal_has_opponent_ref() -> None:
    store = EvidenceStore()
    msg = _pro().produce(
        session_id="s1",
        round_index=1,
        turn_index=2,
        claim_id="c-pro-2",
        opponent_claim_id="c-con-1",
        store=store,
    )
    assert msg["turn_type"] == "rebuttal"
    assert msg["opponent_claim_id"] == "c-con-1"


def test_agents_do_not_reference_each_other() -> None:
    pro = _pro()
    con = ConAgent(MockProvider(["Con argument text here."]), MockSearchTool())
    assert all(con is not value for value in vars(pro).values())
    assert all(pro is not value for value in vars(con).values())
