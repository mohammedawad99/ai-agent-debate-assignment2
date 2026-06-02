# TODO — Assignment 2 (Phase-Based Plan)

> **Phase-gated.** Each phase must be completed (and its exit criteria met) before
> the next begins. Implementation (`src/`) is **blocked** until Phases 1–3 are done
> (see [`PROJECT_RULES.md`](./PROJECT_RULES.md) Rule 1).
>
> Legend: `[ ]` todo · `[~]` in progress · `[x]` done

---

## Review Rule (Definition of "Reviewed")

A phase (or any document/change) is considered **reviewed** only after **all four**
of the following have happened, in order:

1. **Claude** creates or updates the files.
2. The **human developer** reviews them.
3. The **ChatGPT reviewer** approves them.
4. The changes are **committed to Git**.

Until all four steps are complete, a phase's items may be marked `[x]` (the work is
*done/created*) but the phase itself is **not yet "reviewed"** and the next phase's
gate is **not** unlocked. "Created" ≠ "Reviewed."

---

## Phase 0 — Requirements & Audit
**Goal:** Fully understand and record what must be built.
- [x] Create `docs/REQUIREMENTS_AUDIT.md` *(created; incl. §11 Recorded Decisions, §12 Traceability)*
- [x] Create `docs/LESSONS_FROM_ASSIGNMENT1.md` *(created; concrete W-1..W-7 + prevention map)*
- [x] Create `docs/PROJECT_RULES.md` *(created)*
- [x] Create `docs/TODO.md` (this file) *(created; incl. Review Rule)*
- [x] Verify Git/GitHub setup is clean *(verified: main branch, remote origin, gh auth OK)*
- [x] Record Gate 0 decisions (provider, search, topic, budget, language) — see `REQUIREMENTS_AUDIT.md` §11
- [ ] **Human developer review** of Gate 0 docs
- [ ] **ChatGPT reviewer approval** of Gate 0 docs
- [ ] **Commit** Gate 0 docs to Git
**Exit criteria:** All Gate 0 docs **reviewed per the Review Rule above** (created → human review → ChatGPT approval → committed); requirements traceable; rules agreed.
**Status:** Files created; **review/commit pending** — Phase 0 is *not yet reviewed*, so Phase 1 remains gated.

---

## Phase 1 — PRD (Product Requirements Document)
**Goal:** Define *what* the system does, for whom, and success criteria.
- [ ] Create `docs/PRD.md`
- [ ] Problem statement & goals
- [ ] Personas / usage scenarios (CLI user, grader)
- [ ] Functional scope (roles, debate flow, winner selection)
- [ ] Non-functional scope (cost, performance, reliability, security)
- [ ] Success metrics & acceptance criteria (link to audit checklist)
- [ ] Explicit out-of-scope list
**Exit criteria:** PRD maps 1:1 to REQUIREMENTS_AUDIT; no open functional gaps.

---

## Phase 2 — PLAN
**Goal:** Define *how* and *in what order* to build it.
- [ ] Create `docs/PLAN.md`
- [ ] Module breakdown & dependencies
- [ ] Milestones mapped to phases
- [ ] Risk register with mitigations
- [ ] Test strategy (unit / integration / e2e, mocking approach)
- [ ] Tooling plan (uv, ruff, pytest, coverage, mypy)
**Exit criteria:** Plan is buildable; every requirement has an owning module.

---

## Phase 3 — Architecture & Protocol Design
**Goal:** Design components, interfaces, and the JSON message protocol.
- [x] Create `docs/ARCHITECTURE.md` *(created; layers, dependency rules, components, runtime flow, failure states, security)*
- [x] Create `docs/PROTOCOL.md` *(created; resolves OQ-A1 — enums, DebateMessage/EvidenceRecord/ValidationResult/JudgeScore/FinalJudgment schemas, routing/turn/regeneration rules, examples)*
- [x] Create `docs/SCORING_AND_VALIDATION.md` *(created; resolves OQ-A2 — validation pipeline, two-layer evidence relevance, collapse/drift policy, rubric anchors, tie-break, failed-run policy, test map)*
- [x] Component map (Judge, Pro, Con, SDK, CLI, Gatekeeper, Logger, Search adapter, Provider adapter) *(ARCHITECTURE §6)*
- [x] Parent-mediated routing design (no child↔child path, verified by test) *(ARCHITECTURE §4, PROTOCOL §9)*
- [x] JSON message schema(s) + validation rules *(PROTOCOL §4–8, SCORING_AND_VALIDATION §3)*
- [x] Judge rubric & scoring/tie-break algorithm *(SCORING_AND_VALIDATION §7–9)*
- [x] Side-fidelity / agreement-collapse detection design *(SCORING_AND_VALIDATION §5–6)*
- [x] Timeout / watchdog / Gatekeeper design *(ARCHITECTURE §6–8)*
- [x] Resolve OQ-A1 (schema), OQ-A2 (evidence relevance), OQ-A7 (auth/session = fail-fast, no V1 resume)
- [ ] Config **schema** detail (debate/agents/logging/rate-limits/provider) — config files themselves are Phase 4
- [ ] **Human developer review** of Phase 3 docs
- [ ] **ChatGPT reviewer approval** of Phase 3 docs
- [ ] **Commit** Phase 3 docs to Git
**Exit criteria:** Interfaces frozen; schemas drafted; scoring deterministic — **reviewed per the Review Rule**.
**Status:** Docs created + consistency/security polish applied (tie-break → configured `final_tie_break_priority`; `content`/`argument` clarified; `session_id` added to EvidenceRecord; prompt-injection test + SR-4 robustness behavior added); **review/commit pending** — Phase 3 is *not yet reviewed*, so Phase 4 remains gated. (Concrete `config/*.json` schemas/templates are authored in Phase 4.)

---

## Phase 4 — Project Skeleton
**Goal:** Create the buildable structure (still minimal logic where allowed).
- [x] `pyproject.toml` + uv-compatible metadata *(hatchling, src layout, pytest, pytest-cov w/ planned 85% gate, ruff, lenient mypy, placeholder console script)*
- [x] Package layout under `src/agent_debate/` *(cli, sdk, orchestration, agents, protocol, validation, providers, search, evidence, config, logging, results, quality — `__init__.py` docstrings only, no logic)*
- [x] CLI entry-point placeholder *(`cli/main.py` raises NotImplementedError — honest placeholder, no behavior)*
- [x] Tests skeleton *(`tests/unit`, `tests/integration`, `tests/fixtures`, `conftest.py` placeholder, import-only `test_skeleton.py`)*
- [x] Config templates in `config/` *(app/debate/agents/providers/search/logging/rate_limits .json — safe defaults, no secrets)*
- [x] Ruff / formatter / mypy configuration *(in `pyproject.toml`)*
- [x] `.env.example` template *(placeholders only; `.env` confirmed gitignored)*
- [x] Logging rotation config *(template in `config/logging.json`; scaffold code is Phase 6)*
- [x] `README.md` placeholder + `docs/CONFIGURATION.md`
- [ ] Verify with `uv sync` / `uv run pytest` / `uv run ruff check .` *(report results honestly; tooling availability permitting)*
- [ ] **Human developer review** of Phase 4 skeleton
- [ ] **ChatGPT reviewer approval** of Phase 4 skeleton
- [ ] **Commit** Phase 4 skeleton to Git
**Exit criteria:** `uv` install works; ruff runs; package imports cleanly — **reviewed per the Review Rule**.
**Status:** Skeleton created; **review/commit pending** — Phase 4 is *not yet reviewed/complete*, so Phase 5 remains gated. No orchestration/agent/provider/search logic implemented; no results/evidence produced.

---

## Phase 5 — Tests & Quality Gates
**Goal:** TDD scaffolding and automated gates before feature code.
- [x] `docs/QUALITY.md` *(gate purpose, commands, enforced-now vs later, xfail TDD policy)*
- [x] Quality scripts *(`scripts/check_required_docs.py`, `check_file_lengths.py` (≤150), `check_json_configs.py` — tooling only, relative paths, exit non-zero on failure)*
- [x] Config/hygiene tests *(`test_config_values.py`: tie-break=["con","pro"], retry=2, words 160/400, turns=10; `test_repo_hygiene.py`: required docs, .env absent/untracked, .env.example present; `test_quality_scripts.py`: scripts run clean)*
- [x] Behavioral **contract tests as xfail TDD placeholders** *(`tests/integration/test_contracts.py` — 13 contracts; suite still exits 0; no fake evidence)*
- [x] Coverage gate configured *(85% via `--cov-fail-under=85`, documented; not in default addopts)*
- [x] File-size + required-doc + JSON-config gate scripts
- [x] README "Current quality commands" section *(notes contracts are xfail until Phase 6)*
- [ ] Run all gates and report results honestly
- [ ] **Human developer review** of Phase 5
- [ ] **ChatGPT reviewer approval** of Phase 5
- [ ] **Commit** Phase 5 to Git
**Exit criteria:** Failing (xfail) contract tests exist for unbuilt features (TDD); gates wired and green — **reviewed per the Review Rule**.
**Status:** Created; **review/commit pending** — Phase 5 is *not yet reviewed/complete*, so **Phase 6 remains gated**. No debate/orchestration/agent/provider/search logic implemented; behavioral tests are xfail; no results/evidence produced. *(Real unit tests for schema/scoring/gatekeeper become non-xfail in Phase 6 alongside the implementation.)*

---

## Phase 6 — Implementation
**Goal:** Build features to make the tests pass.

### Phase 6.1 — Offline core slice *(✅ committed: `81eea84`)*
- [x] Protocol enums + models *(`protocol/enums.py`, `protocol/models.py`)*
- [x] Config loader *(`config/loader.py` — JSON, relative paths, validated)*
- [x] JSON/protocol validation *(`validation/protocol_validator.py`)*
- [x] Evidence structural validation *(`validation/evidence_validator.py` — untrusted-content rule)*
- [x] Response validation coordinator *(`validation/response_validator.py`)*
- [x] ValidationResult + EvidenceStore *(`validation/result.py`, `evidence/store.py`)*
- [x] Scoring rubric (0–5, sum) + deterministic configured tie-break *(`results/scoring.py`, `results/tie_breaker.py`)*
- [x] Unit tests for all the above + converted contract tests
- **Converted xfail → real (7):** no direct Pro↔Con routing · invalid JSON → regenerate · missing opponent_claim_id · missing evidence · irrelevant evidence · configured tie-break · prompt-injection cannot override rules
- **Still xfail (6):** judge selects exactly one winner · agreement collapse · off-side drift · retry exhaustion → failed run · provider timeout · watchdog → failed run
- [x] **Human review → ChatGPT approval → committed** *(Phase 6.1 reviewed and pushed as `81eea84` — "Implement offline core protocol validation and scoring")*
- **NOT implemented yet (later 6.x):** ClaudeCliProvider, DdgsSearchTool, Gatekeeper, JudgeAgent/Pro/Con, full DebateRunner + regeneration loop, Watchdog, SDK service, CLI behavior, cost accounting.

### Phase 6.2a — Offline provider/search abstractions *(created; review/commit pending)*
- [x] `providers/base.py` *(`ProviderAdapter`, `ProviderError`, `ProviderTimeoutError`)*
- [x] `providers/mock_provider.py` *(`MockProvider` — scripted, call count, deterministic timeout/error; no sleep/network/LLM)*
- [x] `search/base.py` *(`SearchTool`, `SearchError`)*
- [x] `search/mock_search.py` *(`MockSearchTool` — relevant/irrelevant/malicious modes, call count, deterministic error; no web/ddgs)*
- [x] Unit tests for both mocks
- **xfail contracts converted in 6.2a:** none (all 6 remain — they need the runner/judge/watchdog from 6.2b/6.2c)
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.2a)

### Phase 6.2b — Resource control & run safety *(created; review/commit pending)*
- [x] `results/cost_tracker.py` *(`CostTracker` — provider/search/retry counts, token estimates chars/4, injectable runtime, estimate-only summary; no file writing)*
- [x] `quality/gatekeeper.py` *(`Gatekeeper`, `GatekeeperError` — configurable max provider/search/retry/token limits; reads CostTracker; no provider/search calls)*
- [x] `orchestration/watchdog.py` *(`Watchdog`, `WatchdogError` — run-level stalled/retry-loop/max-runtime triggers; injectable time source; deterministic, no sleep)*
- [x] Unit tests for all three
- **xfail contracts converted in 6.2b:** none (provider-timeout, watchdog, retry-exhaustion contracts stay xfail until DebateRunner integrates these primitives in 6.2c)
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.2b)

### Phase 6.2c — Offline debate orchestration with mocks *(created; review/commit pending)*
- [x] `orchestration/session.py` *(`RunStatus`, `DebateSessionResult`, `ProtocolFailure`; failed runs preserve messages/errors/cost)*
- [x] `agents/base.py` + `agents/debate_agent.py` *(`DebateAgent`, `ProAgent`, `ConAgent` — no opponent reference)*
- [x] `agents/judge.py` *(`JudgeAgent` — ResponseValidator + deterministic collapse/drift markers; scoring + configured tie-break)*
- [x] `orchestration/runner.py` *(`DebateRunner` — parent-mediated routing, regeneration ≤ retry_cap, failed-protocol on exhaustion/timeout/watchdog; wires CostTracker/Gatekeeper/Watchdog)*
- [x] `results/transcript_writer.py` *(`TranscriptWriter` — writes only to an explicit output dir; tests use tmp_path; no committed artifacts)*
- [x] Unit tests (session result, transcript writer, agents, debate runner) + contract conversions
- **Converted xfail → real (6):** judge selects exactly one winner · agreement collapse rejected/regenerated · off-side drift rejected/regenerated · retry exhaustion → failed run · provider timeout handled → failed run · watchdog → failed run
- **Remaining strict-xfail contracts:** none (all 13 contracts now real and passing)
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.2c)

### Phase 6.3a — Offline mock SDK + thin CLI *(created; review/commit pending)*
- [x] `sdk/service.py` *(`run_mock_debate` — wires mocks + DebateRunner; returns DebateSessionResult; writes only when output_dir given)*
- [x] `cli/main.py` *(thin `argparse` wrapper; `agent-debate mock-run` with `--turns-per-side`/`--session-id`/`--output-dir`; calls SDK only)*
- [x] Console entry point `agent-debate` → `agent_debate.cli.main:main` *(already wired in pyproject.toml)*
- [x] Unit tests (`test_sdk_service.py`, `test_cli.py` — success, no-default-artifacts, output-dir under tmp_path, CLI delegates to SDK, failed→exit 1)
- [x] README offline mock CLI usage/status
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.3a)

### Phase 6.3b — Claude CLI provider class *(created; review/commit pending)*
- [x] `providers/claude_cli_provider.py` *(`ClaudeCliProvider` implements `ProviderAdapter` via configurable `subprocess.run`: command/timeout/input_mode; timeout→`ProviderTimeoutError`, nonzero/empty→`ProviderError`; no secrets/paths; command list not mutated)*
- [x] `config/providers.json` *(added `input_mode` to `claude_cli`; `mock` stays the active default)*
- [x] Unit tests `test_claude_cli_provider.py` *(mock `subprocess.run`; stdin/argument modes, nonzero, empty+stderr, timeout, call_count, no-mutation, invalid input_mode, empty command — no real Claude call)*
- [x] README/CONFIG honesty: provider exists, NOT used by default CLI, tests mock subprocess, no real run yet
- **subprocess policy:** allowed only in `providers/claude_cli_provider.py` (production) + mocked/benign test usage
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.3b)

### Phase 6.3c — Real search provider class *(created; review/commit pending)*
- [x] `search/real_search.py` *(`RealSearchTool` implements `SearchTool`; converts raw results → `EvidenceRecord`; injected search backend; conservative `relevance_status="relevant"`; untrusted snippet kept as data; wraps backend errors as `SearchError`)*
- [x] `config/search.json` *(added `provider_name` + status note to `ddgs`; `mock` stays active default)*
- [x] Unit tests `test_real_search.py` *(fake injected backend: success, empty, error→SearchError, session/claim carried, malicious-snippet-as-data, call_count, default clock — no web calls)*
- [x] README/CONFIG honesty: real search class exists, NOT default, tests mock backend, no web, live validation deferred to Phase 7
- **Dependency:** none added — DI of a backend callable avoids a heavy/network dep now; concrete `ddgs` backend + dependency added when real-mode is wired
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.3c)

### Phase 6.3d — Real-mode wiring (mock default, no live calls in tests) *(created; review/commit pending)*
- [x] `providers/factory.py` *(`build_provider` — mock | claude_cli; combines command+args; no execution at construction; `ProviderConfigError`)*
- [x] `search/factory.py` *(`build_search` — mock | ddgs/real_search; injectable backend; no web at construction; `SearchConfigError`)*
- [x] `search/ddgs_backend.py` *(`ddgs_search` — lazy optional `ddgs` import + injectable `client_factory`; maps to {title,url,snippet}; clear `SearchError` if `ddgs` missing)*
- [x] `config/loader.py` *(added `load_raw_config` for providers/search JSON)*
- [x] `sdk/service.py` *(`run_mock_debate` behavior preserved via shared `_run_debate`; new `run_configured_debate(provider, search, …, overrides)`)*
- [x] `cli/main.py` *(added `agent-debate run --provider --search …`; mock default; REAL MODE warning; calls SDK only)*
- [x] Tests: provider/search factories, ddgs backend mapping + missing-dep error, configured SDK run + overrides, CLI run mock + real (monkeypatched); `mock-run` unchanged
- **Dependency:** none added — lazy `ddgs` import + injectable client; offline gate stays clean
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.3d)

### Phase 6.4 — Project-local prompt templates *(created; review/commit pending)*
- [x] Prompt files: `prompts/agents/{judge,pro,con}.md`, `prompts/protocol/{regeneration,final_judgment}.md`
- [x] `config/agents.json` references them by **relative** paths (`prompts_dir` + `prompt_template`/`protocol_prompts`)
- [x] `prompts/` package: `loader.py` (rejects absolute/`..`, `PromptError` on missing) + `templates.py` (`{placeholder}` renderer; no eval/exec; fail-clear on missing value)
- [x] Tests: files exist, loader local/absolute/traversal/missing, renderer fill/fail/ignore-JSON-braces, required protocol terms, config references valid
- [x] `docs/PROMPTS.md` (design, list, why-not-global-skills, placeholders, safety) + README/CONFIGURATION updates
- **No behavior change** to DebateRunner/agents (prompts not yet wired into `produce()`); **no real Claude/web**; mock stays default
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.4)

### Phase 6.5 — Prompt wiring & real-run readiness *(created; review/commit pending)*
- [x] `agents/base.py` *(`DebateAgent.produce` renders the project-local Pro/Con template + per-turn context — topic/role/claim_id/opponent_claim_id/evidence_refs/JSON — and sends it to the provider)*
- [x] `agents/judge.py` *(JudgeAgent holds regeneration/final/judge templates; `regeneration_prompt()` + `final_instructions()` render them; scoring stays deterministic, disclosed in `limitations`)*
- [x] `sdk/service.py` *(loads templates + topic from config and wires them into agents/Judge; `run_mock_debate` behavior unchanged)*
- [x] Tests: Pro/Con send rendered local prompt (spy provider), Judge renders local protocol templates; existing offline mock debate/CLI unchanged
- **Resolved gap:** Pro/Con argument prompts now wired into runtime (REAL_RUN_PLAN §8 updated)
- **Remaining gap (honest):** Judge final scoring still deterministic/offline (not content-derived); collapse/drift still marker-based; `ddgs` not installed; Claude login unverified
- **No real Claude/web call; mock stays default**
- [x] **Human review** → **ChatGPT approval** → **committed** (Phase 6.5)

### Phase 6.6 — Content-aware Judge readiness *(created; review/commit pending)*
- [x] `agents/judge.py` *(optional `judge_provider`; `judge()` deterministic by default, provider-backed when supplied — renders final-judgment prompt incl. topic/transcript-summary/rubric/no-tie/tie-break, parses+validates JSON verdict; honest `limitations`)*
- [x] `results/scoring.py` *(`parse_judgment` + `scores_from_data` + `JudgeError` — safe JSON validation, no eval: winner∈{pro,con}, loser opposite, reasoning required, 0–5 dim scores)*
- [x] `orchestration/runner.py` *(passes accepted `messages` to `judge()` — one line; no behavior change for deterministic/mock)*
- [x] Tests: deterministic default, provider-backed valid (MockProvider) selects one winner, invalid/bad-winner/tie/empty-reasoning rejected with `JudgeError`, end-to-end via runner; mock CLI unchanged
- **Improved readiness:** optional content-aware Judge available (mock-tested), wired through the runner
- **Remaining (honest):** no real Claude judgment run; `ddgs` not installed; Claude login unverified; no `judge_provider` wired into CLI/SDK yet
- **No real Claude/web call; mock stays default**
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.6)

### Phase 6.7 — Wire judge-provider selection into SDK/CLI *(created; review/commit pending)*
- [x] `providers/factory.py` *(`build_judge_provider(name, provider_config, *, override)` → `None` for none/deterministic, `MockProvider([canned verdict])` for mock, `build_provider(active=claude_cli)` for claude_cli, `ProviderConfigError` otherwise; never executes a provider)*
- [x] `sdk/service.py` *(`run_configured_debate` gains `judge_provider="none"` + `judge_provider_override`; builds the judge via factory and threads it into `JudgeAgent`; deterministic stays default; `run_mock_debate` unchanged)*
- [x] `cli/main.py` *(`run --judge-provider none|deterministic|mock|claude_cli`, default `none`; prints `judge: <name>`; warns + flags REAL MODE for `claude_cli`; passes through to SDK)*
- [x] Tests: SDK deterministic default, `judge_provider_override`, `judge_provider="mock"`; CLI default prints `judge: none`, `--judge-provider mock` runs offline, `claude_cli` monkeypatched (warns, no real Claude); factory cases incl. override + unsupported; mock-run unchanged
- **Improved:** the 6.6 content-aware Judge is now reachable from SDK/CLI without code edits — a per-run flag
- **Remaining (honest):** no real Claude judgment run; `ddgs` not installed; Claude login unverified
- **No real Claude/web/subprocess call; mock + deterministic judge stay default**
- [x] **Human review** → **ChatGPT approval** → **commit** (Phase 6.7) *(committed `7aa8e2f`)*

### Phase 6.8 — Add `ddgs` dependency without live search *(created/in progress; review/commit pending)*
- [x] `uv add ddgs` *(declared in `pyproject.toml` as `ddgs>=9.14.4`; pinned in `uv.lock`; comment updated to reflect the real-search-only, explicit-opt-in usage)*
- [x] Verified import availability only: `ddgs_available=True` *(no `DDGS()` instance, no `.text()` query, no web call)*
- [x] `tests/unit/test_ddgs_backend.py` *(technical fix: with `ddgs` now importable, the missing-dep test blocks the import via `sys.modules` so the `SearchError` branch stays offline; added an import-availability-only test; mapping test unchanged)*
- **Improved:** the real `ddgs` search backend is now installable/runnable for the controlled Phase 7 run — selected only via `--search ddgs`
- **Remaining (honest):** no live `ddgs` query executed; no real Claude judgment run; Claude CLI login unverified; real evidence-backed run is still Phase 7
- **No live search, no real Claude/LLM call, no web query; mock stays default**
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 6.8)

### Real-run prep (later)
- [ ] Decide whether the real run uses the provider-backed Judge; declare `ddgs` optional extra
**Exit criteria:** All tests green; gates pass; no hardcoded params; **real evidence-backed run is Phase 7** (controlled, manual).

### Phase 7.0 — Real run preflight plan *(created; review/commit pending — NO real run executed)*
- [x] `docs/REAL_RUN_PLAN.md` *(purpose, mode table, preflight checklist, planned command, output dir + artifacts, safety rules, rollback, §8 known prompt-wiring limitation)*
- [x] Safe preflight checks only *(git clean; ruff/pytest/required-docs/file-lengths/json-configs green; `claude` installed = 2.1.159; `ddgs_available=False`)*
- **Decision:** first controlled real run = **2 turns/side**, then **10/side** only after it succeeds; each run into a fresh timestamped `results/real_run_*/`
- **Not done:** real run NOT executed; no Claude prompt sent; no web call; `ddgs` not installed; no results/evidence produced
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 7.0)

### Phase 7.1 — Claude CLI login preflight *(created/in progress; review/commit pending — NO real run executed)*
- [x] Safe environment checks only *(`git status` clean; Claude CLI on PATH at `~/.local/bin/claude`; `claude --version` → `2.1.160 (Claude Code)`; inspected `claude --help` + `claude auth --help`)*
- [x] **Login VERIFIED** via the non-prompt `claude auth status` → `loggedIn: true` (claude.ai, first-party). **No prompt sent, no debate run, no API debate call.** (Status only; email/orgId/account/subscription details intentionally not persisted here.) Auth is time-bound — **re-check immediately before the Phase 7 real run.**
- [x] Project checks green: `pytest` 211 passed; required-docs / file-lengths / json-configs OK; `find results logs` → only `.gitkeep`
- [x] Updated `docs/REAL_RUN_PLAN.md` §3 + §8 *(Claude CLI installed + login verified; real run still not executed)*
- **No code changed; no provider executed; no live ddgs search; no artifacts created**
- **Remaining (honest):** the controlled real run itself (debate prompt + live `ddgs` + artifacts) is still Phase 7 proper — NOT executed
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 7.1)

### Phase 7.2 — First controlled real run *(ATTEMPTED; FAILED HONESTLY — evidence preserved)*
- [x] Executed (approved) `run --provider claude_cli --search ddgs --judge-provider claude_cli --turns-per-side 2 --output-dir results/real_run_20260602_1837`
- **Outcome:** `failed_protocol — retry exhausted: word_limit_exceeded`; 3 real Claude calls, 3 real ddgs searches, 0 accepted turns, no winner, ~155 s. Partial transcript + `error_report.md` + `cost_report.json` kept as honest evidence.
- **NOT a success:** no winner declared; artifacts left **untracked** (not deleted, not committed yet)

### Phase 7.3 — Failed-run review & fix plan *(diagnosis only; no code change)*
- [x] Diagnosed root causes: limit never stated to model; prompt↔code JSON contradiction; regeneration re-sends the same prompt; 160 tight. Recommended Option C.

### Phase 7.4 — Word-limit + prompt tuning fix *(created/in progress; review/commit pending — NO real run)*
- [x] `config/debate.json` child word limit **160 → 220** (moderate; retry cap unchanged)
- [x] `base.py` / `service.py` thread the **configured** limit into Pro/Con agents + Judge validator (config is source of truth; not hardcoded in prompts)
- [x] `prompts/agents/pro.md`, `con.md`, `protocol/regeneration.md` — state the limit via `{word_limit}`, ask for **argument text only** (no full-JSON instruction); Judge prompts still use JSON (the Judge parses JSON)
- [x] Tests: provider-received Pro/Con prompts include the configured limit; prompts no longer instruct full JSON; regeneration renders the limit; mock-run unchanged
- **No real Claude/LLM call; no live ddgs/web search; failed-run artifacts untouched/uncommitted**
- **Remaining (honest):** regeneration is still a no-op in the runner (separate later fix); second real run not yet executed
- [x] **Human review** → **ChatGPT approval** → **commit** (Phase 7.4) *(committed `52cb68a`)*

### Phase 7.5 — Second controlled real run *(ATTEMPTED; FAILED HONESTLY — partial progress)*
- [x] Executed (approved) the same 2-turn command into a fresh dir `results/real_run_20260602_1912`
- **Outcome:** `failed_protocol — retry exhausted: word_limit_exceeded`, but **partial progress**: Pro opening **accepted** (`word_count: 219`, 5 evidence refs) — 7.4 fix works — then Con opening failed after 1 + 2 retries (4 Claude calls, 4 ddgs searches, ~82 s, no winner). Evidence preserved, untracked.
- **Diagnosis:** retries were a no-op (runner re-sent the identical prompt), so Con never got to shorten.

### Phase 7.6 — Real regeneration wiring *(created/in progress; review/commit pending — NO real run)*
- [x] `runner.py` — on retry, build `JudgeAgent.regeneration_prompt(reason)` and pass it into `agent.produce(..., regeneration=...)`; `retry_cap` unchanged; failure-on-exhaustion preserved
- [x] `base.py` — `produce`/`_build_prompt` accept optional `regeneration`; first attempt unchanged; retry appends a "Correction required" block (validation error + word limit, argument text only, no JSON)
- [x] `prompts/agents/pro.md`, `con.md` — margin instruction (aim ~180–200 words; hard limit stays {word_limit}=220)
- [x] Tests: runner retry sends a CHANGED, error-aware prompt (contains `word_limit_exceeded` + the limit, no JSON); a mocked over-limit first attempt recovers on a shorter retry; retry exhaustion still fails; mock-run/configured-mock unchanged
- **No real Claude/LLM call; no live ddgs/web search; both failed-run dirs untouched/uncommitted**
- **Remaining (honest):** `child_turn_max_words` unchanged (220); third real run not yet executed
- [ ] **Human review** → **ChatGPT approval** → **commit** (Phase 7.6)

---

## Phase 7 — Real Debate Run *(NOT started — preflight plan in `docs/REAL_RUN_PLAN.md`)*
**Goal:** Execute a genuine, evidence-producing debate.
- [ ] Choose a topic with real contradiction
- [ ] Run full debate (≥10/side, or documented 5/side budget mode)
- [ ] Capture transcript (Markdown + JSONL)
- [ ] Capture logs and cost report
**Exit criteria:** A complete, rule-compliant debate with a single winner is recorded.

---

## Phase 8 — Documentation, Transcript, Screenshots
**Goal:** Produce the professional submission artifacts.
- [ ] Write rich `README.md` (all required sections)
- [ ] Add prompts log
- [ ] Add transcript files to `results/`
- [ ] Add labeled screenshots (CLI, tests, debate output) to `assets/`
- [ ] Document cost/resource awareness & limitations
**Exit criteria:** README complete; all evidence present and legible.

---

## Phase 9 — Final Audit & Submission Readiness
**Goal:** Verify everything against the acceptance checklist.
- [ ] Walk the acceptance checklist in REQUIREMENTS_AUDIT §10
- [ ] Confirm no secrets in history; `.env` ignored
- [ ] Confirm quality gates all pass
- [ ] Confirm repo accessible to instructor; commit history is progressive
- [ ] Final review of grading risks (REQUIREMENTS_AUDIT §8)
**Exit criteria:** Every acceptance item checked with evidence; ready to submit.
