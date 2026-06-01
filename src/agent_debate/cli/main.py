"""CLI entry point (Phase 6.3a) — thin wrapper over the SDK.

Parses arguments and renders output only; all behavior lives in the SDK
(`agent_debate.sdk.service`). Currently exposes one subcommand, `mock-run`, which
runs the fully OFFLINE mock debate. No real provider/search/network/LLM is used.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from agent_debate.orchestration.session import DebateSessionResult
from agent_debate.sdk.service import run_mock_debate


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-debate",
        description="AI Agent Debate System (offline mock mode in Phase 6.3a).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    mock = sub.add_parser("mock-run", help="Run an offline mock debate (no real provider/search).")
    mock.add_argument("--turns-per-side", type=int, default=2)
    mock.add_argument("--session-id", default="offline-mock")
    mock.add_argument("--output-dir", default=None, help="If set, write artifacts here.")
    return parser


def _render(result: DebateSessionResult) -> None:
    print("AI Agent Debate — OFFLINE MOCK MODE (no real provider/search/LLM/web used)")
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
    if args.command == "mock-run":
        output_dir = Path(args.output_dir) if args.output_dir else None
        result = run_mock_debate(
            session_id=args.session_id,
            turns_per_side=args.turns_per_side,
            output_dir=output_dir,
        )
        _render(result)
        return 0 if result.is_successful else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
