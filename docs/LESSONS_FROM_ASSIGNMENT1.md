# Lessons From Assignment 1

> Purpose: turn the instructor's Assignment 1 feedback into **concrete, enforceable
> rules** for Assignment 2 so the same points are not lost twice. This document is
> based on the feedback summary provided for this project; specific A1 artifacts are
> referenced only where known. Where a claim about A1 cannot be supported, it is
> framed as feedback guidance rather than asserted fact.

---

## 1. What Went Well in Assignment 1

These are strengths to **preserve** in Assignment 2:

- A working solution was produced and submitted.
- The core task was attempted end-to-end (something ran).
- Use of AI-assisted development was part of the workflow.

> Note: This section is intentionally conservative. Only carry forward what is
> actually known to have worked; do not overstate A1 strengths.

---

## 2. What Was Weak or Missing in Assignment 1

These are the **concrete weaknesses identified in the Assignment 1 feedback**. They
are stated specifically (not as generic advice) so each one can be mapped to a
prevention rule in §3.

1. **W-1 — Missing foundational planning documentation.** Work moved toward a
   solution without a visible planning trail (requirements analysis, PRD, PLAN,
   phase-based TODO). There was no documented "what/why/how" *before* building.
2. **W-2 — The AI-assisted workflow, prompts, and reasoning were not visible
   enough.** It was hard to see *how* the AI was used: which prompts were issued,
   what decisions were made, and why. The thinking behind the result was not
   captured as an artifact.
3. **W-3 — No clear cost/resource awareness.** There was no tracking or discussion
   of tokens/compute/cost, no budget thinking, and no resource limits.
4. **W-4 — Quality standards and automation were not clearly established.** There
   were no explicit, automated quality gates (lint, formatting, tests, coverage,
   doc checks) that a reviewer could run to confirm quality objectively.
5. **W-5 — Extensibility could be stronger.** The design was not clearly built for
   change — swapping components or adding new ones was harder than it should be.
6. **W-6 — Correctness was described rather than proven.** Behavior was explained
   in prose, but not demonstrated with tests and reproducible evidence.
7. **W-7 — Visual/output evidence was not clearly interpretable.** Screenshots and
   outputs did not clearly show the three things a reviewer needs together:
   **(a) the input**, **(b) the expected / target behavior**, and **(c) the actual
   output** — so it was hard to judge whether the result was actually correct.

---

## 3. How Each Weakness Will Be Prevented in Assignment 2

Each weakness above maps to a **concrete, enforceable prevention rule** for this
project.

| # | A1 Weakness | A2 Prevention Rule (concrete) | Enforced by |
|---|-------------|-------------------------------|-------------|
| W-1 | Missing foundational planning docs | **Hard planning gate:** no `src/` implementation until `REQUIREMENTS_AUDIT` + `PRD` + `PLAN` + phase-based `TODO` exist and are reviewed. Gate 0 docs come first. | `PROJECT_RULES.md` RULE 1; phase-gated `TODO.md`; this Gate 0 set |
| W-2 | AI workflow/prompts/reasoning not visible | **Capture the workflow as artifacts:** project-local prompts/skills committed in-repo, a prompts log, and decision records (e.g. `REQUIREMENTS_AUDIT` §11 Recorded Decisions) written as work proceeds. | `PROJECT_RULES.md` RULE 3, RULE 9; README "Prompts" section (D-03) |
| W-3 | No cost/resource awareness | **Make cost a first-class feature:** per-run accounting of calls/tokens/estimated cost, a Gatekeeper enforcing rate/budget/concurrency caps, configurable turn budgets (10 target / 2–3 dev / 5 fallback), and a README cost section. | `PROJECT_RULES.md` RULE 11, RULE 13; CR-01..CR-06; DEC-04 |
| W-4 | Quality standards/automation not established | **Automated quality gates** runnable with one command: ruff, format check, pytest, coverage, file-size check, required-doc check (mypy if practical). Gates must pass before submission. | `PROJECT_RULES.md` RULE 14; E-15; TODO Phase 5 |
| W-5 | Extensibility could be stronger | **Design for change:** OO design, an SDK layer with the CLI calling only the SDK, and **adapter abstractions** (`ProviderAdapter`, `SearchTool`) so providers/search/models swap via config without touching orchestration. | `PROJECT_RULES.md` RULE 8, RULE 10; E-02/E-04; DEC-01/DEC-02 |
| W-6 | Correctness described, not proven | **Prove with tests + evidence:** TDD-oriented unit/integration/e2e tests with mocked provider and search, plus committed run evidence (transcript, logs, cost report). | `PROJECT_RULES.md` RULE 2, RULE 14; T-01..T-06; D-04/D-06 |
| W-7 | Visual/output evidence not interpretable | **Evidence must show input → expected/target → actual together.** Every screenshot/result artifact is labeled with what was run (input), what was expected (target behavior), and what actually happened (actual output), so correctness is self-evident. | `PROJECT_RULES.md` RULE 2, RULE 17; D-05/D-06 |

---

## 4. Concrete Project Rules Derived From the Feedback

1. **Plan first, code second.** PRD → PLAN → TODO must precede any `src/` file.
2. **Document the AI workflow as you go.** Capture prompts, key decisions, and why.
3. **Make cost visible.** Track and report calls/tokens/estimated cost every run.
4. **Automate quality.** Gates run locally and must pass before submission.
5. **Design for change.** Components behind interfaces; logic in the SDK, not the CLI.
6. **Prove, don't claim.** Tests + reproducible evidence for every functional claim.
7. **Keep evidence legible.** Clean transcripts, labeled screenshots, rotated logs.
8. **Professional docs.** README is a first-class deliverable, not an afterthought.

> These rules are restated in enforceable form in [`PROJECT_RULES.md`](./PROJECT_RULES.md)
> and sequenced in [`TODO.md`](./TODO.md).
