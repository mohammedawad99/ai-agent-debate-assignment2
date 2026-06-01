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

### Phase 6.3+ — real adapters & interface (later)
- [ ] Real provider adapter (Claude CLI subprocess, timeouts) behind `ProviderAdapter`
- [ ] Real search adapter (`ddgs`) behind `SearchTool`
- [ ] SDK service layer + thin CLI that calls only the SDK; project-local prompts
**Exit criteria:** All tests green; gates pass; no hardcoded params; real evidence-backed run reserved for Phase 7.
**Status:** Phase 6.1 / 6.2a / 6.2b committed; **Phase 6.2c created, review/commit pending** — not yet reviewed/complete. Offline orchestration only; no real provider/search; no committed results/evidence.

---

## Phase 7 — Real Debate Run
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
