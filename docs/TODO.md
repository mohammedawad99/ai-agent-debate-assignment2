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
- [ ] Unit tests: schema validation, scoring, tie-break, side-fidelity, config, gatekeeper
- [ ] Integration test: parent-mediated routing (no child↔child path)
- [ ] E2E test: short bounded debate with mocked provider + mocked search
- [ ] Coverage gate configured
- [ ] File-size + required-doc gate scripts
- [ ] CI-style quality command (run all gates locally)
**Exit criteria:** Failing tests exist for unbuilt features (TDD); gates wired.

---

## Phase 6 — Implementation
**Goal:** Build features to make the tests pass.
- [ ] Provider adapter (API key and/or CLI-subprocess) with timeouts
- [ ] Search/evidence adapter
- [ ] Gatekeeper (rate/budget/concurrency)
- [ ] Agents (Pro, Con) + Judge orchestration & routing
- [ ] JSON protocol + validation + regeneration loop
- [ ] Scoring, rubric, tie-break, winner selection
- [ ] Watchdog/keep-alive
- [ ] SDK layer + CLI that calls only the SDK
- [ ] Cost/resource accounting
**Exit criteria:** All tests green; gates pass; no hardcoded params.

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
