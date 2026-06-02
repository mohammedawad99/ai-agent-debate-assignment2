"""SDK application service (Phase 6.3a / 6.3d / 6.5 / 6.6 / 6.7).

Builds the agents/Judge from config + factories + project-local prompts. Provider /
search / judge-provider are selectable; defaults are mock/mock/deterministic; mocks
ignore prompts (offline unchanged). No real provider/search/judge runs unless selected.
"""

from __future__ import annotations

from pathlib import Path

from agent_debate.agents.debate_agent import ConAgent, ProAgent
from agent_debate.agents.judge import JudgeAgent
from agent_debate.config.loader import load_raw_config
from agent_debate.orchestration.runner import DebateRunner
from agent_debate.orchestration.session import DebateSessionResult
from agent_debate.orchestration.watchdog import Watchdog
from agent_debate.prompts.loader import load_prompt
from agent_debate.providers.base import ProviderAdapter
from agent_debate.providers.factory import build_judge_provider, build_provider
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


def _load_agent_prompts(config_dir: Path | None) -> dict[str, str]:
    agents = load_raw_config("agents.json", config_dir)
    debate = load_raw_config("debate.json", config_dir)
    base = Path(agents["prompts_dir"])
    roles = agents["roles"]
    proto = agents["protocol_prompts"]
    return {
        "topic": str(debate["topic"]),
        "pro": load_prompt(roles["pro"]["prompt_template"], base),
        "con": load_prompt(roles["con"]["prompt_template"], base),
        "judge": load_prompt(roles["judge"]["prompt_template"], base),
        "regen": load_prompt(proto["regeneration"], base),
        "final": load_prompt(proto["final_judgment"], base),
    }


def _run_debate(
    pro_provider: ProviderAdapter,
    con_provider: ProviderAdapter,
    search_tool: SearchTool,
    prompts: dict[str, str],
    *,
    session_id: str,
    turns_per_side: int,
    output_dir: Path | None,
    judge_provider: ProviderAdapter | None = None,
) -> DebateSessionResult:
    cost = CostTracker()
    topic = prompts["topic"]
    pro = ProAgent(pro_provider, search_tool, prompt_template=prompts["pro"], topic=topic)
    con = ConAgent(con_provider, search_tool, prompt_template=prompts["con"], topic=topic)
    judge = JudgeAgent(
        DEFAULT_WORD_LIMIT,
        regeneration_template=prompts["regen"],
        final_template=prompts["final"],
        judge_template=prompts["judge"],
        topic=topic,
        judge_provider=judge_provider,
    )
    gate = Gatekeeper(cost, max_provider_calls=1000, max_search_calls=1000, max_retries=1000)
    runner = DebateRunner(pro, con, judge, cost_tracker=cost, gatekeeper=gate, watchdog=Watchdog())
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
    prompts = _load_agent_prompts(None)
    pro = MockProvider(_cycle(_MOCK_ARGS, turns_per_side))
    con = MockProvider(_cycle(_MOCK_COUNTER, turns_per_side))
    return _run_debate(
        pro,
        con,
        MockSearchTool(),
        prompts,
        session_id=session_id,
        turns_per_side=turns_per_side,
        output_dir=output_dir,
    )


def run_configured_debate(
    *,
    provider: str = "mock",
    search: str = "mock",
    judge_provider: str = "none",
    session_id: str = "configured",
    turns_per_side: int = DEFAULT_TURNS_PER_SIDE,
    output_dir: Path | None = None,
    config_dir: Path | None = None,
    pro_provider: ProviderAdapter | None = None,
    con_provider: ProviderAdapter | None = None,
    search_tool: SearchTool | None = None,
    judge_provider_override: ProviderAdapter | None = None,
) -> DebateSessionResult:
    """Run a debate with provider/search/judge from config + factories (overrides for tests)."""
    prompts = _load_agent_prompts(config_dir)
    provider_cfg = {**load_raw_config("providers.json", config_dir), "active": provider}
    search_cfg = {**load_raw_config("search.json", config_dir), "active": search}
    pro_responses = _cycle(_MOCK_ARGS, turns_per_side)
    con_responses = _cycle(_MOCK_COUNTER, turns_per_side)
    pro = pro_provider or build_provider(provider_cfg, responses=pro_responses)
    con = con_provider or build_provider(provider_cfg, responses=con_responses)
    tool = search_tool or build_search(search_cfg)
    judge = build_judge_provider(judge_provider, provider_cfg, override=judge_provider_override)
    return _run_debate(
        pro,
        con,
        tool,
        prompts,
        session_id=session_id,
        turns_per_side=turns_per_side,
        output_dir=output_dir,
        judge_provider=judge,
    )
