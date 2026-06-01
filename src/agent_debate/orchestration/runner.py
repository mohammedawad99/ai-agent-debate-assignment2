"""DebateRunner (Phase 6.2c) — offline, parent-mediated orchestration with mocks.

The runner is the sole router: it asks each agent to produce a turn, has the Judge
review it, requests regeneration up to the retry cap, and on success scores both
sides and applies the configured tie-break. Pro and Con never address each other.
Uses CostTracker, Gatekeeper, and Watchdog. No real provider/search/network; writes
artifacts only when an explicit output_dir is given (tests use tmp_path).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agent_debate.agents.base import DebateAgent
from agent_debate.agents.judge import JudgeAgent
from agent_debate.evidence.store import EvidenceStore
from agent_debate.orchestration.session import (
    DebateSessionResult,
    ProtocolFailure,
    RunStatus,
)
from agent_debate.orchestration.watchdog import Watchdog, WatchdogError
from agent_debate.providers.base import ProviderError
from agent_debate.quality.gatekeeper import Gatekeeper, GatekeeperError
from agent_debate.results.cost_tracker import CostTracker
from agent_debate.results.transcript_writer import TranscriptWriter


class DebateRunner:
    def __init__(
        self,
        pro: DebateAgent,
        con: DebateAgent,
        judge: JudgeAgent,
        *,
        cost_tracker: CostTracker,
        gatekeeper: Gatekeeper,
        watchdog: Watchdog,
    ) -> None:
        self._pro = pro
        self._con = con
        self._judge = judge
        self._cost = cost_tracker
        self._gate = gatekeeper
        self._watchdog = watchdog

    def run(
        self,
        *,
        session_id: str,
        turns_per_side: int,
        retry_cap: int,
        tie_break_priority: list[str],
        output_dir: Path | None = None,
    ) -> DebateSessionResult:
        store = EvidenceStore()
        messages: list[dict[str, Any]] = []
        errors: list[str] = []
        judgment = None
        status = RunStatus.SUCCESS
        self._cost.start()
        try:
            self._run_rounds(session_id, turns_per_side, retry_cap, store, messages)
            judgment = self._judge.judge(session_id, tie_break_priority)
        except (ProviderError, WatchdogError, GatekeeperError, ProtocolFailure) as exc:
            status = RunStatus.FAILED_PROTOCOL
            errors.append(f"{type(exc).__name__}: {exc}")
        self._cost.stop()
        result = DebateSessionResult(
            session_id=session_id,
            status=status,
            messages=messages,
            final_judgment=judgment,
            errors=errors,
            cost_summary=self._cost.summary(),
        )
        if output_dir is not None:
            TranscriptWriter().write(result, output_dir)
        return result

    def _run_rounds(
        self,
        session_id: str,
        turns_per_side: int,
        retry_cap: int,
        store: EvidenceStore,
        messages: list[dict[str, Any]],
    ) -> None:
        last_claim: dict[str, str | None] = {"pro": None, "con": None}
        turn_index = 0
        for round_index in range(turns_per_side):
            for agent in (self._pro, self._con):
                self._watchdog.record_progress(turn_index)
                self._watchdog.check()
                claim_id = f"c-{agent.role}-{turn_index}"
                opponent = last_claim["con" if agent.role == "pro" else "pro"]
                message = self._turn(
                    agent, session_id, round_index, turn_index, claim_id, opponent, retry_cap, store
                )
                messages.append(message)
                last_claim[agent.role] = claim_id
                turn_index += 1

    def _turn(
        self,
        agent: DebateAgent,
        session_id: str,
        round_index: int,
        turn_index: int,
        claim_id: str,
        opponent: str | None,
        retry_cap: int,
        store: EvidenceStore,
    ) -> dict[str, Any]:
        last_reason = None
        for attempt in range(retry_cap + 1):
            self._gate.check_provider_call()
            message = agent.produce(
                session_id=session_id,
                round_index=round_index,
                turn_index=turn_index,
                claim_id=claim_id,
                opponent_claim_id=opponent,
                store=store,
            )
            self._cost.record_provider_call(claim_id, str(message["argument"]))
            self._cost.record_search_call()
            verdict = self._judge.review(message, store)
            if verdict.is_valid:
                message["protocol_status"] = "accepted"
                return message
            last_reason = verdict.first_reason
            if attempt < retry_cap:
                self._cost.record_retry()
                self._watchdog.record_retry()
        raise ProtocolFailure(f"retry exhausted: {last_reason}")
