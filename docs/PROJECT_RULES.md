# Project Rules — Assignment 2

> These are **strict, non-negotiable rules** for this project. They are derived from
> the assignment requirements ([`REQUIREMENTS_AUDIT.md`](./REQUIREMENTS_AUDIT.md)) and
> the Assignment 1 feedback ([`LESSONS_FROM_ASSIGNMENT1.md`](./LESSONS_FROM_ASSIGNMENT1.md)).
> Breaking any rule is a defect, regardless of whether the code "works".

---

## Process Rules

### RULE 1 — No implementation before PRD, PLAN, and TODO
No file may be created under `src/` (implementation code) until:
1. `docs/PRD.md` exists and is reviewed,
2. `docs/PLAN.md` exists and is reviewed, and
3. `docs/TODO.md` exists with an approved phase plan.

Documentation, configuration scaffolding, and tests scaffolding are exempt only
where the TODO phase explicitly allows them.

### RULE 2 — Prove, never claim
No statement that the system "works" may be made without backing evidence:
a passing test, a committed log, a transcript, or a labeled screenshot. **No
unsupported claims.**

### RULE 3 — Document the AI-assisted workflow
Prompts, key decisions, and their rationale are captured in-repo as work proceeds.

---

## Architecture & Communication Rules

### RULE 4 — All child messages pass through the Judge
Every message from Pro or Con is routed through the Parent/Judge agent.

### RULE 5 — No direct child-to-child communication
There must be **no code path** allowing Pro ↔ Con to exchange messages directly.
This is verified by an integration test.

### RULE 6 — The Judge must choose a winner
A single winner is always selected. **Ties are forbidden.** A deterministic,
documented tie-break rule resolves equal scores.

### RULE 7 — Structured JSON protocol is required
All inter-agent communication uses structured, schema-validated JSON. Malformed
messages trigger regeneration, never a crash.

### RULE 8 — SDK and CLI separation
All business logic lives in the **SDK layer**. The **CLI only calls the SDK** and
contains no business logic.

### RULE 9 — Project-local prompts/skills only
Prompts and skills live in the repository. **No reliance on global Claude skills.**

---

## Implementation Rules

### RULE 10 — No hardcoded parameters
No hardcoded paths, magic numbers, provider settings, model names, or debate
parameters. Everything tunable comes from config files.

### RULE 11 — Resource control is mandatory
Every LLM / CLI-provider call goes through the **Gatekeeper** (rate/budget/concurrency
limits) and has a **timeout**. Long-running autonomous processes have a
**watchdog/keep-alive**.

### RULE 12 — Structured, rotating logs
The system emits structured logs with configurable rotation. Logs must never
contain secrets.

### RULE 13 — Cost/resource tracking required
Each run accounts for calls, tokens, and estimated cost, and surfaces them.

---

## Quality Rules

### RULE 14 — Tests and quality gates required
TDD-oriented development. Quality gates — **ruff, format check, pytest, coverage,
file-size checks, required-doc checks** (and mypy if practical) — must pass before
submission. Tests must not depend on live network or live LLM calls.

---

## Security Rules

### RULE 15 — No secrets in Git
API keys are **never** committed. `.env` is gitignored. Only `.env.example`
(a template, added later) may be committed. Logs must not leak secrets.

---

## Output Rules

### RULE 16 — Debate language
Debate output is in **English** (recommended) or Hebrew — **never Arabic**.

### RULE 17 — Real evidence only
Transcripts, logs, screenshots, and results must reflect actual runs. **Fabricated
evidence is strictly prohibited.**
