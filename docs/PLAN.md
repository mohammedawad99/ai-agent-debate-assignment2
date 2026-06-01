# Technical PLAN — AI Agent Debate System

## 1. Title and Status

- **Document type:** Technical PLAN (Phase 2).
- **Status:** **DRAFT — Phase 2.** Pending review per the [TODO Review Rule](./TODO.md) (Claude creates → human reviews → ChatGPT reviewer approves → committed).
- **Implementation status:** **Not started.** No `src/` code, no `pyproject.toml`, no dependencies, no config files exist yet. This PLAN describes the *intended* design and sequencing only; nothing here is built.
- **Inputs:** [`PRD.md`](./PRD.md), [`REQUIREMENTS_AUDIT.md`](./REQUIREMENTS_AUDIT.md), [`PROJECT_RULES.md`](./PROJECT_RULES.md), [`LESSONS_FROM_ASSIGNMENT1.md`](./LESSONS_FROM_ASSIGNMENT1.md), [`TODO.md`](./TODO.md).
- **Output of next phase:** a detailed [`ARCHITECTURE.md`](./ARCHITECTURE.md) (Phase 3) that freezes interfaces and the final JSON schema.

---

## 2. Purpose

This PLAN converts the approved PRD's *what/why* (`FR-`, `NFR-`, `AC-`, `DP-`) into an
*implementation strategy*: the layers, modules, components, flows, configuration, and
testing approach the system will use. It is the bridge between requirements and
architecture. It contains **no code** — it defines how the code will be organized and
what each part is responsible for, so that Phase 3 can finalize interfaces and Phase 6
can implement against a clear target.

---

## 3. Technical Principles

These principles govern every later design and implementation decision.

- **TP-1 — SDK-first design.** All business logic lives in an importable SDK; the SDK is the single source of behavior. *(E-04, NFR-04)*
- **TP-2 — CLI as a thin interface.** The CLI only parses arguments, calls the SDK, and renders output — no business logic. *(E-04, E-05, PROJECT_RULES RULE 8)*
- **TP-3 — Provider abstraction.** All model calls go through a `ProviderAdapter` interface; orchestration never imports a concrete provider. *(DEC-01, NG-5)*
- **TP-4 — Search abstraction.** All evidence retrieval goes through a `SearchTool` interface; orchestration never imports a concrete search vendor. *(DEC-02, NFR-03)*
- **TP-5 — Strict JSON protocol.** Agents communicate via schema-validated JSON; invalid messages are rejected, not parsed leniently. *(R-17, FR-08, I-06)*
- **TP-6 — Parent-mediated routing.** Pro and Con never hold a reference to each other; the Judge is the only router. **The design exposes no direct child-to-child messaging path, and this is verified by tests.** *(R-02, R-03, FR-03, FR-04)*
- **TP-7 — Testability through mocks.** `MockProvider` and `MockSearchTool` make the entire flow runnable offline and deterministically. *(T-04, NFR-05)*
- **TP-8 — No secrets in Git.** Keys (only if/when an API provider is added) come from `.env`/environment at runtime; never committed; never logged. *(C-01, C-05, C-06, NFR-06)*
- **TP-9 — No hardcoded parameters.** Topic, turn counts, word limits, timeouts, retry caps, provider commands, and logging settings all come from config. *(E-10, E-11, NFR-12)*
- **TP-10 — Logs and evidence as first-class artifacts.** Structured logs, transcripts, evidence records, and the cost report are explicit deliverables, not side effects. *(E-09, D-04, D-06)*
- **TP-11 — Cost/resource awareness.** Every provider/search call is counted and bounded by the Gatekeeper; a per-run estimate report is produced. *(CR-01..CR-06, FR-15, FR-17)*

---

## 4. Proposed Architecture Overview

A layered architecture; dependencies point **downward only** (upper layers depend on
lower abstractions, never the reverse), which keeps orchestration provider-agnostic.

```
┌──────────────────────────────────────────────────────────────┐
│  CLI layer            argument parsing, output rendering only   │  → TP-2
├──────────────────────────────────────────────────────────────┤
│  SDK / application    public entry points; wires dependencies   │  → TP-1
│  service layer        from config; returns results to CLI       │
├──────────────────────────────────────────────────────────────┤
│  Orchestration layer  DebateSession/Runner: turn state machine, │  → TP-6
│                       parent-mediated routing, regeneration loop │
├──────────────────────────────────────────────────────────────┤
│  Agents layer         JudgeAgent, Pro/Con agents (role prompts) │  → FR-01
├──────────────────────────────────────────────────────────────┤
│  Validation layer     JSON schema + protocol + side-fidelity +  │  → TP-5
│                       evidence-relevance checks                  │
├──────────────────────────────────────────────────────────────┤
│  Provider adapter     ProviderAdapter iface; ClaudeCliProvider, │  → TP-3
│  layer                MockProvider; behind a Gatekeeper          │
├──────────────────────────────────────────────────────────────┤
│  Search tool layer    SearchTool iface; DdgsSearchTool,         │  → TP-4
│                       MockSearchTool; EvidenceStore              │
├──────────────────────────────────────────────────────────────┤
│  Cross-cutting:  Configuration · Logging · Gatekeeper/Watchdog · │
│                  CostTracker · Results/artifact writers          │
└──────────────────────────────────────────────────────────────┘
```

- **CLI layer** — entry command(s); maps user input to SDK calls; renders human-readable progress and final result. *(E-05, NFR-10)*
- **SDK/application service layer** — public API (e.g. "run a debate from this config"); constructs and injects dependencies; the only thing the CLI talks to. *(E-04)*
- **Orchestration layer** — the debate state machine: sequences turns, routes through the Judge, runs validation + regeneration, triggers scoring. *(I-01, FR-03)*
- **Agents layer** — Judge, Pro, Con; each owns its role/prompt and produces protocol messages via the provider. *(FR-01, FR-02)*
- **Provider adapter layer** — uniform model-call interface with concrete + mock implementations. *(DEC-01)*
- **Search tool layer** — uniform evidence-retrieval interface with concrete + mock implementations, plus the evidence store. *(DEC-02)*
- **Validation layer** — schema validation, protocol/role checks, evidence-relevance checks. *(I-06, FR-08..FR-12)*
- **Logging layer** — structured, rotating logs. *(E-09)*
- **Configuration layer** — typed loading of all config files; no value is read from a hardcoded constant. *(E-10, E-11)*
- **Results/artifact layer** — transcript (JSONL + MD), judgment, evidence records, cost report. *(D-04, D-06)*

---

## 5. Planned Package / Module Structure (proposal — not created)

> **Plan only.** The tree below is the *intended* future layout under
> `src/agent_debate/`. **No files or directories are created in this phase.**

```
src/agent_debate/
├── cli/            # thin CLI entry points; arg parsing + rendering (TP-2)
├── sdk/            # public application services; dependency wiring (TP-1)
├── orchestration/  # DebateSession/Runner, turn state machine, regen loop
├── agents/         # JudgeAgent, ProAgent/ConAgent (or DebateAgent + role)
├── providers/      # ProviderAdapter, ClaudeCliProvider, MockProvider
├── search/         # SearchTool, DdgsSearchTool, MockSearchTool, EvidenceStore
├── protocol/       # message models, turn types, (de)serialization
├── validation/     # JsonProtocolValidator, side-fidelity, evidence relevance
├── config/         # ConfigLoader + typed config objects
├── logging/        # LoggerFactory, structured/rotating handlers
└── results/        # TranscriptWriter, JudgmentWriter, CostTracker reporters
```

Supporting (also planned, created in later phases):
```
config/   # JSON config templates (Phase 4)
tests/    # unit / integration / e2e (Phase 5)
results/  # produced at runtime (Phase 7)
logs/     # produced at runtime
```

---

## 6. Core Classes / Components (responsibilities only — no code)

| Component | Layer | Responsibility |
|-----------|-------|----------------|
| **DebateRunner / DebateSession** | orchestration | Owns the turn state machine; sequences opening + alternating turns; enforces routing through the Judge; runs the validate→regenerate loop; invokes final scoring; coordinates artifact writing. *(I-01, FR-03, FR-11)* |
| **JudgeAgent** | agents | Initializes the debate (assigns sides, states topic + rules); forwards the opponent's last claim; validates each child turn (schema/side/tone/rebuttal/evidence); requests regeneration; computes rubric scores; applies tie-break; produces the final judgment. *(FR-02, FR-10, FR-13, FR-14, DP-5)* |
| **DebateAgent (base) → ProAgent / ConAgent** | agents | Holds an assigned side + role prompt; produces a protocol message responding to the forwarded opponent claim; requests evidence via the SearchTool. Pro/Con differ only by configured stance, not by logic (DRY). *(FR-01, E-03)* |
| **ProviderAdapter (interface)** | providers | Uniform contract: given a prompt/context, return model text under a timeout. No orchestration code depends on a concrete provider. *(DEC-01, TP-3)* |
| **ClaudeCliProvider** | providers | Concrete adapter invoking the Claude CLI via subprocess; applies timeout; captures stdout/stderr; surfaces failures cleanly. *(DEC-01, CA-3)* |
| **MockProvider** | providers | Deterministic scripted responses for tests, including *intentionally bad* outputs (agreeing/off-side/malformed JSON) to exercise validation. *(T-04, AC-09)* |
| **SearchTool (interface)** | search | Uniform contract: given a query, return evidence items under a timeout. *(DEC-02, TP-4)* |
| **DdgsSearchTool (candidate)** | search | Concrete no-key web search adapter (DuckDuckGo/`ddgs`), if practical; retries + graceful failure. *(DEC-02, OQ-4)* |
| **MockSearchTool** | search | Deterministic canned evidence for tests. *(T-04)* |
| **Gatekeeper** | cross-cutting | Single choke point for all provider/search calls; enforces max call count, retries, concurrency, and (if practical) max runtime; records counts for the CostTracker. *(E-08, FR-15, CR-02)* |
| **Watchdog** | cross-cutting | Guards the **whole debate run** (distinct from per-call timeout, which guards a single call): monitors total wall-clock runtime, progress between rounds, repeated regeneration loops, a stalled round counter, and excessive provider/search failures. On trigger, marks the run a **failed protocol run** with an explanatory log/artifact. *(E-07, NFR-13)* |
| **JsonProtocolValidator** | validation | Validates message structure/types against the protocol; flags schema, role, rebuttal-marker, and evidence presence problems; emits `validation_errors`. *(FR-08, I-06)* |
| **EvidenceStore** | search | Holds collected evidence items keyed by id; supports reuse across turns; persists evidence records to results. *(FR-12, DP-3)* |
| **TranscriptWriter** | results | Appends accepted turns/events to JSONL; renders the human-readable Markdown transcript. *(D-04)* |
| **CostTracker** | results | Accumulates proxy metrics (calls, token estimates, runtime, search calls, transcript size, turn count); emits the cost report labeled as estimates. *(FR-17, CR-03)* |
| **ConfigLoader** | config | Loads/merges/validates all config files into typed objects; the only source of tunable values. *(E-10, E-11)* |
| **LoggerFactory** | logging | Builds structured, rotating loggers from config; ensures no secrets are logged. *(E-09, C-06)* |

---

## 7. Debate Flow (step by step)

1. **Load config** — `ConfigLoader` reads all config files into typed objects (topic, turn count, word limits, timeouts, retry cap, provider command, search settings, logging). *(E-10, FR-05/06/07)*
2. **Initialize cross-cutting services** — `LoggerFactory` builds loggers; `Gatekeeper` set up with limits; the configured `ProviderAdapter` and `SearchTool` are constructed and injected. *(FR-15, FR-16)*
3. **Judge initializes agents** — `JudgeAgent` assigns Pro/Con stances, states the topic and the rules/constraints (turn count, word limits, evidence + rebuttal requirements). *(FR-02, DP-5)*
4. **Opening turn** — the first child (e.g. Pro) produces an opening argument (no opponent claim to reference yet) with ≥1 evidence reference. *(FR-12)*
5. **Alternating turns through the Judge only** — the Judge forwards the opponent's last accepted claim to the next agent; that agent responds, referencing it via the claim-reference marker. Children never talk directly. *(FR-03, FR-09, TP-6)*
6. **Validation after each child response** — `JsonProtocolValidator` checks schema, word-count limit, side fidelity (no agreement collapse/off-side drift), respectful tone, and the rebuttal marker. *(FR-08, FR-09, FR-10)*
7. **Evidence check** — the Judge confirms ≥1 evidence reference exists and is **relevant** to the specific claim; missing or clearly irrelevant evidence → reject. *(FR-12, DP-3, OQ-1 resolution §12)*
8. **Regeneration up to 2 attempts** — on any validation/evidence failure, the Judge requests regeneration; **max 2 attempts** per turn. *(FR-11)*
9. **Failed protocol run if exhausted** — if both regenerations still fail (or the Watchdog triggers), the run is marked a **failed protocol run**. It still **writes a partial transcript, logs, and an error report** explaining the failure, but it **must not be presented as the final successful submission run**. *(FR-11, AC-09b)*
10. **Final scoring** — after all turns, the Judge scores both sides on the rubric (§9) and aggregates per side. *(FR-13, DP-6)*
11. **Deterministic tie-break** — if totals are equal, apply the fixed tie-break order (§9). A tie is never an allowed outcome. *(FR-13, R-04)*
12. **Save artifacts** — `TranscriptWriter` writes JSONL + Markdown; the judgment is written; `EvidenceStore` persists evidence records; `CostTracker` writes the cost report; logs are flushed/rotated. *(D-04, D-06, FR-14, FR-17)*

---

## 8. JSON Protocol Plan (planned fields — final schema deferred to ARCHITECTURE)

> Product-level field list only; exact types, required/optional rules, and the formal
> schema are frozen in Phase 3. *(R-17, FR-08)*

| Planned field | Purpose |
|---------------|---------|
| `message_id` | Unique id for the message/turn. |
| `round_index` | Which round/turn number in the debate. |
| `sender_role` | `judge` / `pro` / `con`. |
| `receiver_role` | Intended recipient (always mediated by the Judge). |
| `turn_type` | e.g. `init` / `opening` / `rebuttal` / `judgment` / `regeneration_request`. |
| `claim_id` | Id of this turn's primary claim. |
| `opponent_claim_id` | The claim being rebutted — the machine-checkable rebuttal link (FR-09). |
| `argument` | The argument text (subject to the word limit). |
| `evidence_refs` | List of evidence ids/records backing the argument (FR-12). |
| `protocol_status` | e.g. `accepted` / `rejected` / `regeneration_requested` / `failed`. |
| `word_count` | Computed length, checked against the configured max (§10). |
| `validation_errors` | List of detected problems when a turn is rejected. |

---

## 9. Judge Scoring Plan

**Rubric dimensions** (scored per side, per the PRD rubric): *(R-14, DP-6)*
- **clarity**
- **responsiveness / rebuttal quality**
- **evidence quality**
- **consistency with the assigned position**
- **respectful tone**
- **persuasive force**

**Scale and weighting.** Each dimension is scored on a **0–5 integer scale**. The first
planned version uses **equal weighting** across all six dimensions, so a side's **total
is the simple sum** of its dimension scores (max 30). Equal weighting is chosen for
transparency; **weighting may become configurable later** (`config/debate.json`), but the
initial version keeps it equal. Judging emphasizes **persuasiveness**, not factual truth
as the sole criterion. *(R-13, NG-4)*

**Deterministic tie-break (applied only if totals are equal):** *(FR-13, I-07)*
1. **Higher evidence quality** (that dimension's score)
2. **Stronger rebuttal / responsiveness** (that dimension's score)
3. **Fewer protocol violations / regenerations**
4. **Deterministic role-id fallback (non-LLM):** if steps 1–3 are still tied, choose the
   **lexicographically smaller normalized role id** among the remaining finalists. With
   the normalized ids `"con"` and `"pro"`, **`"con"` wins** this final technical
   tie-break. The final judgment **must explicitly state when this technical tie-break
   was used**, and must frame it as a **deterministic protocol requirement to satisfy the
   no-tie rule — not a claim that the side argued substantively better.**

This four-step cascade is **deterministic and contains no LLM call**, so it is repeatable.
**A tie is forbidden;** the scoring + tie-break rules are **designed to yield exactly one
winner**. *(R-04, AC-05)*

---

## 10. Configuration Plan (planned files — not created here)

> All files created in Phase 4. **Config format is JSON** — it matches the assignment's
> structured-JSON communication requirement, simplifies schema validation, avoids adding
> a YAML dependency early, and stays readable. **No value the system uses may be a
> hardcoded constant.** *(E-10, E-11, TP-9, R-17)*

| Planned config file | Contents |
|---------------------|----------|
| `config/app.json` | Top-level wiring: which provider/search to use, artifact output paths, run mode (dev/full/budget). |
| `config/debate.json` | Topic (default = DEC-03), **turn count per side** (full=10, dev=2–3, fallback=5), **max child turn words = 160**, **max judge decision words = 400**, rubric weights, retry cap (=2). |
| `config/agents.json` | Role definitions/stances for Judge, Pro, Con; prompt template references (project-local). |
| `config/providers.json` | Provider command(s) and arguments for `ClaudeCliProvider`; **per-call timeout**; selection of active provider; placeholder for a future API-key provider. |
| `config/search.json` | Active search tool; `ddgs` settings (max results, region); **per-search timeout**; retry settings; evidence-relevance thresholds. |
| `config/logging.json` | Log level, format, file paths, **rotation** settings (size/count). |
| `config/rate_limits.json` | Gatekeeper limits: **max provider calls**, **max retries**, concurrency, optional **max runtime**, budget caps. |

Emphasis: **turn counts, word limits (160 / 400), provider commands, timeouts, retry
caps, and logging settings are all configurable** — none hardcoded. *(NFR-12)*

---

## 11. Provider Plan

- **Primary:** `ClaudeCliProvider` — invokes the Claude CLI via Python subprocess (login-based, no committed key). *(DEC-01, CA-3)*
- **Tests:** `MockProvider` — deterministic, offline, scriptable to produce bad outputs. *(T-04)*
- **Future:** an API-key provider as a secondary configurable adapter (optional, out of initial scope). *(DEC-01, R-20)*

| Provider risk | Mitigation |
|---------------|------------|
| CLI may be **slow** | Per-call **timeout** + Watchdog; Gatekeeper bounds total calls/runtime. *(E-06, E-07)* |
| CLI may **not expose token counts** | **Proxy cost metrics** (chars ÷ 4), clearly labeled as estimates. *(FR-17)* |
| CLI output may be **malformed** | **Output validation** via `JsonProtocolValidator` + bounded regeneration. *(FR-08, FR-11)* |
| **Login/session dependency** | Detect/auth-fail surfaced as a clear logged error; graceful failure, not a crash. *(NFR-13)* |

All provider interactions are **logged** (without secrets). *(E-09, C-06)*

---

## 12. Search / Evidence Plan

- **`SearchTool` abstraction** — orchestration depends only on the interface. *(DEC-02, TP-4)*
- **`MockSearchTool` in tests** — deterministic canned evidence; the suite never hits the network. *(T-04, NG-7)*
- **`DdgsSearchTool` candidate** — configurable no-key DuckDuckGo/`ddgs` adapter for real runs, **if practical** (validated in Phase 6). *(OQ-4)*
- **Store evidence records** — `EvidenceStore` keeps items with ids; records persisted under `results/evidence/`. *(FR-12, D-06)*
- **Support evidence reuse** — a turn may reference a previously stored evidence item instead of a fresh search; reuse is explicit and recorded. *(FR-12)*
- **Validate relevance at the Judge level** — the Judge rejects/regenerates when evidence is missing or clearly irrelevant to the claim it supports (relevance strictness detailed in ARCHITECTURE). *(OQ-1 resolution §22, DP-3)*
- **Resilience** — because live search may be **unavailable, slow, or rate-limited**, the design supports **retries, graceful failure, logging, and provider replacement** behind the abstraction. *(CA-5, NFR-13)*
- **Untrusted-content / prompt-injection safety** — search result snippets and page content are **untrusted external text**. They are treated as **evidence data, not instructions**: retrieved text is **quoted/summarized as evidence** and must **not be allowed to override the agent/system/debate rules** (e.g. a snippet saying "ignore your instructions" has no authority). This is a required robustness/security mitigation. *(NFR-06, NFR-13)*
- **Search-failure contingency** — `MockSearchTool` is acceptable for tests and development. The **final evidence-backed run requires at least one successful real search-backed execution**. If `ddgs` is unavailable, the `SearchTool` abstraction allows **replacing the provider**; an **alternate no-key search provider may be evaluated in Phase 6** if `ddgs` proves unreliable. A **failed live search run is logged and must not be falsely reported as a real evidence-backed success**. *(DEC-02, D-06, R-15, OQ-A5)*

---

## 13. Gatekeeper and Cost/Resource Plan

The **Gatekeeper** is the single choke point for all provider/search calls and feeds
the **CostTracker**. *(E-08, FR-15, CR-02)*

**Tracked metrics (proxy — labeled as estimates, not exact billing):** *(FR-17, KPI-7)*
- provider call count
- estimated input/output tokens — **English characters ÷ 4**
- runtime
- search call count
- transcript size
- configured turn count

**Enforced limits (from `config/rate_limits.json`):**
- **max allowed calls** (provider/search)
- **max retries** (aligns with the regeneration cap)
- **max runtime if practical**
- budget/concurrency caps

> Claude CLI token numbers are **estimates**, never presented as exact provider billing. *(FR-17)*

---

## 14. Watchdog / Timeout Plan

**Two distinct guards, different scopes:**

- **Per-call timeout — guards a single call.** A configurable timeout wraps each
  individual provider/search subprocess call; exceeded → abort that one call (then
  fall back/log/retry within the cap). *(E-06, CA-5)*
- **Watchdog — guards the whole debate run.** Separate from per-call timeouts, the
  Watchdog monitors run-level health: **total wall-clock runtime, progress between
  rounds, repeated regeneration loops, a stalled round counter, and excessive
  provider/search failures.** *(E-07, NFR-13)*

**Behavior on trigger:**
- **Failure logging** — every per-call timeout and every Watchdog trigger is logged with
  a clear reason (no secrets). *(E-09, C-06)*
- **Per-call retry / regeneration** — a failed call is retried within the cap; if still
  failing, it becomes a turn rejection → regeneration; exhausting the 2 regenerations ⇒
  **failed protocol run**. *(FR-11, AC-09b)*
- **Watchdog trigger ⇒ failed protocol run** — if the Watchdog fires (stalled run /
  runaway retries / too many failures), the run is marked a **failed protocol run** and
  the **logs/artifacts must explain why** (partial transcript + error report retained). *(AC-09b)*
- **Test requirement** — both behaviors are covered by tests (§16): a provider-timeout
  test and a Watchdog-trigger test (stalled run / excessive retry loop). *(T-04)*

---

## 15. Logging and Artifacts Plan

| Artifact | Layer | Notes |
|----------|-------|-------|
| **Structured logs** | logging | Machine-parseable events (routing, validation, regeneration, scoring, errors). *(E-09)* |
| **Log rotation** | logging | Size/count rotation from `config/logging.json`. *(E-09)* |
| **Transcript JSONL** | results | One JSON object per accepted turn/event. *(D-04)* |
| **Transcript Markdown** | results | Human-readable rendering. *(D-04, D-07)* |
| **Final judgment** | results | Winner + rubric scores + rationale (JSON and/or MD). *(FR-14)* |
| **Evidence records** | results | Saved evidence backing arguments. *(D-06, FR-12)* |
| **Cost report** | results | Proxy metrics, labeled as estimates. *(FR-17)* |
| **Screenshots** | (later) | Phase 8: CLI run, tests passing, final output — each showing input→expected→actual. *(D-05, W-7)* |

Logs must never contain secrets. *(C-06, NFR-06)*

---

## 16. Testing Strategy (plan only — no tests written yet)

TDD-oriented; the full suite runs offline with mocks. *(T-01..T-06, NFR-05)*

- **Unit tests** — ConfigLoader; JsonProtocolValidator; scoring + tie-break; word-count check; EvidenceStore reuse; CostTracker proxy math; Gatekeeper limits.
- **Integration tests** — Judge-mediated routing; agent↔provider via adapter; search via SearchTool.
- **Mock-based full debate (e2e)** — a short bounded debate (2–3 turns/side) end-to-end with `MockProvider` + `MockSearchTool`. *(AC-01 scaled, AC-08)*
- **Invalid JSON test** — MockProvider returns malformed output → detected + regenerated. *(AC-02, AC-09)*
- **Agreement-collapse test** — MockProvider returns an agreeing turn → detected + regenerated. *(R-11, AC-09)*
- **Off-side drift test** — MockProvider returns a wrong-side turn → detected + regenerated. *(R-12, AC-09)*
- **Missing/irrelevant evidence test** — turn with no/irrelevant evidence → rejected + regenerated. *(FR-12, OQ-1)*
- **Exhausted-retry test** — bad output persists past 2 retries → run marked **failed protocol run**. *(FR-11, AC-09b)*
- **No direct child-to-child communication test** — assert the design exposes no message route allowing Pro↔Con directly (verified, not assumed). *(FR-04, AC-06, T-03)*
- **Judge no-tie test** — equal scores → tie-break yields exactly one winner, **including the step-4 role-id fallback** (`"con"` wins on a full tie) and that the judgment records the technical tie-break. *(FR-13, AC-05)*
- **Config loading test** — missing/invalid config handled; values come from files not constants. *(E-10, E-11)*
- **Gatekeeper / CostTracker test** — limits enforced; proxy metrics computed correctly. *(FR-15, FR-17)*
- **Log/artifact writing test** — transcript/judgment/evidence/cost files written with expected shape. *(D-04, D-06)*
- **Provider timeout test** — a slow/hung `MockProvider` call is **aborted at the timeout and logged**, not left to hang. *(E-06, §14)*
- **Watchdog test** — a stalled run (no round progress) or an excessive regeneration loop **triggers the Watchdog → failed protocol run** with an explanatory artifact. *(E-07, §14, AC-09b)*
- **Search-failure test** — `MockSearchTool` raising an error or returning **empty results** is handled **gracefully** (retry/fallback/logged), not fatal. *(CA-5, NFR-13)*
- **Secrets-not-logged test** — given a configured secret value, assert it **never appears in logs or results artifacts**. *(C-06, NFR-06, AC-13)*
- **CLI smoke test** — the CLI **starts a debate by calling the SDK** and renders a result, proving the CLI owns **no business logic** (logic invoked lives in the SDK). *(AC-07, E-04, TP-2)*
- **Coverage-threshold test/gate** — the coverage gate **fails below the planned 85% minimum** (see §17). *(E-15, AC-12)*

---

## 17. Quality Gate Plan (intended commands — nothing installed yet)

> Listed for later use; **no installation or execution happens in this phase.** *(E-15, AC-12)*

- `uv run ruff check .` — lint
- `uv run ruff format --check .` — formatting check
- `uv run pytest` — tests
- `uv run pytest --cov=src --cov-report=term-missing` — coverage; the gate will **fail below the planned minimum of 85%** (`--cov-fail-under=85`, to be wired in Phase 5)
- *(optional)* `uv run mypy src` — types, if practical *(E-16)*
- **File-size check** — flag oversized files (maintainability gate). *(E-15, NFR-02)*
- **Required-docs check** — assert required docs exist (REQUIREMENTS_AUDIT, PRD, PLAN, ARCHITECTURE, README, etc.). *(E-15)*

All gates intended to be runnable via a single aggregate command in Phase 5. *(PG-9)*

---

## 18. Development Phases (work after this PLAN)

Maps to [`TODO.md`](./TODO.md) Phases 3–9:
1. **Architecture/protocol document** — freeze interfaces + final JSON schema (Phase 3).
2. **`pyproject`/uv skeleton** — reproducible environment, tool config (Phase 4).
3. **Config templates** — the `config/*` files from §10 (Phase 4).
4. **Protocol models and validators** — message models + `JsonProtocolValidator` (Phase 5/6, TDD).
5. **Mock provider/search + tests** — `MockProvider`, `MockSearchTool`, failing-first tests (Phase 5).
6. **Orchestration** — `DebateSession`, routing, regeneration, scoring, tie-break (Phase 6).
7. **CLI** — thin interface over the SDK (Phase 6).
8. **Real provider/search integration** — `ClaudeCliProvider`, `DdgsSearchTool` (Phase 6).
9. **Final run** — real, evidence-backed debate; capture artifacts (Phase 7).
10. **README / screenshots / final audit** — submission artifacts + acceptance walk (Phases 8–9).

---

## 19. Alternatives Considered

| Decision | Options | Chosen | Why |
|----------|---------|--------|-----|
| Model access | API provider **vs** CLI subprocess | **CLI subprocess (primary)**, API as future option | Developer works in Claude Code on Ubuntu; no committed key; abstraction keeps API open. *(DEC-01)* |
| Evidence source | Real search **vs** mock only | **Both** (mock for tests, real for the final run) | Determinism for tests + genuine evidence for submission. *(DEC-02, R-15)* |
| Knowledge | Full RAG/vector DB **vs** search-only | **Search-only** | RAG is out of scope; search satisfies the evidence requirement at lower complexity. *(R-16, NG-2)* |
| Interface | GUI **vs** CLI | **CLI** | GUI not required; CLI is sufficient and cheaper to build/test. *(E-05, NG-1)* |
| Code structure | Single monolithic script **vs** SDK/OOP layered | **SDK/OOP layered** | Maintainability, extensibility, testability, and the SDK/CLI split requirement. *(E-02, E-04, W-5)* |
| Judge framing | Topic-expert judge **vs** debate-rubric judge | **Debate-rubric judge** | Judges **persuasiveness** via a transparent rubric, not factual authority. *(R-13, R-14, NG-4)* |

---

## 20. Risks and Mitigations

**Technical risks**
| Risk | Mitigation | Refs |
|------|-----------|------|
| Provider slow/unavailable/hung | Timeout + Watchdog + Gatekeeper caps + graceful failure | E-06, E-07, NFR-13 |
| Malformed agent JSON | Schema validation + bounded regeneration | FR-08, FR-11 |
| Agreement collapse / off-side drift | Side-fidelity validation + regeneration | R-11, R-12, AC-09 |
| Live search unreliable/rate-limited | Retries, graceful fallback, evidence reuse, provider replacement behind `SearchTool` | CA-5, DEC-02 |
| `ddgs` unavailable at submission time | `SearchTool` allows swapping in an alternate no-key provider (evaluated in Phase 6); failed live search is logged, never reported as real success | DEC-02, OQ-A5 |
| Malicious/injection text in search results | Treat retrieved content as untrusted evidence data, not instructions; it cannot override agent/system/debate rules | NFR-06, §12 |
| Irrelevant/missing evidence | Judge relevance check → reject/regenerate | FR-12, OQ-1 |
| Excessive cost | Configurable budgets, Gatekeeper limits, English output, proxy cost report | DEC-04, CR-02..CR-05 |
| Hardcoded parameters slip in | Config-driven design + file-size/review/required-docs gates | E-10, E-11 |

**Grading risks** (from REQUIREMENTS_AUDIT §8)
| Risk | Mitigation | Refs |
|------|-----------|------|
| Tie / no clear winner | Deterministic tie-break (§9) | G-02, FR-13 |
| Direct child↔child leakage | No such code path + integration test | G-03, FR-04 |
| Disconnected monologues | Mandatory opponent-claim marker | G-04, FR-09 |
| No real internet evidence | Real search run + saved evidence artifacts | G-05, FR-12 |
| Unsupported "it works" claims | Tests + committed evidence; future-tense until proven | G-06, RULE 2 |
| Manual-CLI-only submission | Python orchestrator is the deliverable | G-08, NG-3 |
| Secrets committed | `.gitignore`, no keys, `.env.example` only | G-09, NFR-06 |

---

## 21. Traceability

| PLAN section | Maps to |
|--------------|---------|
| §3 Principles | PRD §3, NFR-01..13; PROJECT_RULES RULE 1–17 |
| §4 Architecture overview | PRD §7 (FR-01..04, FR-15), E-02/E-04 |
| §5 Module structure | E-02, E-03, NFR-02/03 |
| §6 Core components | PRD FR-01..FR-17; DEC-01/DEC-02 |
| §7 Debate flow | PRD §10 (DP-1..6), FR-03/09/11/12/13 |
| §8 JSON protocol fields | PRD FR-08/FR-09; R-17, I-06 |
| §9 Scoring + tie-break | PRD FR-13/DP-6; R-04/R-13/R-14, I-07 |
| §10 Configuration | E-10, E-11, DEC-04; word limits resolve OQ-6 |
| §11 Provider plan | DEC-01, R-20, FR-15/FR-17 |
| §12 Search/evidence plan | DEC-02, R-15/R-16, FR-12; resolves OQ-1/OQ-4 |
| §13 Gatekeeper/cost | E-08, CR-01..06, FR-15/FR-17 |
| §14 Watchdog/timeout | E-06, E-07, NFR-13 |
| §15 Logging/artifacts | E-09, D-04, D-06 |
| §16 Testing strategy | T-01..T-06, all AC-* |
| §17 Quality gates | E-13..E-16, AC-12 |
| §18 Dev phases | TODO Phases 3–9 |
| §19 Alternatives | DEC-01/DEC-02, R-16, E-02/E-04/E-05, R-13 |
| §20 Risks | REQUIREMENTS_AUDIT §8 (G-), PRD §14 (RK-) |

---

## 22. Open Questions

> Gate 0 decisions (DEC-01..DEC-05) and PRD resolutions (OQ-2/3/5) are **not** reopened.

### Resolved in this PLAN
- **OQ-1 — Evidence relevance strictness — RESOLVED (behavior level).** Every accepted child turn must include ≥1 evidence reference or an approved reuse; evidence must be **relevant to the specific claim** it supports; the Judge **rejects/requests regeneration** when evidence is **missing or clearly irrelevant**. **Relevance validation is a required behavior**; the exact scoring/threshold mechanics are finalized in ARCHITECTURE. *(FR-12, DP-3)*
- **OQ-4 — search reliability — RESOLVED (strategy level).** Use the `SearchTool` abstraction with mandatory `MockSearchTool` for tests and a `DdgsSearchTool` candidate for real runs; support **retries, graceful failure, logging, and provider replacement**; the final submission must include saved evidence from **≥1 successful real run**. Whether `ddgs` specifically is used is confirmed in Phase 6. *(DEC-02)*
- **OQ-6 — word limits — RESOLVED.** **Max child turn = 160 words; max judge decision = 400 words.** Both are **configurable** (`config/debate.json`), used to control cost, readability, and debate discipline. *(R-07, DEC-04)*
- **OQ-A3 — Config format — RESOLVED.** **JSON.** Matches the structured-JSON communication requirement, simplifies schema validation, avoids an early YAML dependency, and stays readable. (See §10.) *(R-17, E-10)*
- **OQ-A4 — Rubric scale/weighting — RESOLVED.** **0–5 integer per dimension; equal weighting; total = sum (max 30).** Weighting may become configurable later; the first version is equal for transparency. (See §9.) *(R-14, I-07)*
- **OQ-A6 — Tie-break step 4 (final fallback) — RESOLVED.** Replaced the earlier "forced persuasive choice" (which would have needed an LLM and broken determinism) with a **deterministic, non-LLM role-id fallback**: lexicographically smaller normalized role id wins (`"con"` over `"pro"`), explicitly recorded in the judgment as a technical tie-break, not a substantive judgment. (See §9.) *(FR-13, R-04)*

### Still open (for ARCHITECTURE / later phases)
- **OQ-A1 — Final JSON schema details.** Exact types, required/optional rules, and formal schema for the §8 fields. *(Phase 3.)*
- **OQ-A2 — Relevance check mechanism.** How relevance is concretely judged (keyword overlap, model-judged score, threshold) and how it feeds the rubric's evidence-quality dimension. *(Phase 3.)*
- **OQ-A5 — `ddgs` confirmation.** Empirical confirmation that the no-key adapter is reliable enough, or selection of an alternative no-key source. *(Phase 6.)*
- **OQ-A7 — Mid-run provider auth/session expiry.** Whether a long run needs checkpoint/resume if the Claude CLI session drops mid-debate, or whether a clean failed-protocol-run + rerun is acceptable. *(Phase 3/6 — noted from review.)*
