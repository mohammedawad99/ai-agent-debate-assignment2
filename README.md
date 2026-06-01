# AI Agent Debate System

A Python project **designed to orchestrate** a structured, supervised debate between two
AI agents (**Pro** and **Con**) moderated by a **Parent/Judge** agent that will route
every message, enforce the rules, and declare a single winner.

> **Status: early development (Phase 4 — project skeleton).**
> The package layout, configuration templates, and tooling exist, but the debate
> orchestration, agents, providers, and search adapters are **not implemented yet**.
> This README is a placeholder; the full README (problem, setup, usage, architecture,
> debate flow, screenshots, quality commands, cost/resource awareness, limitations,
> reproducibility) is authored in Phase 8. No results or evidence have been produced yet.

## Planning & design documents
- [`docs/REQUIREMENTS_AUDIT.md`](docs/REQUIREMENTS_AUDIT.md)
- [`docs/PRD.md`](docs/PRD.md)
- [`docs/PLAN.md`](docs/PLAN.md)
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- [`docs/PROTOCOL.md`](docs/PROTOCOL.md)
- [`docs/SCORING_AND_VALIDATION.md`](docs/SCORING_AND_VALIDATION.md)
- [`docs/CONFIGURATION.md`](docs/CONFIGURATION.md)
- [`docs/PROJECT_RULES.md`](docs/PROJECT_RULES.md) · [`docs/TODO.md`](docs/TODO.md)

## Development (skeleton)
Reproducible setup uses [uv](https://docs.astral.sh/uv/):

```bash
uv sync                # create the environment from pyproject.toml
uv run pytest          # run the skeleton + quality tests
uv run ruff check .    # lint
```

Configuration lives in `config/*.json` (see `docs/CONFIGURATION.md`). Secrets, if ever
needed, come from `.env` (gitignored); copy `.env.example` to start. The primary provider
path is the login-based Claude CLI and needs no API key.

## Current quality commands
Full details in [`docs/QUALITY.md`](docs/QUALITY.md). The gates are runnable today:

```bash
uv run ruff check .
uv run ruff format --check .
uv run pytest -rx
uv run pytest --cov=src/agent_debate --cov-report=term-missing --cov-fail-under=85
uv run mypy src scripts
uv run python scripts/check_required_docs.py
uv run python scripts/check_file_lengths.py
uv run python scripts/check_json_configs.py
```

> **Note:** the behavioral **contract tests** in `tests/integration/test_contracts.py`
> are marked **strict `xfail`** (expected failure) until the Phase 6 implementation
> exists — they document required behavior in advance (TDD) and do **not** indicate the
> debate system works yet. Because they are `strict=True`, an unexpected pass fails the
> quality gate, forcing the marker to be removed and the test converted into a real
> assertion. No debate has been run; no results/evidence have been produced.

## License
MIT.
