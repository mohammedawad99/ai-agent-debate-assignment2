# Requirements Audit — Assignment 2: AI Agent Debate System

> Status: **Stage 0 — Requirements analysis only.** No implementation has begun.
> This document is the authoritative extraction of *what must be true* for the
> project to be considered complete and correct. Every later document (PRD,
> PLAN, TODO) and every line of code must trace back to a requirement here.

---

## 1. Explicit Requirements (stated directly in the assignment)

### 1.1 Roles & Orchestration
- **R-01** Three distinct agent roles must exist:
  - **Parent/Judge Agent** — moderates, routes messages, enforces rules, decides the winner.
  - **Pro Agent** — argues *for* one side.
  - **Con Agent** — argues *against* (the opposite side).
- **R-02** All child-to-child communication **must pass through the Parent/Judge**.
- **R-03** Direct Pro ↔ Con communication is **forbidden**.
- **R-04** The Judge must **choose a winner** — a **tie is not allowed**.

### 1.2 Debate Content & Dialogue Quality
- **R-05** The topic is free but must create a **real contradiction** (genuine two-sided tension).
- **R-06** The debate must be **respectful**.
- **R-07** The debate must be **bounded** by number of turns **or** words.
- **R-08** A full run must contain **≥ 10 arguments/pings per side**.
- **R-09** If a real budget limit applies, **5 per side** is allowed **only if explicitly documented in README**.
- **R-10** Each agent must **respond to the opponent's previous argument** — real dialogue, not disconnected monologues.
- **R-11** The Judge must **prevent agreement collapse** (one agent drifting into agreeing with the other).
- **R-12** The Judge must **reject / request regeneration** when an agent fails to hold its assigned side.
- **R-13** Judging is based on **persuasiveness**, not only factual correctness.
- **R-14** The Judge must use a **clear rubric**: clarity, responsiveness, rebuttal quality, evidence quality, consistency, respectful tone, persuasive force.

### 1.3 Evidence & Knowledge
- **R-15** **Internet/search evidence is required.**
- **R-16** Full RAG / vector DB is **optional**, not mandatory.

### 1.4 Protocol & Delivery
- **R-17** Inter-agent communication should use **structured JSON**.
- **R-18** Final deliverable must be **Python code that orchestrates the agents**.
- **R-19** Manual Claude CLI experiments are allowed and may be documented, but the final submission **must not be only a manual CLI workflow**.
- **R-20** Connection may be via **API key** *or* a **login-based CLI provider invoked through Python subprocesses**.
- **R-21** **Project-local** prompts/skills must be used — **do not rely on global Claude skills**.

---

## 2. Implicit Requirements (not stated, but necessary to satisfy the explicit ones)

- **I-01** A **turn/state machine** is required to enforce the parent-mediated routing (R-02/R-03) and the turn/word bounds (R-07/R-08).
- **I-02** A **persistent shared debate context** so each agent can see the opponent's last argument (needed for R-10) — but only what the Judge forwards.
- **I-03** A **side-fidelity check** mechanism (classifier or Judge sub-prompt) to detect agreement collapse and off-side drift (R-11/R-12), plus a **regeneration loop** with a retry cap.
- **I-04** A **deterministic, reproducible transcript record** (the dialogue must be replayable / auditable) to back R-08 and documentation requirements.
- **I-05** A **search/evidence adapter** with a defined interface (so the provider can be swapped) to satisfy R-15 without hardcoding one search vendor.
- **I-06** **Schema validation** of the JSON messages (R-17) — malformed agent output must be detected and regenerated, not crash the run.
- **I-07** A **scoring/aggregation function** that combines rubric dimensions into a single comparable score and guarantees a non-tie outcome (R-04/R-14) — including a documented **tie-break rule**.
- **I-08** **Determinism / seed / temperature control** documented so results are interpretable.
- **I-09** **Graceful degradation**: when search or a provider call fails, the system must continue or fail cleanly with a logged reason (supports watchdog/timeout reqs).
- **I-10** **Cost/turn accounting** surfaced to the user (tokens, calls, estimated cost) — implied by cost-awareness expectations.

---

## 3. Engineering Requirements

- **E-01** Language: **Python**.
- **E-02** **Object-oriented design**.
- **E-03** **No duplicated code** (DRY).
- **E-04** **SDK layer**: all business logic accessible via an SDK; the **CLI only calls the SDK** (no logic in CLI).
- **E-05** **Terminal/CLI interface** provided; GUI not required.
- **E-06** **Timeouts** on every agent/provider call.
- **E-07** **Watchdog / keep-alive** behavior for autonomous/long-running processes.
- **E-08** **Gatekeeper / resource-control layer** for all LLM / CLI-provider calls (rate limiting, concurrency, budget caps).
- **E-09** **Structured logs** with **configurable rotation**.
- **E-10** **Configuration files** for: debate settings, agents, logging, rate limits, provider settings.
- **E-11** **No hardcoded** paths, magic numbers, provider settings, model names, or debate parameters.
- **E-12** **Tests** with **TDD-oriented** development.
- **E-13** **Ruff** / linter.
- **E-14** **uv** + **pyproject.toml** for reproducible setup.
- **E-15** **Quality gates**: ruff, format check, pytest, coverage, file-size checks, required-doc checks.
- **E-16** **mypy** considered if practical.

---

## 4. Documentation Requirements

- **D-01** **Rich, professional README.md**.
- **D-02** README sections: problem, setup, usage, architecture, debate flow, screenshots, quality commands, cost/resource awareness, limitations, reproducibility.
- **D-03** Include **prompts** used during development and/or the debate.
- **D-04** Include a **full debate transcript** in **Markdown and/or JSONL**.
- **D-05** Include **screenshots** of CLI execution, tests, and final debate output.
- **D-06** Include **evidence/logs/results** proving the system ran.
- **D-07** Transcript language: **English or Hebrew, not Arabic** (English recommended for cost/reliability).
- **D-08** **GitHub repo accessible to the instructor**.
- **D-09** **Commit history** shows real development progression.
- **D-10** If 5-per-side budget mode is used, it must be **explicitly documented** (ties to R-09).

---

## 5. Testing Requirements

- **T-01** TDD-oriented: tests written alongside / before implementation.
- **T-02** **Unit tests** for: JSON schema validation, scoring/aggregation, tie-break, side-fidelity detection, config loading, gatekeeper limits.
- **T-03** **Integration tests** for the parent-mediated routing (proving R-02/R-03 — no direct child-to-child path exists).
- **T-04** Tests must run **without live network / live LLM** (mock the provider and the search adapter) so the suite is deterministic and free to run.
- **T-05** **Coverage** measured and reported as a quality gate.
- **T-06** At least one **end-to-end test** of a short bounded debate using mocked providers.

---

## 6. Configuration & Security Requirements

- **C-01** **API keys must never be committed.**
- **C-02** **.env must be gitignored.** (Verified present in current `.gitignore`.)
- **C-03** **.env.example** committed **later** as a template — **not now** unless needed.
- **C-04** All tunable behavior driven by **config files**, not code constants (ties to E-10/E-11).
- **C-05** Secrets loaded **only** from environment / .env at runtime.
- **C-06** Logs must **not leak secrets** (no API keys in log output).
- **C-07** Project-local prompts/skills stored in-repo (ties to R-21).

---

## 7. Cost / Resource Requirements

- **CR-01** README must include **cost/resource awareness**.
- **CR-02** **Gatekeeper** enforces call/rate/budget limits (E-08).
- **CR-03** Per-run accounting of **calls, tokens, and estimated cost** surfaced to the user.
- **CR-04** **Budget mode** (5/side) supported and documented as an explicit, configurable fallback (R-09/D-10).
- **CR-05** Default to **English** debate output to reduce token cost (D-07).
- **CR-06** **Timeouts** prevent runaway cost from hung calls (E-06).

---

## 8. Grading Risks (where points are most likely lost)

| # | Risk | Severity | Mitigation owner |
|---|------|----------|------------------|
| G-01 | Starting to code before PRD/PLAN/TODO exist (repeat of A1 feedback) | **High** | PROJECT_RULES enforces gate |
| G-02 | Judge produces a tie or no clear winner | **High** | Mandatory tie-break rule (I-07) |
| G-03 | Direct Pro↔Con communication leaks into design | **High** | Integration test proving only parent-routed path (T-03) |
| G-04 | Disconnected monologues instead of real rebuttal | **High** | Each turn must cite/respond to opponent's last (R-10) |
| G-05 | No real internet evidence used | **High** | Search adapter is required, not optional (R-15) |
| G-06 | Unsupported "it works" claims with no evidence | **High** | Evidence/logs/screenshots required (D-05/D-06) |
| G-07 | Hardcoded model names / params | Medium | Config-driven; file-size + review gates |
| G-08 | Only a manual CLI workflow, no orchestrator | **High** | Python orchestrator is the deliverable (R-18/R-19) |
| G-09 | Secrets committed | **High** | .gitignore + .env.example only; pre-commit check |
| G-10 | Thin README / missing sections | Medium | README section checklist (D-02) |
| G-11 | Agreement collapse not handled | Medium | Side-fidelity check + regeneration (R-11/R-12) |
| G-12 | Relying on global Claude skills | Medium | Project-local prompts/skills only (R-21) |
| G-13 | Tests require live network → not reproducible | Medium | Mock providers (T-04) |
| G-14 | Fewer than 10/side without documenting budget mode | Medium | Enforce bound + README note (R-08/R-09) |

---

## 9. "Must NOT Do" List

- ❌ Do **not** write implementation/src code before PRD, PLAN, and TODO are approved.
- ❌ Do **not** allow direct Pro ↔ Con communication.
- ❌ Do **not** permit a tie outcome.
- ❌ Do **not** hardcode paths, model names, provider settings, magic numbers, or debate parameters.
- ❌ Do **not** commit `.env` or any secret/API key.
- ❌ Do **not** create fake evidence, transcripts, or screenshots.
- ❌ Do **not** claim the system works without reproducible evidence.
- ❌ Do **not** rely on global Claude skills — project-local only.
- ❌ Do **not** ship only a manual Claude CLI workflow as the final deliverable.
- ❌ Do **not** put business logic in the CLI layer (must live in the SDK).
- ❌ Do **not** output the debate in Arabic.
- ❌ Do **not** let tests depend on live network / live LLM calls.

---

## 10. Acceptance Checklist (Definition of Done)

Each item must be **demonstrable with evidence** before submission.

### Functional
- [ ] Three roles implemented (Judge, Pro, Con).
- [ ] All messages routed through the Judge; no direct child-to-child path (proven by test).
- [ ] Topic creates a genuine contradiction.
- [ ] Debate bounded by turns/words via config.
- [ ] ≥ 10 args/side (or 5/side **with** documented budget mode).
- [ ] Every turn responds to the opponent's previous argument.
- [ ] Agreement collapse detected and prevented.
- [ ] Off-side drift rejected with regeneration.
- [ ] Judge selects a single winner with a rubric-based rationale; no tie.
- [ ] Internet/search evidence used and visible in the transcript.
- [ ] Inter-agent messages are structured JSON, schema-validated.

### Engineering
- [ ] OO design; no significant duplication.
- [ ] SDK layer; CLI only calls SDK.
- [ ] Timeouts on all provider/agent calls.
- [ ] Watchdog/keep-alive for long runs.
- [ ] Gatekeeper enforces rate/budget/concurrency.
- [ ] Structured logs with configurable rotation.
- [ ] All settings in config files; nothing hardcoded.
- [ ] uv + pyproject.toml reproducible install.
- [ ] Ruff + format check pass.
- [ ] pytest passes; coverage reported.
- [ ] File-size and required-doc gates pass.
- [ ] mypy run if practical.

### Documentation & Security
- [ ] Professional README with all required sections.
- [ ] Prompts documented.
- [ ] Full transcript (Markdown and/or JSONL) included.
- [ ] Screenshots of CLI, tests, and debate output.
- [ ] Logs/results evidence included.
- [ ] Cost/resource awareness documented.
- [ ] .env ignored; .env.example template present (added later).
- [ ] No secrets in history.
- [ ] Repo accessible to instructor; commit history shows progression.
- [ ] Transcript in English (or Hebrew), not Arabic.

---

## 11. Recorded Decisions (Gate 0)

These are the binding decisions made at Gate 0. They resolve the open questions
from the initial audit and constrain the PRD, PLAN, and architecture. Each
decision references the requirement(s) it satisfies.

### DEC-01 — Provider path (satisfies R-18, R-19, R-20, E-04, E-02)
- **Primary planned provider:** **Claude Code / Claude CLI invoked through a Python
  subprocess.** Rationale: the developer works through Claude Code as a CLI in Ubuntu,
  so this is the lowest-friction, login-based path (no committed API key required).
- The architecture **must** expose a **`ProviderAdapter`** abstraction; the
  subprocess provider is one concrete implementation behind it.
- A **`MockProvider`** is **required** for deterministic, offline tests (ties to T-04).
- An **API-key provider** may be added later as a secondary, configurable provider
  — optional, not part of the initial scope.
- **No provider-specific logic may leak into the debate orchestration.** Orchestration
  depends only on the `ProviderAdapter` interface.

### DEC-02 — Search/evidence provider (satisfies R-15, R-16, I-05)
- The project **must** define a **`SearchTool`** abstraction.
- Tests **must** use a **`MockSearchTool`** (deterministic, offline).
- The planned real search option is a **configurable, no-key web search adapter**
  if practical (e.g. **DuckDuckGo / `ddgs`**), keeping the project key-free.
- The **final debate run must save evidence artifacts under `results/`** so the
  submission includes proof of internet/search-backed argumentation.
- **Full RAG / vector DB remains optional and out of scope** unless explicitly
  added later (confirms R-16).

### DEC-03 — Debate topic (satisfies R-05, R-06, R-13)
- **Planned topic:** *"Should university software engineering courses require
  students to use AI coding agents?"*
- **Rationale:** directly tied to the course subject, creates a genuine Pro/Con
  contradiction, supports persuasive (not merely factual) debate, and admits
  evidence-based arguments on both sides.

### DEC-04 — Budget / turn counts (satisfies R-07, R-08, R-09, E-11, CR-04)
- **Target final run:** **10 turns per side.**
- **Development / test runs:** **2–3 turns per side** (fast, cheap, deterministic).
- **5 turns per side** is **only a documented fallback** for genuine budget limits
  (must be noted in README if used — ties to D-10).
- **All turn counts must be configurable** (no hardcoded values — ties to E-11).

### DEC-05 — Transcript language (satisfies R-06, D-07, CR-05)
- **Debate transcript language: English.**
- **Rationale:** English reduces token cost, is well supported by LLMs (higher
  reliability), and is acceptable for submission. (Arabic remains explicitly
  disallowed for the transcript.)

---

## 12. Source Materials & Traceability

This repository **does not include the instructor's original PDFs, lecture slides,
or assignment briefs**, in order to **avoid committing copyrighted course
materials** to a (publicly accessible) GitHub repository.

Instead, the requirements in this document are **derived and paraphrased** from the
lecture/assignment materials and the Assignment 1 feedback, and are organized into
traceable IDs (`R-`, `I-`, `E-`, `D-`, `T-`, `C-`, `CR-`, `G-`, `DEC-`). Every later
artifact (PRD, PLAN, ARCHITECTURE, code, tests) cites these IDs so the chain from
"course requirement" → "design" → "implementation" → "evidence" stays auditable
without redistributing the source files.

If the instructor needs to verify a requirement against the original brief, the ID
labels here make it straightforward to cross-reference the corresponding section of
the course materials.
