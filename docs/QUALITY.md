# Quality Gates

## Purpose

These gates make quality **objective and automatable** — a reviewer (human, ChatGPT,
or grader) can run them and see pass/fail rather than trust prose. They directly address
Assignment 1 weakness **W-4** (no automated quality standards) and enforce
[`PROJECT_RULES.md`](./PROJECT_RULES.md) RULE 14.

> **Phase 5 status:** the gates and test structure exist now. Debate/orchestration/agent/
> provider/search **logic is not implemented yet** (Phase 6). Behavioral expectations are
> recorded as **`xfail` contract tests** until then (see below).

## Commands

Run individually, or all together before a commit:

```bash
uv run ruff check .                  # lint
uv run ruff format --check .         # formatting (no changes applied)
uv run pytest -rx                    # tests (-rx shows xfail reasons)
uv run pytest --cov=src/agent_debate --cov-report=term-missing --cov-fail-under=85
uv run mypy src scripts              # type check
uv run python scripts/check_required_docs.py
uv run python scripts/check_file_lengths.py
uv run python scripts/check_json_configs.py
```

| Gate | Command | What it checks |
|------|---------|----------------|
| Lint | `ruff check .` | Style/correctness lint (rules E, F, I, UP, B). |
| Format | `ruff format --check .` | Code is formatted; no diffs. |
| Tests | `pytest -rx` | All non-xfail tests pass; xfail contracts are expected-fail. |
| Coverage | `pytest --cov=... --cov-fail-under=85` | Line/branch coverage ≥ **85%** of `src/agent_debate`. |
| Types | `mypy src scripts` | Static types (lenient in skeleton phase). |
| Required docs | `scripts/check_required_docs.py` | All required docs present. |
| File size | `scripts/check_file_lengths.py` | Python files ≤ **150 lines**. |
| Config JSON | `scripts/check_json_configs.py` | Every `config/*.json` parses. |

## Coverage target

- **Target: 85%** of `src/agent_debate`, enforced via `--cov-fail-under=85`.
- It is configured in `pyproject.toml` (`[tool.coverage.report] fail_under = 85`) and
  applied when coverage runs. It is intentionally **not** in default `pytest` `addopts`
  so a bare `uv run pytest` stays simple and is not blocked prematurely while the package
  surface is still tiny.

## Required docs

Enforced by `scripts/check_required_docs.py`: `README.md`, and under `docs/`:
`REQUIREMENTS_AUDIT.md`, `LESSONS_FROM_ASSIGNMENT1.md`, `PROJECT_RULES.md`, `TODO.md`,
`PRD.md`, `PLAN.md`, `ARCHITECTURE.md`, `PROTOCOL.md`, `SCORING_AND_VALIDATION.md`,
`CONFIGURATION.md`, `QUALITY.md`.

## File-size check

- Default limit: **150 lines** per Python file under `src/`, `tests/`, `scripts/`.
- Generated/venv/cache dirs (`.venv`, `__pycache__`, `.ruff_cache`, `.pytest_cache`,
  `.mypy_cache`, `build`, `dist`, `.git`) are ignored.
- Violations are printed with file path and line count; exit code is non-zero.

## JSON config validation

`scripts/check_json_configs.py` parses every `config/*.json` (also covered by
`tests/unit/test_config_values.py`, which additionally asserts key values match the
approved decisions: tie-break priority, retry cap, word limits, target turns).

## Principles

- **No secrets.** No API keys/tokens/passwords in the repo or in logs; `.env` is
  gitignored; only `.env.example` is committed. A hygiene test asserts `.env` is neither
  present nor tracked. *(NFR-06)*
- **No fake evidence/results.** No transcripts, judgments, evidence, or logs are
  fabricated. Tests use mocks (Phase 6) and never call real LLMs or the web. *(RULE 17)*

## Enforced now vs planned for later

| Gate | Now (Phase 5) | Later |
|------|---------------|-------|
| ruff lint + format | ✅ enforced | — |
| pytest (skeleton + quality tests) | ✅ enforced | + behavioral tests (Phase 6) flip from xfail to pass |
| coverage ≥ 85% | ✅ available/enforceable now | meaningful once real logic exists (Phase 6) |
| mypy | ✅ enforced (lenient) | tightened if practical |
| required-docs / file-size / config-json | ✅ enforced | — |

## xfail contract tests (TDD)

`tests/integration/test_contracts.py` records the **required future behaviors** from the
design docs (no direct Pro↔Con routing, exactly one winner, invalid-JSON regeneration,
missing/irrelevant evidence rejection, agreement-collapse, off-side drift, retry
exhaustion, configured tie-break, prompt-injection resistance, provider timeout,
watchdog). Each is marked `@pytest.mark.xfail(reason=..., strict=True)`:

- It **documents the contract** before the code exists (TDD).
- It currently raises `NotImplementedError`, so it **xfails** — the suite still exits 0.
- **`strict=True` is deliberate:** if a future Phase 6 implementation makes a contract
  test unexpectedly pass, pytest reports **`XPASS(strict)` and fails the quality gate**.
  This forces us to **remove the `xfail` marker and convert the test into a real
  assertion** rather than leaving a silent `xpass`. It prevents stale placeholders and
  enforces disciplined TDD: a contract is either a known-pending `xfail` or a real,
  asserting test — never silently passing while still marked pending.
