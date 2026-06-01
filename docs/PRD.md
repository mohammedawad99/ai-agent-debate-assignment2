# Product Requirements Document — AI Agent Debate System

## 1. Title and Status

- **Product:** AI Agent Debate System (Assignment 2)
- **Document type:** Product Requirements Document (PRD)
- **Status:** **DRAFT — Phase 1.** Pending review per the [TODO Review Rule](./TODO.md#review-rule-definition-of-reviewed) (Claude creates → human reviews → ChatGPT reviewer approves → committed).
- **Implementation status:** **Not started.** No `src/` code, dependencies, or runtime artifacts exist yet. This document defines *what* will be built and *why*; the *how* belongs to `PLAN.md` (Phase 2) and `ARCHITECTURE.md` (Phase 3).
- **Traceability:** Every requirement here references Gate 0 IDs from [`REQUIREMENTS_AUDIT.md`](./REQUIREMENTS_AUDIT.md) (`R-`, `I-`, `E-`, `D-`, `T-`, `C-`, `CR-`, `DEC-`) and the rules in [`PROJECT_RULES.md`](./PROJECT_RULES.md).

---

## 2. Problem Statement

University and self-directed learners increasingly use AI coding agents, but the
deeper skill the course targets is **engineering the orchestration of AI agents** —
not just prompting a model for an answer. The exercise is to build a system in which
**multiple AI agents interact under supervision**, with controlled communication,
structured data exchange, evidence gathering, and an impartial decision process.

This project solves that by building a **Python orchestration system** that runs a
**structured, supervised debate** between a **Pro** agent and a **Con** agent,
moderated by a **Parent/Judge** agent that routes all messages, enforces the rules,
and declares a single winner.

> **Key framing:** The deliverable is an **engineered orchestration system**, *not*
> merely a debate transcript. A transcript is an *output/evidence artifact*; the
> graded product is the **software** that produces it reproducibly — with an SDK, a
> CLI, adapters, a gatekeeper, logging, tests, and quality gates. **Based on our
> interpretation of the assignment** (`R-18`, `R-19`, `G-08`), a hand-run Claude CLI
> conversation that merely looks like a debate would not, on its own, meet the
> submission requirement; a Python orchestrator is required.

---

## 3. Background and Course Context

This assignment sits in a course on AI-assisted software development. The PRD is
shaped by these themes:

- **Vibe Coding** — building software fluidly with an AI assistant, while still
  producing rigorous engineering artifacts (planning, tests, docs), not ad-hoc code.
- **AI agents, subagents, skills, commands** — the debate models a multi-agent
  system: a parent agent supervising two child agents, each with a defined role.
  Project-local prompts/skills are used (`R-21`, `PROJECT_RULES` RULE 9), not global
  Claude skills.
- **Context engineering** — each agent must receive exactly the context it needs
  (the opponent's *forwarded* last argument and the debate state) and nothing it
  must not have (no private channel to the opponent). This is the heart of
  parent-mediated routing (`R-02`, `R-03`, `I-02`).
- **Structured communication** — agents exchange **schema-validated JSON**, not free
  text, so messages are machine-checkable and auditable (`R-17`, `I-06`).
- **Lessons from Assignment 1 feedback** — the project explicitly prevents the seven
  weaknesses recorded in [`LESSONS_FROM_ASSIGNMENT1.md`](./LESSONS_FROM_ASSIGNMENT1.md)
  (`W-1`..`W-7`): plan first, make the AI workflow visible, track cost, automate
  quality, design for change, prove correctness with tests/evidence, and present
  legible input→expected→actual evidence.

---

## 4. Target Users / Stakeholders

| Stakeholder | Needs | Implications for the product |
|-------------|-------|------------------------------|
| **Student developer** (author) | Build, run, iterate, and debug the system locally on Ubuntu via Claude Code/CLI | Simple CLI entry point; fast dev runs (2–3 turns/side, `DEC-04`); readable logs |
| **Instructor / grader** | Verify the system meets requirements and actually ran | Reproducible setup, transcript + evidence + logs, professional README, clear winner rationale (`D-01..D-09`) |
| **Future developer / reviewer** | Understand, extend, or swap components | OO design, SDK layer, adapter abstractions, documentation (`E-02`, `E-04`, `DEC-01`, `DEC-02`) |
| **AI coding assistant** (used during development/debugging) | Inspect state and reproduce issues | Structured logs, deterministic mock-based tests, clear CLI commands (`E-09`, `T-04`) |

---

## 5. Product Goals (measurable)

| Goal | Measurable target | Source |
|------|-------------------|--------|
| **PG-1** Run a full debate | A configured run completes **10 turns per side** (20 child turns) plus a final judgment | `DEC-04`, `R-08` |
| **PG-2** Enforce parent-mediated routing | All child messages pass through the Judge; direct Pro↔Con messaging is **enforced by design and verified by tests** | `R-02`, `R-03`, `T-03` |
| **PG-3** Validate JSON messages | **100%** of accepted child turns are schema-valid JSON | `R-17`, `I-06` |
| **PG-4** Prevent agreement collapse | Off-side / agreement-collapse turns are detected and regenerated (bounded retries, max 2) | `R-11`, `R-12`, `I-03` |
| **PG-5** Require evidence-backed arguments | **100%** of accepted substantive child turns include ≥1 evidence reference, either newly retrieved via the SearchTool or reused from the evidence store | `R-15`, `DEC-02` |
| **PG-6** Produce a final decision with **no tie** | Exactly **one** winner, with a rubric-based rationale | `R-04`, `R-14`, `I-07` |
| **PG-7** Persist transcript/results/logs | Transcript (JSONL + Markdown), final judgment, evidence, and logs are written to disk | `D-04`, `D-06`, `DEC-02` |
| **PG-8** Provide CLI and SDK access | Debate is startable via CLI, which calls only the SDK | `E-04`, `E-05` |
| **PG-9** Reproducible setup + quality checks | `uv` install works; one command runs all quality gates | `E-14`, `E-15` |

---

## 6. Non-Goals / Out of Scope

- **NG-1** No GUI — a terminal/CLI interface is sufficient (`E-05`).
- **NG-2** No full RAG / vector database unless explicitly added later (`R-16`, `DEC-02`).
- **NG-3** No manual-only Claude CLI submission — the deliverable is the orchestrator (`R-19`, `G-08`).
- **NG-4** No "factual truth" as the **primary** judging criterion — judging is on **persuasiveness** per the rubric (factual/evidence quality is one dimension, not the whole) (`R-13`, `R-14`).
- **NG-5** No hardcoded, provider-specific debate logic — orchestration depends only on the `ProviderAdapter` abstraction (`DEC-01`, `E-11`, `PROJECT_RULES` RULE 10).
- **NG-6** No image/multimodal debate unless explicitly added later (text-only debate for this submission).
- **NG-7** No live-network dependency in the test suite (mocks only) (`T-04`).

---

## 7. Functional Requirements

> Implementation details are deferred to PLAN/ARCHITECTURE; these state *what* the
> product must do.

- **FR-01** The system supports **three roles**: a **Judge** (parent), a **Pro** agent, and a **Con** agent. *(R-01)*
- **FR-02** The **Judge initializes** the debate: it assigns sides, states the topic, and communicates the rules/constraints to both agents before the first turn. *(R-01)*
- **FR-03** **All child messages pass through the Judge** — Pro and Con never address each other directly; the Judge forwards (a possibly summarized/validated form of) the opponent's last argument. *(R-02, I-02)*
- **FR-04** There is **no code path enabling direct Pro↔Con communication**; this is enforced by design and proven by an integration test. *(R-03, T-03)*
- **FR-05** The **debate topic is configurable** (default: the `DEC-03` topic) via config, not hardcoded. *(R-05, E-11, DEC-03)*
- **FR-06** The **turn count is configurable** (per side) via config. *(R-07, E-11, DEC-04)*
- **FR-07** The **target full run is 10 turns per side**; dev/test runs may use 2–3; a documented 5/side fallback exists for budget limits. *(R-08, R-09, DEC-04)*
- **FR-08** All inter-agent messages use a **structured, schema-validated JSON protocol**. *(R-17, I-06)*
- **FR-09** **Each accepted child turn after the opening must reference the opponent's previous claim** via an **explicit claim-reference marker** (e.g. an `opponent_claim_id` or equivalent schema field — final field name deferred to ARCHITECTURE), so the reference is **machine-checkable** later, not just inferred from prose. This keeps the exchange a connected dialogue rather than disconnected monologues. *(R-10)*
- **FR-10** The **Judge validates role adherence** each turn (correct side, on-topic, respectful tone). *(R-12, R-06, R-11)*
- **FR-11** On **agreement collapse, off-side drift, invalid JSON, or rule violation**, the Judge **rejects the turn and requests regeneration**, up to a **maximum of 2 regeneration attempts** per turn. If the retries are exhausted, the **run is marked as a failed protocol run** (logged as such). The **final submission run must complete without any exhausted-retry failures**. This behavior is **verified by tests using `MockProvider`**. *(R-11, R-12, I-03, I-06)*
- **FR-12** **Substantive arguments must be evidence-backed.** Every accepted child turn must include **at least one evidence reference**, which may be **newly retrieved via the `SearchTool`** or an **explicit reuse of a previously collected item from the evidence store**. **A new live web search is not required on every turn**, but each substantive argument must carry evidence. Evidence references are **saved in the transcript/results artifacts** for auditing. *(R-15, DEC-02)*
- **FR-13** The Judge **must select exactly one winner** — **ties are forbidden**. The Judge computes a rubric score per side; if total scores are equal, a **deterministic tie-break** is applied in this fixed order: **(1) higher evidence quality → (2) stronger rebuttal/responsiveness → (3) fewer protocol violations/regenerations → (4) a forced final persuasive choice by the Judge**. *(R-04, I-07)*
- **FR-14** The Judge produces a **final report/judgment** with a rubric-based rationale, and the **full transcript and judgment are saved** to `results/`. *(R-14, D-04, DEC-02)*
- **FR-15** The system runs through a **Gatekeeper** that enforces rate/budget/concurrency limits, and every provider/search call has a **timeout**. *(E-06, E-08, CR-02)*
- **FR-16** The system emits **structured logs** (with configurable rotation) for every significant event (routing, validation, regeneration, scoring, errors). *(E-09)*
- **FR-17** The system reports **per-run resource accounting**. Because the Claude CLI subprocess path **may not expose exact token billing**, the project records **proxy metrics**: provider call count, **approximate input/output token estimates** (English characters ÷ 4), runtime, search call count, transcript size, and the configured turn count. **Cost reporting must clearly label these figures as estimates, not exact provider billing.** *(CR-03, I-10)*

---

## 8. Non-Functional Requirements

- **NFR-01 — Reproducibility.** `uv` + `pyproject.toml` produce an identical environment; runs are repeatable and documented. *(E-14, NFR for D-02)*
- **NFR-02 — Maintainability.** Object-oriented design, DRY, small focused modules (file-size gate). *(E-02, E-03, E-15)*
- **NFR-03 — Extensibility.** New providers/search tools/models added via config behind the `ProviderAdapter`/`SearchTool` abstractions, without touching orchestration. *(DEC-01, DEC-02, W-5)*
- **NFR-04 — Testability.** Components are injectable/mockable; logic lives in the SDK, callable without the CLI. *(E-04, E-12)*
- **NFR-05 — Deterministic tests with mocks.** The full suite runs offline using `MockProvider` and `MockSearchTool`; no live network/LLM. *(T-04, DEC-01, DEC-02)*
- **NFR-06 — Security.** API keys never committed; `.env` gitignored; secrets loaded only at runtime; logs never leak secrets. *(C-01, C-02, C-05, C-06)*
- **NFR-07 — Logging.** Structured, rotating, configurable logs; debuggable by a human or AI assistant. *(E-09)*
- **NFR-08 — Cost/resource awareness.** Configurable budgets, Gatekeeper enforcement, per-run cost reporting, English output to reduce tokens. *(CR-01..CR-06, DEC-05)*
- **NFR-09 — No secrets in Git.** Enforced by `.gitignore` and review; only `.env.example` (template) committed later. *(C-01, C-03)*
- **NFR-10 — Readable CLI output.** Human-legible progress and a clear final result; structured detail goes to logs/results. *(E-05, D-05)*
- **NFR-11 — Clear documentation.** Professional README with all required sections; prompts and decisions documented. *(D-01, D-02, D-03)*
- **NFR-12 — Configurability / no hardcoding.** All paths, model names, provider settings, and debate parameters come from config files. *(E-10, E-11)*
- **NFR-13 — Robustness / graceful degradation.** Provider/search failures and timeouts are handled with logged reasons, not crashes. *(I-09, E-06, E-07)*

---

## 9. User Stories

- **US-1 (Student).** *As a student developer, I want to start a debate from the CLI with a chosen topic and turn count, so I can run and observe the system end-to-end.* — covers FR-05, FR-06, FR-07, PG-8.
- **US-2 (Instructor).** *As an instructor/grader, I want to inspect the saved transcript, evidence, and logs, so I can verify the system actually ran and met the rules.* — covers FR-14, FR-16, PG-7, D-04/D-06.
- **US-3 (Developer).** *As a developer, I want to run the full test suite with `MockProvider` and `MockSearchTool` offline, so tests are deterministic and free.* — covers NFR-05, T-04.
- **US-4 (Reviewer).** *As a reviewer, I want to see the Judge's rubric-based rationale for why a side won, so the decision is transparent and not arbitrary.* — covers FR-13, FR-14, R-14.
- **US-5 (AI coding assistant).** *As the AI assistant used to build/debug this, I want structured logs and clear CLI commands, so I can reproduce and diagnose issues.* — covers FR-16, NFR-07, NFR-10.
- **US-6 (Cost-conscious operator).** *As an operator, I want a per-run cost/resource report and configurable budgets, so I can keep runs within limits.* — covers FR-15, FR-17, NFR-08.

---

## 10. Debate Protocol Requirements (product level)

These describe expected behavior, not data structures (schemas live in ARCHITECTURE).

- **DP-1 — Message lifecycle.** A turn is *requested* by the Judge → *generated* by a child agent → *validated* by the Judge (schema, side, topic, tone, rebuttal, evidence) → *accepted and forwarded* or *rejected and regenerated*. Only accepted turns enter the transcript. *(I-01, I-03, FR-08..FR-12)*
- **DP-2 — Role constraints.** Pro always argues the affirmative; Con always argues the negative; neither may switch, concede the core position, or merge with the opponent (agreement-collapse guard). *(R-11, R-12)*
- **DP-3 — Evidence requirement.** Substantive arguments must be evidence-backed: each accepted turn cites ≥1 evidence reference, either newly retrieved via the `SearchTool` or reused from the evidence store (a new live search is not required every turn). Evidence is stored in the transcript/results artifacts for auditing. *(R-15, DEC-02)*
- **DP-4 — Claim/rebuttal relationship.** Every accepted turn after the opening must explicitly engage the opponent's most recent claim (acknowledge → counter) via an explicit claim-reference marker (e.g. `opponent_claim_id`), keeping the exchange a connected, machine-checkable dialogue. *(R-10)*
- **DP-5 — Judge moderation.** The Judge is the sole router and rule-enforcer: it sets up the debate, mediates every message, enforces bounds and respectful tone, and triggers regeneration when needed. *(R-01, R-02, R-06, R-12)*
- **DP-6 — Final scoring rubric.** The Judge scores both sides on: **clarity, responsiveness, rebuttal quality, evidence quality, consistency, respectful tone, persuasive force**, aggregates to a single comparable score per side, and — if scores tie — applies the deterministic tie-break in FR-13 (evidence quality → rebuttal/responsiveness → fewer protocol violations/regenerations → forced final persuasive choice) to guarantee exactly one winner. *(R-14, I-07, R-13)*

---

## 11. Acceptance Criteria

Each criterion is concrete and verifiable (by test, transcript inspection, or log/CLI output).

- **AC-01** A full configured run produces **20 child turns (10/side) plus one final judgment**. *(FR-07, PG-1)*
- **AC-02** **Every accepted child turn is valid JSON** conforming to the message schema. *(FR-08, PG-3)*
- **AC-03** **Every accepted child turn after the opening carries an explicit opponent-claim reference marker** (e.g. `opponent_claim_id`), making the rebuttal link machine-checkable in the transcript. *(FR-09, DP-4)*
- **AC-04** **Every accepted substantive child turn includes ≥1 evidence reference** (newly retrieved or an approved reuse from the evidence store), and those references are saved in the transcript/results artifacts. *(FR-12, DP-3)*
- **AC-05** The Judge selects **exactly one winner**; **no run ends in a tie** (deterministic tie-break per FR-13). *(FR-13, PG-6)*
- **AC-06** **No direct Pro↔Con messages** appear in the transcript; direct child-to-child messaging is **enforced by design and verified by an integration test**. *(FR-04, PG-2, T-03)*
- **AC-07** The **CLI can start a debate through the SDK** and print a readable result. *(FR-01, PG-8, E-04)*
- **AC-08** **Tests run without real LLM/network access** using `MockProvider` (+ `MockSearchTool`) and pass deterministically. *(NFR-05, T-04)*
- **AC-09** Agreement collapse, off-side drift, and invalid JSON are **detected and regenerated**, verified by **tests in which `MockProvider` intentionally returns bad outputs** (e.g. an agreeing/off-side turn or malformed JSON); the **logs/results show the detection and the regeneration request**. *(FR-10, FR-11, PG-4)*
- **AC-09b** When regeneration retries (max 2) are exhausted, the run is **marked as a failed protocol run**, verified by a mock-driven test; the **final submission run must show no exhausted-retry failures**. *(FR-11)*
- **AC-10** A **final judgment artifact** and a **transcript artifact** are written under `results/`. *(FR-14, PG-7)*
- **AC-11** A **per-run resource/cost report** is produced. *(FR-17, NFR-08)*
- **AC-12** **All quality gates pass** (ruff, format, pytest, coverage, file-size, required-docs) via a single command. *(E-15, PG-9)*
- **AC-13** **No secrets** are present in the repository or logs. *(NFR-06, NFR-09)*

---

## 12. Evidence and Artifacts Expected

> These are produced in later phases (7–8); listed here so the target output is explicit.

- `results/debate_transcript.jsonl` — full machine-readable transcript (one JSON object per turn/event). *(D-04)*
- `results/debate_transcript.md` — human-readable transcript. *(D-04, D-07)*
- `results/final_judgment.json` and/or `results/final_judgment.md` — winner + rubric scores + rationale. *(FR-14)*
- `results/evidence/…` — saved search-evidence artifacts proving internet-backed arguments. *(DEC-02, R-15)*
- `results/cost_report.*` — per-run calls/tokens/estimated cost. *(CR-03)*
- `logs/` — structured, rotated run logs. *(E-09)*
- `assets/screenshots/` — labeled screenshots (CLI run, tests passing, final debate output), each showing **input → expected/target → actual**. *(D-05, W-7)*
- README execution-proof section linking the above. *(D-02, D-06)*
- Prompts and decisions docs (added in later phases). *(D-03)*

---

## 13. Constraints and Assumptions

- **CA-1** **Python** project. *(E-01)*
- **CA-2** **Ubuntu** development environment. *(DEC-01)*
- **CA-3** **Claude Code / Claude CLI** is the primary development workflow and the primary provider path (via subprocess). *(DEC-01)*
- **CA-4** The provider **may be unavailable or slow**; the system must apply timeouts and degrade gracefully. *(E-06, I-09, NFR-13)*
- **CA-5** **Search may fail or return nothing**; errors must be handled and logged, not fatal. *(I-09, DEC-02)*
- **CA-6** **API keys are optional** (primary path is login-based CLI) and must be **externalized** via `.env`/environment when used. *(R-20, C-01, C-05)*
- **CA-7** **Debate output is in English.** *(DEC-05, D-07)*
- **CA-8** Determinism for tests comes from mocks; live-provider runs are inherently non-deterministic and are treated as evidence, not as test oracles. *(T-04, I-08)*

---

## 14. Risks and Mitigations

| Risk | Mitigation | Refs |
|------|-----------|------|
| **RK-1** Provider failure/slowness | Timeouts, watchdog/keep-alive, retries via Gatekeeper, graceful degradation with logged reason | E-06, E-07, I-09 |
| **RK-2** Invalid JSON from an agent | Schema validation + bounded regeneration loop; never crash | FR-08, FR-11, I-06 |
| **RK-3** Agreement collapse / off-side drift | Judge side-fidelity check + regeneration | FR-10, FR-11, R-11, R-12 |
| **RK-4** Excessive token/cost usage | Configurable turn budgets, Gatekeeper budget caps, English output, per-run cost report | DEC-04, CR-02, CR-03, CR-05 |
| **RK-5** Missing evidence | Evidence required per argument; fallback handling + logging if search fails | FR-12, DEC-02, I-09 |
| **RK-6** Judge returns a tie | Deterministic, documented tie-break rule guarantees one winner | FR-13, I-07 |
| **RK-7** Hardcoded configuration | All parameters in config files; file-size/review gates | E-10, E-11, NFR-12 |
| **RK-8** Weak documentation | README section checklist as a doc gate; prompts/decisions captured | D-01, D-02, E-15 |
| **RK-9** Failing reproducibility | `uv` + `pyproject.toml`; mock-based deterministic tests; documented run steps | E-14, T-04, NFR-01 |
| **RK-10** Secrets committed | `.gitignore`, `.env.example` only, review, no secrets in logs | C-01, C-02, C-06 |

---

## 15. Success Metrics / KPIs

- **KPI-1 — Turns completed:** target 20/20 child turns in a full run. *(PG-1, AC-01)*
- **KPI-2 — Valid-JSON rate:** 100% of accepted turns are schema-valid. *(PG-3, AC-02)*
- **KPI-3 — Evidence coverage:** **100% of accepted substantive child turns** include an evidence reference or an approved evidence reuse. *(PG-5, AC-04)*
- **KPI-4 — Rejected/regenerated turns:** count of invalid/off-role turns caught and regenerated (proves the guard works). *(PG-4, AC-09)*
- **KPI-5 — Quality-gate pass/fail:** all gates green. *(PG-9, AC-12)*
- **KPI-6 — Test pass count:** number of passing unit/integration/e2e tests. *(NFR-04, T-02..T-06)*
- **KPI-7 — Resource usage (estimates):** provider call count, approximate input/output token estimates (English chars ÷ 4), runtime, search call count, transcript size, configured turn count — **clearly labeled as estimates, not exact provider billing**. *(FR-17, NFR-08)*
- **KPI-8 — Transcript completeness:** transcript + judgment + evidence + logs all present and consistent. *(PG-7, AC-10)*

---

## 16. Traceability

| PRD section(s) | Maps to Gate 0 source |
|----------------|-----------------------|
| §2 Problem, §5 Goals, §7 Functional, §10 Protocol, §11 Acceptance | [`REQUIREMENTS_AUDIT.md`](./REQUIREMENTS_AUDIT.md) §1–§2 (R-, I-), §10 acceptance checklist |
| §5/§6/§7 provider, search, topic, budget, language decisions | [`REQUIREMENTS_AUDIT.md`](./REQUIREMENTS_AUDIT.md) §11 Recorded Decisions (DEC-01..DEC-05) |
| §8 Non-functional, §13 Constraints | [`REQUIREMENTS_AUDIT.md`](./REQUIREMENTS_AUDIT.md) §3 (E-), §5 (T-), §6 (C-), §7 (CR-) |
| §12 Artifacts, §16 docs expectations | [`REQUIREMENTS_AUDIT.md`](./REQUIREMENTS_AUDIT.md) §4 (D-) |
| §14 Risks | [`REQUIREMENTS_AUDIT.md`](./REQUIREMENTS_AUDIT.md) §8 Grading Risks (G-) |
| Project framing & "must not" guarantees | [`PROJECT_RULES.md`](./PROJECT_RULES.md) RULE 1–17 |
| §3 background, §6 non-goals (anti-A1-weakness rationale) | [`LESSONS_FROM_ASSIGNMENT1.md`](./LESSONS_FROM_ASSIGNMENT1.md) W-1..W-7 |
| Phase sequencing & gating of this PRD | [`TODO.md`](./TODO.md) Phase 1 + Review Rule |

---

## 17. Open Questions

> Only genuinely unresolved items. Gate 0 decisions (DEC-01..DEC-05) are **not** reopened here.

### Still open
- **OQ-1 — Evidence relevance strictness.** Minimum is now fixed (≥1 reference per accepted substantive turn, new or reused — FR-12); what remains open is *how strictly* the Judge checks that an evidence item is relevant/on-point. *To be settled in PLAN/ARCHITECTURE.*
- **OQ-4 — `ddgs` viability.** Whether the no-key DuckDuckGo/`ddgs` adapter is reliable enough in practice, or whether a different no-key source is needed (the abstraction stays either way). *(DEC-02 — validated in Phase 6.)*
- **OQ-6 — Word-limit vs turn-limit.** Whether to also enforce a per-turn word/length bound in addition to the turn-count bound. *(R-07 allows either; turn-count is chosen, word cap is optional — PLAN.)*

### Resolved in this PRD
- **OQ-2 — Tie-break specifics — RESOLVED.** Deterministic tie-break order fixed in **FR-13 / DP-6**: evidence quality → rebuttal/responsiveness → fewer protocol violations/regenerations → forced final persuasive choice. Tie remains forbidden.
- **OQ-3 — Regeneration retry cap — RESOLVED.** Fixed in **FR-11**: max **2** regeneration attempts per turn; on exhaustion the run is marked a **failed protocol run**; the final submission run must complete without exhausted retries; verified by mock-driven tests.
- **OQ-5 — Cost estimation under CLI provider — RESOLVED.** Fixed in **FR-17 / KPI-7**: record proxy metrics (call count, token estimates via chars ÷ 4, runtime, search calls, transcript size, configured turns), clearly labeled as **estimates, not exact billing**.
