"""CLI entry point (Phase 6.3a / 6.3d) — thin wrapper over the SDK.

Parses arguments and renders output only; all behavior lives in the SDK
(`agent_debate.sdk.service`). `mock-run` runs the fully OFFLINE mock debate. `run`
selects provider/search (mock by default; `claude_cli`/`ddgs` are opt-in and may
invoke external tools/web — clearly warned). The CLI never embeds business logic.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_debate.orchestration.session import DebateSessionResult
from agent_debate.sdk.service import run_configured_debate, run_mock_debate


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-debate",
        description="AI Agent Debate System (offline-mock default; opt-in real mode).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    mock = sub.add_parser("mock-run", help="Run an offline mock debate (no real provider/search).")
    mock.add_argument("--turns-per-side", type=int, default=2)
    mock.add_argument("--session-id", default="offline-mock")
    mock.add_argument("--output-dir", default=None, help="If set, write artifacts here.")
    run = sub.add_parser("run", help="Run a debate with selected provider/search.")
    run.add_argument("--provider", choices=["mock", "claude_cli"], default="mock")
    run.add_argument("--search", choices=["mock", "ddgs"], default="mock")
    run.add_argument("--turns-per-side", type=int, default=2)
    run.add_argument("--session-id", default="configured")
    run.add_argument("--output-dir", default=None, help="If set, write artifacts here.")
    return parser


def _render(result: DebateSessionResult) -> None:
    print(f"session_id: {result.session_id}")
    print(f"status: {result.status}")
    if result.is_successful and result.final_judgment is not None:
        print(f"winner: {result.final_judgment.winner_role}")
    else:
        print("winner: <none — failed protocol run>")
        for error in result.errors:
            print(f"error: {error}")


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    output_dir = Path(args.output_dir) if getattr(args, "output_dir", None) else None
    if args.command == "mock-run":
        print("AI Agent Debate — OFFLINE MOCK MODE (no real provider/search/LLM/web used)")
        result = run_mock_debate(
            session_id=args.session_id, turns_per_side=args.turns_per_side, output_dir=output_dir
        )
        _render(result)
        return 0 if result.is_successful else 1
    if args.command == "run":
        real = args.provider != "mock" or args.search != "mock"
        if real:
            print("AI Agent Debate — REAL MODE: may invoke external tools/web (Claude CLI / ddgs).")
        else:
            print("AI Agent Debate — MOCK MODE (offline; no real provider/search/LLM/web).")
        print(f"provider: {args.provider} | search: {args.search}")
        result = run_configured_debate(
            provider=args.provider,
            search=args.search,
            session_id=args.session_id,
            turns_per_side=args.turns_per_side,
            output_dir=output_dir,
        )
        _render(result)
        return 0 if result.is_successful else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
