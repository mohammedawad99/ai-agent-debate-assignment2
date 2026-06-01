# Configuration

All tunable behavior lives in JSON files under `config/` — **nothing is hardcoded**
(PROJECT_RULES RULE 10, E-10/E-11). These are **templates with safe defaults and no
secrets**. Secrets (only if the optional API provider is used) come from the environment
via `.env` (see `.env.example`); `.env` is gitignored and never committed.

> Phase 4 status: these are configuration **templates**. The `ConfigLoader` that reads
> and validates them is implemented in a later phase.

| File | Purpose |
|------|---------|
| `config/app.json` | Top-level wiring: run mode (`dev`/`full`/`budget`), which provider/search adapter is active, and output paths (transcript, judgment, evidence, cost report, logs). |
| `config/debate.json` | Debate parameters: topic, language, turns per side (`full`=10, `dev`=3, `budget_fallback`=5), word limits (child=160, judge=400), retry cap (2), rubric scale/dimensions (0–5, equal weight), and `final_tie_break_priority` (default `["con","pro"]`). |
| `config/agents.json` | Role definitions for Judge/Pro/Con and references to project-local prompt templates (prompt files authored in Phase 6). |
| `config/providers.json` | Provider adapters: `mock` (tests), `claude_cli` (primary, login-based subprocess — **no key**), and an optional future `api_key` provider whose key is read from an **env var name**, never stored. Includes per-call timeouts. |
| `config/search.json` | Search/evidence tools: `mock` (tests) and the no-key `ddgs` candidate; evidence policy (min refs per turn, reuse allowed, relevance required, untrusted-content flag); per-search timeout + retries. |
| `config/logging.json` | Structured logging: level, format, console/file sinks, rotation (`max_bytes`/`backup_count`), JSONL event log, and secret redaction. |
| `config/rate_limits.json` | Gatekeeper limits (max provider/search calls, max retries, concurrency, max runtime) and the cost proxy (`chars/4` token **estimate**, explicitly labeled not-billing). |

## Conventions
- Keys prefixed with `_` (e.g. `_comment`, `_note`, `_active_options`) are **human-facing
  annotations**, not runtime settings.
- No file contains an API key, token, password, or other secret.
- Values intentionally mirror the figures fixed in `docs/PRD.md`, `docs/PLAN.md`, and
  `docs/SCORING_AND_VALIDATION.md`, so config stays traceable to the design.
