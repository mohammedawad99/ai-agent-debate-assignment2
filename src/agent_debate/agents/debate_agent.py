"""Pro and Con agents (Phase 6.2c).

Thin subclasses differing only by assigned role/stance. Neither references the
other; the Judge (via the runner) mediates all communication (DR-4/DR-5).
"""

from __future__ import annotations

from agent_debate.agents.base import DebateAgent


class ProAgent(DebateAgent):
    role = "pro"


class ConAgent(DebateAgent):
    role = "con"
