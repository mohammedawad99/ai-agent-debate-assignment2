"""SDK application service (Phase 6.3a).

The single public entry point the CLI uses. `run_mock_debate` wires the existing
OFFLINE components (MockProvider, MockSearchTool, CostTracker, Gatekeeper, Watchdog,
JudgeAgent, DebateRunner) and returns a DebateSessionResult. No real provider/search,
no network/LLM. Artifacts are written only when an explicit output_dir is given.
"""

from __future__ import annotations

from pathlib import Path

from agent_debate.agents.debate_agent import ConAgent, ProAgent
from agent_debate.agents.judge import JudgeAgent
from agent_debate.orchestration.runner import DebateRunner
from agent_debate.orchestration.session import DebateSessionResult
from agent_debate.orchestration.watchdog import Watchdog
from agent_debate.providers.mock_provider import MockProvider
from agent_debate.quality.gatekeeper import Gatekeeper
from agent_debate.results.cost_tracker import CostTracker
from agent_debate.search.mock_search import MockSearchTool

DEFAULT_TURNS_PER_SIDE = 2
DEFAULT_RETRY_CAP = 2
DEFAULT_WORD_LIMIT = 160
DEFAULT_TIE_BREAK_PRIORITY = ["con", "pro"]
# Deterministic scripted arguments for the offline mock debate (no markers).
_MOCK_ARGS = [
    "AI coding agents build industry-relevant skills students will use.",
    "Guided AI use frees time for design thinking and review.",
]
_MOCK_COUNTER = [
    "Heavy reliance can erode core problem-solving fundamentals.",
    "Unsupervised agent use risks shallow understanding of code.",
]


def run_mock_debate(
    *,
    session_id: str = "offline-mock",
    turns_per_side: int = DEFAULT_TURNS_PER_SIDE,
    output_dir: Path | None = None,
) -> DebateSessionResult:
    """Run a fully offline mock debate and return the session result."""
    cost = CostTracker()
    search = MockSearchTool()
    pro = ProAgent(MockProvider(_cycle(_MOCK_ARGS, turns_per_side)), search)
    con = ConAgent(MockProvider(_cycle(_MOCK_COUNTER, turns_per_side)), search)
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


def _cycle(samples: list[str], count: int) -> list[str]:
    """Return `count` scripted responses, cycling the samples deterministically."""
    return [samples[index % len(samples)] for index in range(max(count, 1))]
