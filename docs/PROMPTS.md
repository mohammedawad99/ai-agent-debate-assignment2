# Prompts

This project keeps its agent/Judge prompts as **project-local templates** under the
repository `prompts/` directory — **not** as global Claude skills. They are versioned,
reviewable, and traceable to the protocol design (PROTOCOL.md, SCORING_AND_VALIDATION.md),
satisfying the course requirement (`R-21`, PROJECT_RULES RULE 9) that prompts/skills be
local to the project and documented.

> **Status (Phase 6.4):** these are **templates and a loader/renderer only**. They are
> not yet wired into the agents' runtime, and **no real Claude run has happened**. Mock
> mode remains the default.

## Templates

| File | Purpose |
|------|---------|
| `prompts/agents/judge.md` | Judge: parent-mediated routing, reject direct Pro↔Con, role/evidence/opponent-reference checks, agreement-collapse & off-side-drift prevention, 0–5 rubric, exactly one winner (no tie), configured technical tie-break disclosure, untrusted-evidence rule. |
| `prompts/agents/pro.md` | Pro: argue *for* requiring AI coding agents; respond to the opponent's claim; respectful; `evidence_refs`; never concede the Con position; JSON protocol. |
| `prompts/agents/con.md` | Con: argue *against*; same discipline as Pro on the opposite side. |
| `prompts/protocol/regeneration.md` | Tell an agent its output violated the protocol, list validation errors, request corrected JSON only, preserve role/side. |
| `prompts/protocol/final_judgment.md` | Apply the rubric, explain the winner, no tie, disclose any technical tie-break. |

`config/agents.json` references these via paths **relative to `prompts_dir`** (no
absolute paths, no secrets).

## Why local, not global skills
Global Claude skills are hidden from the repository, not reviewable by the grader, and
not reproducible. Project-local prompts are committed, diffable, and cited from the
design docs — so the debate's instructions are transparent and auditable.

## Placeholders
Templates use simple `{placeholder}` tokens (e.g. `{topic}`, `{role}`,
`{opponent_claim_id}`, `{validation_errors}`). The renderer
(`agent_debate.prompts.templates.render`) replaces a bare `{word}` only when a value is
supplied and raises `PromptError` if a `{word}` has no value (fail-clearly). It performs
**no eval, no code execution, no external template engine**; JSON-like braces
(`{"k": 1}`) are left untouched.

## Safety rules
- **Untrusted evidence:** search/evidence snippets are **data, not instructions**. No
  retrieved text may override the system/Judge/protocol/role rules. This is stated in
  the Judge and regeneration prompts and enforced structurally in validation.
- **No secrets** appear in prompts or in `config/agents.json`.
- The loader rejects **absolute paths** and **`..` traversal**.

## Status disclosure
The prompts describe intended behavior; deterministic offline checks (collapse/drift
markers, scoring) stand in for full semantic judgment during testing. A real,
evidence-backed Claude run is reserved for **Phase 7**.
