# AI Agent Debate System

A Python project **designed to orchestrate** a structured, supervised debate between two
AI agents (**Pro** and **Con**) moderated by a **Parent/Judge** agent that will route
every message, enforce the rules, and declare a single winner.

> **Status: early development (Phase 6.3d — real-mode wiring, mock default).**
> Implemented and tested **offline**: protocol/validation/scoring/tie-break (6.1),
> provider/search abstractions + mocks (6.2a), `CostTracker`/`Gatekeeper`/`Watchdog`
> (6.2b), Judge/Pro/Con agents + `DebateRunner` + `TranscriptWriter` (6.2c), offline mock
> SDK + CLI (6.3a), `ClaudeCliProvider` (6.3b), `RealSearchTool` (6.3c), and now
> **provider/search factories, a lazy `ddgs` backend, a configured SDK run, and an
> `agent-debate run` command** with `--provider`/`--search` flags (6.3d).
> **Mock mode is the default and the safe path** — `run` defaults to `--provider mock
> --search mock`, and `mock-run` is unchanged. `claude_cli`/`ddgs` are **opt-in**; the
> CLI clearly warns when real mode is selected. **Normal tests mock all external calls
> (`subprocess`, the ddgs backend) and never call Claude or the web.** **No real
> Claude-backed or evidence-backed debate has been run yet — Phase 7 is the controlled
> real run.** No committed results/transcripts/logs/evidence (artifacts only when
> `--output-dir` is given; tests use pytest `tmp_path`). The full README is in Phase 8.

### CLI usage
```bash
# Offline mock debate (unchanged, fully deterministic):
uv run agent-debate mock-run --turns-per-side 1

# Configured run — defaults to mock/mock (offline, safe):
uv run agent-debate run --provider mock --search mock --turns-per-side 1

# Opt-in real mode (NOT yet exercised in project evidence; may call external tools/web):
#   uv run agent-debate run --provider claude_cli --search ddgs
# add --output-dir <dir> to write transcript/cost artifacts (never written by default).
```
Both commands default to the offline mocks (`MockProvider`/`MockSearchTool`) — **no real
provider, search, network, or LLM**. `--provider claude_cli` / `--search ddgs` are opt-in;
the CLI prints a clear **REAL MODE** warning, and a concrete `ddgs` backend requires the
optional `ddgs` package (lazily imported). **No real run has been performed yet.**

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
