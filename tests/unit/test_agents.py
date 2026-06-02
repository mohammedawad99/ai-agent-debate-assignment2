"""Unit tests: Pro/Con agents build valid turns, render local prompts, no cross-ref."""

from __future__ import annotations

from pathlib import Path

from agent_debate.agents.debate_agent import ConAgent, ProAgent
from agent_debate.agents.judge import JudgeAgent
from agent_debate.evidence.store import EvidenceStore
from agent_debate.prompts.loader import load_prompt
from agent_debate.providers.base import ProviderAdapter
from agent_debate.providers.mock_provider import MockProvider
from agent_debate.search.mock_search import MockSearchTool

PROMPTS = Path(__file__).resolve().parents[2] / "prompts"


class _SpyProvider(ProviderAdapter):
    def __init__(self) -> None:
        self.last_prompt = ""
        self._calls = 0

    @property
    def call_count(self) -> int:
        return self._calls

    def generate(self, prompt: str) -> str:
        self._calls += 1
        self.last_prompt = prompt
        return "Argument text."


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


def _render_prompt(agent_cls: type[ProAgent | ConAgent], template_file: str) -> str:
    spy = _SpyProvider()
    template = load_prompt(template_file, PROMPTS)
    agent = agent_cls(spy, MockSearchTool(), prompt_template=template, topic="My Debate Topic")
    agent.produce(
        session_id="s1",
        round_index=1,
        turn_index=2,
        claim_id="c1",
        opponent_claim_id="o1",
        store=EvidenceStore(),
    )
    return spy.last_prompt


def test_pro_prompt_rendered_from_local_template() -> None:
    prompt = _render_prompt(ProAgent, "agents/pro.md")
    for term in (
        "My Debate Topic",
        "Pro",
        "evidence_refs",
        "opponent_claim_id",
        "JSON",
        "o1",
        "c1",
    ):
        assert term in prompt


def test_con_prompt_rendered_from_local_template() -> None:
    prompt = _render_prompt(ConAgent, "agents/con.md")
    for term in ("My Debate Topic", "Con", "evidence_refs", "opponent_claim_id", "JSON", "o1"):
        assert term in prompt


def test_judge_renders_local_protocol_templates() -> None:
    regen = load_prompt("protocol/regeneration.md", PROMPTS)
    final = load_prompt("protocol/final_judgment.md", PROMPTS)
    judge = JudgeAgent(160, regeneration_template=regen, final_template=final)
    rendered = judge.regeneration_prompt("missing evidence; wrong side")
    assert "missing evidence; wrong side" in rendered
    assert "corrected JSON" in rendered
    instructions = judge.final_instructions()
    assert "rubric" in instructions
    assert "no tie" in instructions


def test_judge_instructions_render_local_judge_template() -> None:
    judge_t = load_prompt("agents/judge.md", PROMPTS)
    judge = JudgeAgent(160, judge_template=judge_t)
    text = judge.judge_instructions(topic="My Debate Topic")
    assert "My Debate Topic" in text
    for term in (
        "JSON",
        "evidence_refs",
        "opponent_claim_id",
        "exactly one winner",
        "tie is not allowed",
        "untrusted",
    ):
        assert term in text
