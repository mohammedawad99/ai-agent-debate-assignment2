# AI Agent Debate System

A Python project **designed to orchestrate** a structured, supervised debate between two
AI agents (**Pro** and **Con**) moderated by a **Parent/Judge** agent that will route
every message, enforce the rules, and declare a single winner.

> **Status: early development (Phase 6.2c — offline debate orchestration with mocks).**
> Implemented and tested **offline**: protocol/validation/scoring/tie-break (6.1), the
> `ProviderAdapter`/`SearchTool` abstractions + `MockProvider`/`MockSearchTool` (6.2a),
> `CostTracker`/`Gatekeeper`/`Watchdog` (6.2b), and now the **Judge/Pro/Con agents, the
> parent-mediated `DebateRunner`/session, and `TranscriptWriter`** (6.2c). A short
> debate can now run **end-to-end with mocks** (deterministic, no network/LLM), and all
> 13 behavioral contract tests pass. **Not implemented yet:** the **real Claude CLI
> provider** and **real web/`ddgs` search**, the SDK service, and the CLI. **No real
> evidence-backed debate has been run** — no committed results, transcripts, logs, or
> evidence (test artifacts are written only under pytest `tmp_path`). The full README is
> authored in Phase 8.

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
> use strict `xfail` for TDD. As of **Phase 6.1**, **7** contracts are now real,
> passing, offline tests (routing, invalid JSON, missing opponent reference, missing
> evidence, irrelevant evidence, configured tie-break, prompt-injection resistance);
> the remaining **6** stay strict-`xfail` because they need the full DebateRunner, a
> real provider, or the watchdog (Phase 6.2+). Strict means an unexpected pass fails
> the gate, forcing conversion into a real test. No debate has been run; no
> results/evidence have been produced.

## License
MIT.
