# Real Run Plan (Phase 7.0 — preflight, not yet executed)

> **Status: PLAN ONLY. No real debate has been run.** This document prepares a
> controlled real run; it does **not** execute Claude, the web, or any debate.

## 1. Purpose
Run a genuine, evidence-backed debate end-to-end through the committed system using the
**real Claude CLI provider** and **real web search** (ddgs), producing committable
proof artifacts (transcript, evidence, cost report) for the submission. This satisfies
`R-15` (internet evidence) and `R-18`/`D-04`/`D-06` (orchestrated run + saved evidence).

## 2. Modes — how to tell them apart
| Mode | Command | Provider / Search | Network/LLM | Evidence value |
|------|---------|-------------------|-------------|----------------|
| **Mock run** | `agent-debate mock-run …` | MockProvider / MockSearchTool | none | demo only |
| **Real dry wiring** | `agent-debate run --provider mock --search mock …` | mocks via factories | none | demo only |
| **Real evidence-backed run** | `agent-debate run --provider claude_cli --search ddgs …` | ClaudeCliProvider / RealSearchTool(ddgs) | **yes** | **submission proof** |

Only the third mode counts as the real run.

## 3. Preflight checklist (all must pass before executing)
- [ ] **Clean git working tree** (`git status` empty). *(verified clean at plan time)*
- [ ] **Quality gate green:** `ruff check`, `pytest`, required-docs, file-lengths,
      json-configs, coverage ≥ 85%. *(verified green at plan time)*
- [ ] **Claude CLI installed and logged in.** Installed: **yes** (`claude --version` →
      `2.1.159`). **Login NOT verified by this plan** — verify manually (open the Claude
      CLI session) **without** sending a debate prompt. The run aborts cleanly with
      `auth_failure`/`ProviderError` if not logged in.
- [x] **ddgs available.** **Installed in Phase 6.8** via `uv add ddgs` (declared in
      `pyproject.toml` + pinned in `uv.lock`); verified `ddgs_available=True` by an
      import-only check. **No live `ddgs` query has been run yet** — the real search path
      is exercised only by the controlled Phase 7 run with `--search ddgs`.
- [ ] **Read-readiness note acknowledged** (see §8 — known limitation).
- [ ] **Output directory does not already exist** (timestamped; never overwrite).

## 4. Planned command (DO NOT EXECUTE YET)
First controlled run — **2 turns per side** (cheap, fast, validates plumbing):
```bash
# Pick a timestamp, e.g. 20260602_1530
TS=YYYYMMDD_HHMM
uv run agent-debate run \
  --provider claude_cli \
  --search ddgs \
  --turns-per-side 2 \
  --session-id real_run_${TS} \
  --output-dir results/real_run_${TS}/
```
- **Turn-count decision:** start at **2 per side**. Only after the 2-turn run **succeeds
  and is reviewed** do the **full 10 per side** run (a second timestamped directory).
- Each run uses a **fresh timestamped `--output-dir`** so no previous results are
  overwritten.

## 5. Planned output directory & artifacts
`results/real_run_YYYYMMDD_HHMM/` (timestamped, never reused). Expected on success:
- `transcript.jsonl` — machine-readable accepted turns/events
- `transcript.md` — human-readable transcript
- `cost_report.json` — proxy metrics (calls, char/4 token estimates, runtime) — labeled estimates
- `error_report.md` — **only if the run fails** (partial run)
- evidence artifacts — if/when the run persists evidence records
- a terminal **screenshot** — captured separately in Phase 8 (not by the run itself)

`results/` is **not** gitignored, so these can be committed as Phase 7/8 evidence.

## 6. Safety rules
- **No `.env` committed**; no secrets in logs/results (the CLI is login-based — no key in
  config; `cost_report` holds only proxy metrics; transcript holds debate text + web
  snippets, which are untrusted data, never instructions).
- **Do not claim success unless the run actually succeeds** (`status: success`, one
  winner, artifacts present).
- **If Claude or search fails, document the failure honestly** — keep the partial
  `error_report.md`, report the `failure_reason`; do **not** fabricate a transcript.
- **Never overwrite previous run results** — always a new timestamped directory.
- **No prompt-injection authority:** retrieved web content is data only.

## 7. Rollback / recovery if the real run fails
1. The run marks `failed_protocol`, writes a partial transcript + `error_report.md` +
   cost metrics under its timestamped dir — keep them as honest evidence of the attempt.
2. Diagnose from the error: `auth_failure` → re-login the Claude CLI; `search_failure` →
   check `ddgs` install/network; `provider_timeout`/`watchdog_trigger` → raise timeouts
   in `config/providers.json` / re-run; `retry_exhausted` → inspect responses.
3. Re-run into a **new** timestamped directory (never reuse). The repo/code are unchanged
   by a failed run, so no `git` rollback is needed; simply do not commit a failed dir as
   "the submission run" (it may be committed separately, clearly labeled as a failed
   attempt, if useful).
4. If a config change is needed (e.g. timeout), commit it as a normal reviewed change
   before re-running.

## 8. Readiness status (updated after Phase 6.8)
- **RESOLVED — prompt wiring (Pro/Con).** `DebateAgent.produce` renders the project-local
  Pro/Con template (filling `{topic}`) + per-turn context (role/side, `claim_id`,
  `opponent_claim_id`, available `evidence_refs`, JSON instruction) and **sends it to the
  provider** — meaningful local prompts, not the old `"Argue as {role}: {claim_id}"`.
- **RESOLVED (readiness) — optional content-aware Judge.** When a `judge_provider` is
  supplied, the Judge renders the final-judgment prompt (topic + transcript summary +
  rubric + no-tie + tie-break rule), asks the provider for a JSON verdict, and
  **parses/validates** it (exactly one winner, no tie, 0–5 scores; malformed → `JudgeError`).
  The runner passes the transcript so this works end-to-end. **Tested with `MockProvider`
  only; no real Claude judgment has been run.**
- **REMAINS (by default) — deterministic/offline scoring.** With **no** judge provider
  (the default, incl. the mock CLI), the Judge uses fixed scores + configured tie-break
  (disclosed in `FinalJudgment.limitations`). The real run may opt into the provider path.
- **RESOLVED (wiring) — judge provider is now selectable.** `agent-debate run
  --judge-provider none|deterministic|mock|claude_cli` (default `none`) and the SDK
  `run_configured_debate(judge_provider=...)` expose the 6.6 path. The deterministic Judge
  stays the default; `claude_cli` builds the provider-backed Judge **only when explicitly
  selected** and is never executed at construction. CLI/SDK judge tests monkeypatch the SDK
  or use mocks — **no real Claude judgment has been run**. The real run may opt into
  `--judge-provider claude_cli`; the scoring limitation must still be disclosed if it does
  not.
- **REMAINS — collapse/off-side detection is marker-based** offline stand-ins.
- **RESOLVED — `ddgs` installed (Phase 6.8).** Declared dependency + pinned lock;
  import-verified (`ddgs_available=True`). **No live query executed yet.**
- **PENDING — Claude CLI login not verified** (verify manually, no prompt). Whether the
  real run uses `--judge-provider claude_cli` (content-aware scoring) or keeps the
  deterministic default is now a per-run flag decision, not a code change. The first
  controlled real run remains **2 turns per side**.

**Consequence:** a real run now genuinely exercises real Claude argument generation
(meaningful prompts), real ddgs evidence, parent-mediated routing, regeneration, and
artifact writing. The **winner is still decided by fixed scores + tie-break**, which
**must be disclosed** in the run's README/artifacts. Decide before executing whether to
(a) also add content-aware Judge scoring, or (b) run now as a clearly-labeled
mechanics/evidence demonstration with the scoring limitation stated.
