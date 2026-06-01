"""SDK application service (Phase 6.3a / 6.3d).

`run_mock_debate` runs a fully OFFLINE mock debate (the default, unchanged behavior).
`run_configured_debate` selects provider/search via factories from config — `mock` by
default; `claude_cli`/`ddgs` are opt-in and only invoked when explicitly selected. No
real provider/search runs unless configured. Artifacts only when output_dir is given.
"""

from __future__ import annotations

from pathlib import Path

from agent_debate.agents.debate_agent import ConAgent, ProAgent
from agent_debate.agents.judge import JudgeAgent
from agent_debate.config.loader import load_raw_config
from agent_debate.orchestration.runner import DebateRunner
from agent_debate.orchestration.session import DebateSessionResult
from agent_debate.orchestration.watchdog import Watchdog
from agent_debate.providers.base import ProviderAdapter
from agent_debate.providers.factory import build_provider
from agent_debate.providers.mock_provider import MockProvider
from agent_debate.quality.gatekeeper import Gatekeeper
from agent_debate.results.cost_tracker import CostTracker
from agent_debate.search.base import SearchTool
from agent_debate.search.factory import build_search
from agent_debate.search.mock_search import MockSearchTool

DEFAULT_TURNS_PER_SIDE = 2
DEFAULT_RETRY_CAP = 2
DEFAULT_WORD_LIMIT = 160
DEFAULT_TIE_BREAK_PRIORITY = ["con", "pro"]
_MOCK_ARGS = [
    "AI coding agents build industry-relevant skills students will use.",
    "Guided AI use frees time for design thinking and review.",
]
_MOCK_COUNTER = [
    "Heavy reliance can erode core problem-solving fundamentals.",
    "Unsupervised agent use risks shallow understanding of code.",
]


def _cycle(samples: list[str], count: int) -> list[str]:
    return [samples[index % len(samples)] for index in range(max(count, 1))]


def _run_debate(
    pro_provider: ProviderAdapter,
    con_provider: ProviderAdapter,
    search_tool: SearchTool,
    *,
    session_id: str,
    turns_per_side: int,
    output_dir: Path | None,
) -> DebateSessionResult:
    cost = CostTracker()
    pro = ProAgent(pro_provider, search_tool)
    con = ConAgent(con_provider, search_tool)
    gatekeeper = Gatekeeper(cost, max_provider_calls=1000, max_search_calls=1000, max_retries=1000)
    runner = DebateRunner(
        pro,
        con,
        JudgeAgent(DEFAULT_WORD_LIMIT),
        cost_tracker=cost,
        gatekeeper=gatekeeper,
        watchdog=Watchdog(),
    )
    return runner.run(
        session_id=session_id,
        turns_per_side=turns_per_side,
        retry_cap=DEFAULT_RETRY_CAP,
        tie_break_priority=DEFAULT_TIE_BREAK_PRIORITY,
        output_dir=output_dir,
    )


def run_mock_debate(
    *,
    session_id: str = "offline-mock",
    turns_per_side: int = DEFAULT_TURNS_PER_SIDE,
    output_dir: Path | None = None,
) -> DebateSessionResult:
    """Run a fully offline mock debate and return the session result."""
    pro = MockProvider(_cycle(_MOCK_ARGS, turns_per_side))
    con = MockProvider(_cycle(_MOCK_COUNTER, turns_per_side))
    return _run_debate(
        pro,
        con,
        MockSearchTool(),
        session_id=session_id,
        turns_per_side=turns_per_side,
        output_dir=output_dir,
    )


def run_configured_debate(
    *,
    provider: str = "mock",
    search: str = "mock",
    session_id: str = "configured",
    turns_per_side: int = DEFAULT_TURNS_PER_SIDE,
    output_dir: Path | None = None,
    config_dir: Path | None = None,
    pro_provider: ProviderAdapter | None = None,
    con_provider: ProviderAdapter | None = None,
    search_tool: SearchTool | None = None,
) -> DebateSessionResult:
    """Run a debate using provider/search selected via config + factories.

    Overrides (pro_provider/con_provider/search_tool) are for tests; real provider/
    search run only when explicitly selected (e.g. provider='claude_cli').
    """
    provider_cfg = {**load_raw_config("providers.json", config_dir), "active": provider}
    search_cfg = {**load_raw_config("search.json", config_dir), "active": search}
    pro_responses = _cycle(_MOCK_ARGS, turns_per_side)
    con_responses = _cycle(_MOCK_COUNTER, turns_per_side)
    pro = pro_provider or build_provider(provider_cfg, responses=pro_responses)
    con = con_provider or build_provider(provider_cfg, responses=con_responses)
    tool = search_tool or build_search(search_cfg)
    return _run_debate(
        pro,
        con,
        tool,
        session_id=session_id,
        turns_per_side=turns_per_side,
        output_dir=output_dir,
    )
