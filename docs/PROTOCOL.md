# Protocol — AI Agent Debate System

## 1. Title and Status

- **Document type:** JSON message protocol (Phase 3).
- **Status:** **DRAFT — Phase 3.** Pending review per the [TODO Review Rule](./TODO.md).
- **Scope:** **Documentation-level schema only — no Python code, no models.** This resolves **OQ-A1** (final JSON schema details) at the design level. Concrete models (e.g. dataclasses/Pydantic) are built in Phase 6.
- **Companions:** [`ARCHITECTURE.md`](./ARCHITECTURE.md), [`SCORING_AND_VALIDATION.md`](./SCORING_AND_VALIDATION.md).
- **Convention:** field types are described as `string`, `integer`, `array<...>`, `object`, `boolean`, `string|null`. "Required" means the field must be present for that message kind; "optional" may be absent or null.

---

## 2. Protocol Goals

- **PG-1 — JSON-first.** Every inter-agent message is a JSON object. *(R-17)*
- **PG-2 — Machine-checkable.** Roles, turn types, statuses, and references are explicit fields, not inferred from prose. *(I-06)*
- **PG-3 — Parent-mediated.** Routing fields make Judge-mediation explicit and enforceable. *(R-02, FR-03)*
- **PG-4 — Evidence-backed.** Child arguments carry `evidence_refs`; evidence has its own record schema. *(R-15, FR-12)*
- **PG-5 — No direct Pro↔Con communication.** Routing rules forbid child-to-child messages. *(R-03, FR-04)*
- **PG-6 — Reproducible transcript.** Accepted messages and relevant rejected/regenerated events are persisted as JSONL. *(D-04)*

---

## 3. Enumerations

### 3.1 Roles
`judge` · `pro` · `con` · `system`
- `system` — used only for setup/meta messages (e.g. initial rules envelope); not a debater.

### 3.2 Sender / receiver constraints
- `pro` and `con` may set `receiver_role` only to `judge`.
- `judge` may set `receiver_role` to `pro`, `con`, or `system` (and emits the `final_judgment`).
- `system` may address `judge` (setup) only.
- A message with `sender_role` ∈ {`pro`,`con`} and `receiver_role` ∈ {`pro`,`con`} is **illegal** (see §9).

### 3.3 `turn_type`
`judge_instruction` · `opening_argument` · `rebuttal` · `regeneration_request` · `final_judgment` · `protocol_error`

### 3.4 `protocol_status`
`generated` · `accepted` · `rejected` · `regenerated` · `failed`
- `generated` — produced, not yet validated.
- `accepted` — passed all validation; enters the canonical transcript.
- `rejected` — failed validation; retained as a rejected event.
- `regenerated` — a replacement was produced after a rejection (links to the attempt count).
- `failed` — terminal failure for this message/run.

### 3.5 `failure_reason`
`invalid_json` · `missing_required_field` · `wrong_role` · `direct_child_to_child` ·
`missing_opponent_reference` · `missing_evidence` · `irrelevant_evidence` ·
`agreement_collapse` · `off_side_drift` · `word_limit_exceeded` · `provider_timeout` ·
`search_failure` · `auth_failure` · `watchdog_trigger` · `retry_exhausted`

---

## 4. DebateMessage Schema

The core message exchanged in the debate.

**Always required**
| Field | Type | Notes |
|-------|------|-------|
| `message_id` | string | Unique per message. |
| `session_id` | string | Identifies the debate run. |
| `round_index` | integer | Round number (0-based or 1-based; fixed at implementation). |
| `turn_index` | integer | Global ordering index across the run. |
| `sender_role` | string (role enum) | §3.1. |
| `receiver_role` | string (role enum) | Subject to §3.2 constraints. |
| `turn_type` | string (turn_type enum) | §3.3. |
| `protocol_status` | string (status enum) | §3.4. |
| `content` | string | The **full natural-language message** as returned/rendered by the agent (the complete turn text). |
| `word_count` | integer | Computed; checked against the configured limit (§10). |
| `created_at` | string (ISO-8601 timestamp) | Creation time. |

**Required for child turns** (`sender_role` ∈ {`pro`,`con`}, `turn_type` ∈ {`opening_argument`,`rebuttal`})
| Field | Type | Notes |
|-------|------|-------|
| `claim_id` | string | Id of this turn's primary claim. |
| `argument` | string | The **specific scored argumentative claim text** for this child turn (subject to the 160-word limit). It **may be derived from `content`**, but it **must be present explicitly** so validators and the scorer operate on a precise, unambiguous claim rather than re-parsing free text. |
| `evidence_refs` | array<string> | ≥1 evidence id (newly retrieved or reused). *(FR-12)* |

**Required after the opening** (`turn_type` = `rebuttal`)
| Field | Type | Notes |
|-------|------|-------|
| `opponent_claim_id` | string | The opponent claim being rebutted — the machine-checkable rebuttal link. *(FR-09)* |

**Optional**
| Field | Type | Notes |
|-------|------|-------|
| `validation_errors` | array<object>\|null | Present when rejected (see ValidationResult.errors). |
| `regeneration_attempt` | integer\|null | 0,1,2 — which attempt this message represents. |
| `notes` | string\|null | Free-text annotation (never secrets). |

> The **opening argument does not require `opponent_claim_id`** (no prior claim exists).
> Every **rebuttal requires it**.
>
> **`content` vs `argument`:** `content` is the full natural-language turn as the agent
> produced it; `argument` is the precise argumentative claim that validation and scoring
> act on. For child turns both are present — `argument` may be a faithful extract of
> `content`, but it is stored explicitly so the system never has to re-parse free text to
> find the scored claim.

---

## 5. EvidenceRecord Schema

One record per evidence item, stored in the `EvidenceStore` and persisted to results.

**Required**
| Field | Type | Notes |
|-------|------|-------|
| `evidence_id` | string | Unique id; referenced by `evidence_refs`. |
| `session_id` | string | The debate session this evidence belongs to — makes evidence artifacts self-identifying across runs (`session_id` links evidence to the session; `supports_claim_id` links it to the claim). |
| `source_type` | string | e.g. `web`, `reuse`, `mock`. |
| `title` | string | Source title. |
| `url` | string | Source URL (or a clearly-marked synthetic id for mock/reuse). |
| `snippet` | string | Quoted/summarized untrusted text — treated as **data, not instructions** (SR-4). |
| `retrieved_at` | string (timestamp) | When retrieved (or first retrieved, for reuse). |
| `query` | string | The search query that produced it. |
| `supports_claim_id` | string | The claim this evidence is attached to. |
| `relevance_status` | string | `unchecked` · `relevant` · `irrelevant` (set by validation; see SCORING_AND_VALIDATION.md). |

**Optional**
| Field | Type | Notes |
|-------|------|-------|
| `provider_name` | string\|null | e.g. `ddgs`, `mock`. |
| `rank` | integer\|null | Result rank from the search tool. |
| `cached` | boolean\|null | True if served from a prior retrieval (reuse). |
| `notes` | string\|null | Annotation. |

---

## 6. ValidationResult Schema

Produced by the validators for each child turn.

| Field | Type | Notes |
|-------|------|-------|
| `message_id` | string | The validated message. |
| `is_valid` | boolean | True only if no blocking errors. |
| `errors` | array<object> | Each: `{ failure_reason, detail }` using the §3.5 enum. |
| `warnings` | array<object> | Non-blocking issues. |
| `required_action` | string | `accept` · `regenerate` · `fail_run`. |
| `regeneration_prompt_summary` | string\|null | Short, secret-free summary of what to fix, sent in the `regeneration_request`. |

---

## 7. JudgeScore Schema

Per-side rubric scores. Each dimension is a **0–5 integer**.

| Field | Type | Notes |
|-------|------|-------|
| `clarity` | integer 0–5 | |
| `responsiveness` | integer 0–5 | rebuttal quality / responsiveness |
| `evidence_quality` | integer 0–5 | |
| `position_consistency` | integer 0–5 | consistency with assigned side |
| `respectful_tone` | integer 0–5 | |
| `persuasive_force` | integer 0–5 | |
| `total` | integer 0–30 | **sum of the six dimensions** (equal weight) |
| `protocol_violations` | integer | count of violations attributed to the side |
| `regeneration_count` | integer | regenerations triggered by the side |

`protocol_violations` and `regeneration_count` feed tie-break step 3 (§ SCORING_AND_VALIDATION.md).

---

## 8. FinalJudgment Schema

| Field | Type | Notes |
|-------|------|-------|
| `session_id` | string | The run. |
| `winner_role` | string (`pro`\|`con`) | Exactly one winner. *(R-04)* |
| `loser_role` | string (`pro`\|`con`) | The other side. |
| `scores` | object | `{ pro: JudgeScore, con: JudgeScore }`. |
| `tie_break_used` | boolean | True if any tie-break step beyond raw totals was needed. |
| `tie_break_reason` | string\|null | Which step decided it (e.g. `evidence_quality`, `responsiveness`, `fewer_violations`, `configured_priority`). |
| `reasoning` | string | Rubric-based rationale (≤ **400 words**). *(DEC: judge decision limit)* |
| `limitations` | string | Honest limitations (e.g. "configured technical tie-break used; not a claim of substantive superiority"). |
| `created_at` | string (timestamp) | |

> When `tie_break_reason` = `configured_priority`, `limitations` **must** state that the
> outcome was decided by the **configured technical tie-break priority list**
> (`final_tie_break_priority`, default `["con", "pro"]`) — an **arbitrary deterministic
> protocol mechanism to satisfy the no-tie rule, NOT** a judgment that the side argued
> substantively better. *(FR-13)*

---

## 9. Routing Rules

- **RR-1** `pro`/`con` can only send to `judge`. *(R-02)*
- **RR-2** `judge` can send to `pro`/`con` (instructions, forwarded claims, regeneration requests).
- **RR-3** `judge` can emit the `final_judgment`.
- **RR-4** `pro`/`con` **cannot** send direct messages to each other. *(R-03)*
- **RR-5** Any message with a child sender **and** a child receiver is a **protocol failure**: it is rejected with `failure_reason = direct_child_to_child` (and, since the design exposes no such route, this also serves as a defensive assertion verified by tests). *(FR-04, AC-06)*

---

## 10. Turn Rules

- **TR-1** The **opening turn does not need `opponent_claim_id`**. *(FR-09)*
- **TR-2** Every **rebuttal must include `opponent_claim_id`** referencing a prior accepted opponent claim. *(FR-09)*
- **TR-3** Every **accepted child turn must include ≥1 `evidence_refs`** (new or reused). *(FR-12)*
- **TR-4** The **word limit is enforced**: child turn ≤ **160 words**, final judgment ≤ **400 words** (configurable). Exceeding → `word_limit_exceeded`. *(DEC)*
- **TR-5** **Role consistency is enforced**: a child must argue its assigned side; agreement collapse / off-side drift are rejected. *(R-11/12)*
- **TR-6** The **final judgment must name exactly one winner** — **no tie**. *(R-04)*

---

## 11. Regeneration Protocol

- **RP-1** Up to **2 regeneration attempts** per turn. *(FR-11)*
- **RP-2** On a rejection, the Judge sends a `regeneration_request` (carrying a secret-free `regeneration_prompt_summary` of what to fix).
- **RP-3** The invalid response is **retained in the transcript** with `protocol_status = rejected` (or logged as a rejected artifact), so the audit trail is complete.
- **RP-4** **Exhausted retries ⇒ failed protocol run** (`failure_reason = retry_exhausted`). *(AC-09b)*
- **RP-5** A **final successful submission run must not contain retry exhaustion** (nor watchdog/auth failure). *(OQ-A7)*

---

## 12. Transcript Rules

- **TX-1** The **JSONL transcript** preserves **every accepted message** and the **relevant rejected/regenerated events** (one JSON object per line). *(D-04)*
- **TX-2** The **Markdown transcript** is a human-readable rendering of the accepted flow. *(D-04, D-07)*
- **TX-3** **Evidence artifacts must be linked** — `evidence_refs` resolve to `EvidenceRecord`s persisted under `results/evidence/`. *(D-06)*
- **TX-4** **No secrets** appear in any transcript or artifact. *(C-06, SR-2)*

---

## 13. Example JSON Snippets (illustrative only — NOT real run evidence)

> ⚠️ These are **hand-written illustrations** of the schema for review. They are **not**
> output from any real or mock run and must never be presented as run evidence.

**13.1 Accepted opening argument**
```json
{
  "message_id": "msg-0001",
  "session_id": "sess-demo",
  "round_index": 1,
  "turn_index": 1,
  "sender_role": "pro",
  "receiver_role": "judge",
  "turn_type": "opening_argument",
  "protocol_status": "accepted",
  "claim_id": "claim-pro-1",
  "argument": "Requiring AI coding agents in SE courses builds industry-relevant skills...",
  "evidence_refs": ["ev-001"],
  "content": "Requiring AI coding agents in SE courses builds industry-relevant skills...",
  "word_count": 58,
  "created_at": "2026-01-01T00:00:00Z"
}
```

**13.2 Accepted rebuttal with `opponent_claim_id`**
```json
{
  "message_id": "msg-0002",
  "session_id": "sess-demo",
  "round_index": 1,
  "turn_index": 2,
  "sender_role": "con",
  "receiver_role": "judge",
  "turn_type": "rebuttal",
  "protocol_status": "accepted",
  "claim_id": "claim-con-1",
  "opponent_claim_id": "claim-pro-1",
  "argument": "Mandating AI agents can erode foundational problem-solving skills...",
  "evidence_refs": ["ev-002"],
  "content": "Mandating AI agents can erode foundational problem-solving skills...",
  "word_count": 61,
  "created_at": "2026-01-01T00:01:00Z"
}
```

**13.3 EvidenceRecord**
```json
{
  "evidence_id": "ev-002",
  "session_id": "sess-demo",
  "source_type": "web",
  "title": "Study on novice programmer skill retention",
  "url": "https://example.org/study",
  "snippet": "Students who relied heavily on automated tools showed lower unaided performance...",
  "retrieved_at": "2026-01-01T00:00:50Z",
  "query": "AI coding tools effect on student skill",
  "supports_claim_id": "claim-con-1",
  "relevance_status": "relevant",
  "provider_name": "mock",
  "rank": 1,
  "cached": false
}
```

**13.4 FinalJudgment**
```json
{
  "session_id": "sess-demo",
  "winner_role": "pro",
  "loser_role": "con",
  "scores": {
    "pro": {"clarity": 4, "responsiveness": 4, "evidence_quality": 4,
            "position_consistency": 5, "respectful_tone": 5, "persuasive_force": 4,
            "total": 26, "protocol_violations": 0, "regeneration_count": 0},
    "con": {"clarity": 4, "responsiveness": 3, "evidence_quality": 4,
            "position_consistency": 5, "respectful_tone": 5, "persuasive_force": 3,
            "total": 24, "protocol_violations": 0, "regeneration_count": 1}
  },
  "tie_break_used": false,
  "tie_break_reason": null,
  "reasoning": "Pro maintained tighter responsiveness and stronger persuasive force...",
  "limitations": "Scores reflect persuasiveness per the rubric, not factual ground truth.",
  "created_at": "2026-01-01T00:10:00Z"
}
```
