# AI Agent Debate System

A Python project **designed to orchestrate** a structured, supervised debate between two
AI agents (**Pro** and **Con**) moderated by a **Parent/Judge** agent that will route
every message, enforce the rules, and declare a single winner.

> **Status: early development (Phase 7.10 — tolerant provider-backed Judge JSON parsing).**
> The **fourth** controlled real run produced a **complete 4-turn debate body** — both Pro
> and Con turns accepted, on-side, evidence-cited, under the word limit, with **zero
> retries** (real Claude + live `ddgs` generation now works end-to-end). It still **failed**
> at the provider-backed Judge, whose verdict was not directly parseable JSON; Phase 7.8
> made that a graceful `failed_protocol` (artifacts written, **no winner**, no crash).
> Phase 7.10 adds **tolerant Judge JSON parsing** — it unwraps a markdown code fence and
> extracts exactly one JSON object from surrounding prose before applying the **same strict
> validation** (one winner, opposite loser, no tie, reasoning required, scores 0–5); zero or
> multiple objects are rejected, and no `eval` is used. **No successful real run exists yet,
> and no winner has been produced by a real debate.** A fifth real run (fresh timestamped
> directory) is still pending.
>
> **Status: early development (Phase 7.8 — graceful provider-backed Judge failure).**
> Three controlled real runs (2 turns/side, real Claude CLI + live `ddgs`) have been
> attempted; **none has succeeded yet**. The **third** got furthest: both Pro and Con
> turns were **accepted** (the Phase 7.6 regeneration + margin fixes worked) and the run
> **reached the provider-backed Judge** — but Claude returned **empty/non-JSON** for the
> verdict, raising `JudgeError`, which the runner did not catch, so the CLI **crashed with
> no artifacts**. Phase 7.8 makes that failure **graceful**: `JudgeError` is now a
> controlled `failed_protocol` result that preserves accepted turns and writes
> transcript + cost report + `error_report.md` (no crash, **no fabricated winner**); the
> final-judgment prompt is hardened to demand a single JSON object. **No successful real
> run exists yet, and no winner has been produced by a real debate.** A fourth real run
> (fresh timestamped directory) is still pending.
>
> **Status: early development (Phase 7.6 — real regeneration wiring after 2 failed runs).**
> Two controlled real runs (2 turns/side, real Claude CLI + live `ddgs`) have been
> attempted and **both failed honestly** on `word_limit_exceeded`. The **second** made
> partial progress — Pro's opening turn was **accepted** (219 words, 5 evidence refs),
> proving the Phase 7.4 limit fix works — then Con's opening failed because retries were a
> no-op (the runner re-sent the identical prompt). Phase 7.6 wires **real regeneration**:
> on retry the runner now sends a correction prompt carrying the validation error + the
> configured word limit and asks for a shortened argument text; Pro/Con prompts add a
> ~180–200-word margin (hard limit stays 220, retry cap stays 2). Verified offline only (a
> mocked over-limit attempt now recovers on retry). Both failed-run directories are kept as
> untracked evidence. **No successful real run exists yet, and no winner has been produced
> by a real debate.** A third real run (fresh timestamped directory) is still pending.
>
> **Status: early development (Phase 7.4 — first real run attempted & failed; fix applied).**
> A first controlled real run (2 turns/side, real Claude CLI + live `ddgs`) was executed
> and **failed honestly**: `failed_protocol — retry exhausted: word_limit_exceeded` (3
> Claude calls, 3 ddgs searches, **no winner**). Its partial artifacts are kept as honest
> evidence under `results/real_run_20260602_1837/` (untracked). **No successful real run
> exists yet, and no winner has been produced by a real debate.** Phase 7.4 applies the
> minimal fix: child word limit **160 → 220** (config), and Pro/Con + regeneration prompts
> now state the configured limit and ask for **argument text only** (the orchestration
> wraps it into the protocol message; the model is not asked to emit JSON). Retry cap
> unchanged. A second real run (fresh timestamped directory) is still pending.
>
> **Status: early development (Phase 6.8 — `ddgs` dependency added, no live search).**
> `ddgs` is now a **declared project dependency** (`pyproject.toml` + `uv.lock`) so the
> Phase 7 controlled run can later exercise the real search path intentionally. **No live
> search has been executed** — this phase only installs and verifies the dependency
> (`ddgs_available=True`). `ddgs` is used **only when `--search ddgs` is explicitly
> selected**; the default search path remains the offline `MockSearchTool`. Mock mode
> stays the default end-to-end, and **no real Claude/LLM call, web query, or
> evidence-backed run has been performed.** Plan:
> [`docs/REAL_RUN_PLAN.md`](docs/REAL_RUN_PLAN.md).
>
> **Status: early development (Phase 6.7 — judge-provider selection in SDK/CLI).**
> The optional provider-backed Judge (6.6) is now **selectable** through the SDK and CLI
> without changing the safe default. `agent-debate run` gained
> `--judge-provider none|deterministic|mock|claude_cli` (**default `none`**, i.e. the
> deterministic/offline Judge); the SDK `run_configured_debate(...)` gained a matching
> `judge_provider` argument (plus a `judge_provider_override` for tests). `none`/
> `deterministic` keep the existing fixed-score Judge, `mock` uses an offline canned
> verdict, and `claude_cli` builds the real provider-backed Judge **only when explicitly
> selected** (printed and warned; never executed at construction). **CLI/SDK judge tests
> monkeypatch the SDK or use mocks — no real Claude is ever called.** Mock mode remains
> the default end-to-end. **No real Claude-backed judgment or evidence-backed debate has
> been executed** — `ddgs` not installed, Claude login not verified. Plan:
> [`docs/REAL_RUN_PLAN.md`](docs/REAL_RUN_PLAN.md).
>
> **Status: early development (Phase 6.6 — optional content-aware Judge).**
> The project-local Pro/Con prompts are wired into the runtime provider call (6.5), and
> the Judge now has an **optional provider-backed final-judgment path**: when a
> `judge_provider` is supplied, the Judge renders the final-judgment prompt (topic +
> transcript summary + rubric + no-tie + tie-break rule), asks the provider for a JSON
> verdict, and **parses/validates it** (exactly one winner, no tie, 0–5 scores; malformed
> output is rejected with `JudgeError`). **This path is tested with `MockProvider` only —
> no real Claude call.** **When no judge provider is supplied (the default, including the
> mock CLI), the Judge uses the existing deterministic/offline scoring** — disclosed in
> `FinalJudgment.limitations`. **Mock mode remains the default. No real Claude-backed
> judgment or evidence-backed debate has been executed** — `ddgs` not installed, Claude
> login not verified. Plan: [`docs/REAL_RUN_PLAN.md`](docs/REAL_RUN_PLAN.md).
>
> **Status: early development (Phase 6.4 — project-local prompt templates).**
> **Project-local prompt templates** for the Judge/Pro/Con agents and the
> regeneration / final-judgment steps now live under `prompts/` (referenced by
> `config/agents.json` via relative paths) with a small loader/renderer — **no global
> Claude skills**. They are **templates only**, not yet wired into the runtime, and
> **no real Claude run has been performed**. Mock mode remains the default. Earlier
> phases (offline core, mocks, orchestration, real adapters behind factories) are
> summarized below.
>
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

# Configured run — defaults to mock/mock + deterministic judge (offline, safe):
uv run agent-debate run --provider mock --search mock --turns-per-side 1

# Judge provider is selectable (default `none` = deterministic/offline scoring):
uv run agent-debate run --provider mock --search mock --judge-provider mock --turns-per-side 1

# Opt-in real mode (NOT yet exercised in project evidence; may call external tools/web):
#   uv run agent-debate run --provider claude_cli --search ddgs --judge-provider claude_cli
# add --output-dir <dir> to write transcript/cost artifacts (never written by default).
```
Both commands default to the offline mocks (`MockProvider`/`MockSearchTool`) — **no real
provider, search, network, or LLM**. `--provider claude_cli` / `--search ddgs` are opt-in;
the CLI prints a clear **REAL MODE** warning. The concrete `ddgs` backend uses the
installed `ddgs` package (lazily imported). The Judge defaults to `--judge-provider none`
(deterministic/offline scoring); `mock` uses an offline canned verdict and `claude_cli`
builds the provider-backed Judge **only when explicitly selected** (warned, never run at
construction). **A first real run was attempted and failed honestly (see the Phase 7.4
status above); no successful real run exists yet.**

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
