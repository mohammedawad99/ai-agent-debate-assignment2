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

## Claude CLI provider (`claude_cli`)

`config/providers.json` includes a `claude_cli` provider section, implemented by
`ClaudeCliProvider` (Phase 6.3b). It is **not the active default** — `mock` remains the
default, offline-safe provider, and the `agent-debate` CLI still runs the offline mock
path. `claude_cli` is opt-in and will be wired into a real-mode path in a later phase.

| Field | Meaning |
|-------|---------|
| `command` | Base command to launch the login-based CLI (e.g. `["claude"]`). |
| `args` | Fixed arguments that follow the command (e.g. `["-p"]`). |
| `input_mode` | How the prompt is delivered: `"stdin"` (piped to the process) or `"argument"` (appended as the final CLI argument). |
| `timeout_seconds` | Per-call timeout; on expiry the provider raises `ProviderTimeoutError`. |

**`input_mode` allowed values:** `"stdin"` or `"argument"` (any other value is rejected
with a clear error).

**Wiring note:** `ClaudeCliProvider.__init__` takes a single `command: list[str]`. The
future real-mode wiring layer is responsible for **combining `command` + `args` into that
one list** (e.g. `["claude", "-p"]`) and passing `input_mode`/`timeout_seconds` through.

**Safety:**
- `command`/`args` **must not contain secrets** (API keys, tokens) or **user-specific
  absolute paths**. The CLI is login-based; authentication is handled by the CLI session,
  not by this config.
- The provider never prints the environment and never logs secrets.

**Testing:** `ClaudeCliProvider` tests **mock `subprocess.run`** and do **not** execute
Claude or any real CLI/LLM. **A real Claude-backed debate run has not been executed yet**
(reserved for a later phase / the Phase 7 real run).

## Real search provider (`ddgs`)

`config/search.json` includes a `ddgs` provider section, used by `RealSearchTool`
(Phase 6.3c). `mock` remains the **active default**; `ddgs` is opt-in and not wired into
the default CLI yet.

| Field | Meaning |
|-------|---------|
| `provider_name` | Label recorded on each `EvidenceRecord` (e.g. `"ddgs"`). |
| `max_results` | Maximum results requested per query. |
| `region` | Search region hint (e.g. `"wt-wt"`). |
| `timeout_seconds` | Per-search timeout for the real backend. |
| `retries` | Retry attempts for transient failures. |

**Design note:** `RealSearchTool` takes an **injected search backend** callable
`(query, max_results) -> list[dict]` rather than importing a web library directly. This
keeps the adapter real and behind `SearchTool` while staying fully offline-testable; the
concrete `ddgs`-backed backend (and its dependency) is supplied when a real-mode run is
wired. No keys or personal paths appear in config.

**Safety / testing:** retrieved content is **untrusted evidence data**, never
instructions. Normal tests **inject a fake backend** and **do not call the web**. **Live
search validation is deferred to Phase 7 / a controlled manual smoke test.**
