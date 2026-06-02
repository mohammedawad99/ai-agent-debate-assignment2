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
- [ ] **ddgs available.** Currently **NOT installed** (`ddgs_available=False`). Install
      intentionally before the run: `uv add ddgs` (updates `pyproject.toml` + `uv.lock`),
      then re-run the quality gate.
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

## 8. Known limitation to acknowledge before Phase 7 (important / honest)
The project-local prompt templates (Phase 6.4) are **not yet wired into the agents'
provider call**. Today `DebateAgent.produce` sends a **minimal** prompt
(`"Argue as {role}: {claim_id}"`) to the provider and builds the JSON message around the
returned text; the **Judge scoring is fixed/deterministic** and collapse/off-side checks
are **marker-based offline stand-ins**. Consequently, a real run executed **now** would
genuinely exercise: real Claude text generation, real ddgs evidence retrieval,
parent-mediated routing, regeneration, and artifact writing — but the **arguments would
be driven by a trivial prompt** and the **winner would be decided by fixed scores +
configured tie-break**, not by content-derived persuasiveness.

**Recommendation:** before the meaningful Phase 7 run, add a small **Phase 6.5** to wire
`prompts/` (judge/pro/con + `{topic}`/`{role}`/`{opponent_claim_id}` rendering) into the
provider call (and, if feasible, content-aware Judge scoring). Alternatively, proceed
with a **clearly-labeled "plumbing" real run** that demonstrates the mechanics, and
document the scoring/prompt limitation in the README. **This decision is made before
executing, and disclosed honestly in the run's artifacts and README.**
