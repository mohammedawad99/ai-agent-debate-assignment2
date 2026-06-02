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
- [x] **Claude CLI installed and logged in.** Installed: **yes** (`claude --version` →
      `2.1.160`, Claude CLI on PATH at `~/.local/bin/claude`). **Login VERIFIED in Phase
      7.1** via the non-prompt `claude auth status` (`loggedIn: true`, auth method
      `claude.ai`, first-party). No debate prompt was sent. The run would still abort
      cleanly with `auth_failure`/`ProviderError` if a future session is logged out.
      **Auth is time-bound. Re-run `claude auth status` immediately before the Phase 7
      controlled real run; do not rely only on the Phase 7.1 snapshot.**
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

## 8. Readiness status (updated after Phase 7.14)
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
- **RESOLVED — Claude CLI login verified (Phase 7.1).** `claude auth status` reported
  `loggedIn: true` (claude.ai, first-party) — a status check only, **no prompt sent, no
  debate run**. Auth is time-bound — **re-check `claude auth status` immediately before
  the real run** (do not rely on this snapshot). Whether the real run uses
  `--judge-provider claude_cli` (content-aware scoring) or keeps the deterministic default
  is a per-run flag decision, not a code change. The first controlled real run remains
  **2 turns per side**.
- **ATTEMPTED & FAILED HONESTLY (Phase 7.2) — first controlled real run.**
  `results/real_run_20260602_1837/` (2 turns/side, provider=claude_cli, search=ddgs,
  judge=claude_cli) ended `failed_protocol — retry exhausted: word_limit_exceeded`:
  3 real Claude calls, 3 real ddgs searches, 0 accepted turns, no winner, ~155 s. The
  failure is **genuine and preserved as evidence** (partial transcript + `error_report.md`
  + `cost_report.json`); nothing was fabricated.
- **FIX APPLIED (Phase 7.4) — word-limit + prompt tuning.** Root cause: the model was
  never told the limit, the prompts demanded full JSON while the code wraps raw argument
  text, and regeneration re-sent effectively the same prompt. Fix: child word limit raised
  **160 → 220** (config, source of truth); Pro/Con + regeneration prompts now **state the
  configured limit** and ask for **argument text only** (no JSON wrapper); **retry cap
  unchanged**. The provider-backed Judge still outputs JSON (correct — the Judge path
  parses JSON). Tested offline only; **no real Claude/ddgs call in this phase**.
- **ATTEMPTED & FAILED HONESTLY (Phase 7.5) — second controlled real run.**
  `results/real_run_20260602_1912/` (2 turns/side, same flags) made **partial progress**:
  Pro's opening turn was **accepted** (`word_count: 219`, 5 evidence refs) — proving the
  7.4 fix works — but Con's opening then failed `word_limit_exceeded` after 1 attempt + 2
  retries (4 Claude calls, 4 ddgs searches, ~82 s, no winner). Preserved as evidence;
  nothing fabricated.
- **FIX APPLIED (Phase 7.6) — real regeneration wiring + margin instruction.** Evidence
  showed retries were a no-op (runner re-sent the identical prompt), so Con never got to
  shorten. Fix: on retry the runner now builds `JudgeAgent.regeneration_prompt(reason)` and
  passes it into `agent.produce(..., regeneration=...)`, so the retry prompt includes the
  **validation error** (e.g. `word_limit_exceeded`) and the **configured word limit** and
  asks for a corrected, shortened **argument text only** (no JSON). Pro/Con prompts also add
  a **margin instruction** (aim ~180–200 words; hard limit stays 220). `retry_cap`
  unchanged (2); `child_turn_max_words` unchanged (220). Tested offline only — a mocked
  over-limit first attempt now recovers on a shorter retry; **no real Claude/ddgs call in
  this phase**.
- **ATTEMPTED & FAILED HONESTLY (Phase 7.7) — third controlled real run.** Furthest yet:
  **both child turns were accepted** (regeneration + margin worked) and the run **reached
  the provider-backed Judge** for the first time. Claude then returned **empty/non-JSON**
  for the final verdict → `parse_judgment` raised `JudgeError`, which the runner did **not**
  catch → the CLI **crashed with a traceback** and **no artifacts were written** (the
  `results/real_run_20260602_2037/` directory was never created). No winner; nothing
  fabricated. This revealed a robustness gap, not a regression.
- **FIX APPLIED (Phase 7.8) — graceful provider-backed Judge failure.** `JudgeError` is now
  caught by `runner.run()` alongside the other controlled failures: a non-JSON/empty/invalid
  judge verdict yields a `failed_protocol` result that **preserves the accepted child
  turns**, keeps cost metrics, and (when `output_dir` is set) writes `transcript.jsonl`,
  `transcript.md`, `cost_report.json`, and `error_report.md` — **no crash, no fabricated
  winner**. `final_judgment.md` was hardened to demand exactly one JSON object (no markdown,
  no code fence, no prose, no empty response) — a mitigation, not a guarantee. Tested
  offline only; **no real Claude/ddgs call in this phase**.
- **ATTEMPTED & FAILED GRACEFULLY (Phase 7.9) — fourth controlled real run.**
  `results/real_run_20260602_2058/`: **all four child turns were accepted** (Pro/Con ×2),
  substantive, on-side, evidence-cited, under 220 words, **`retry_count: 0`** — the debate
  body now works end-to-end with real Claude + real ddgs (~145 s). The provider-backed Judge
  again returned **non-JSON**, but Phase 7.8 handled it **gracefully**: `failed_protocol`,
  no winner, **all four artifacts written** (incl. `error_report.md`), **no traceback**.
  Still not a successful run (no winner), but the only remaining blocker is now isolated to
  Judge JSON formatting.
- **FIX APPLIED (Phase 7.10) — tolerant provider-backed Judge JSON parsing.**
  `parse_judgment` now tolerantly **extracts** the verdict before strict validation: direct
  JSON still works; a ```` ``` ````-fenced object (with or without a `json` language tag) is
  unwrapped; exactly one JSON object embedded in surrounding prose is extracted via
  `json.JSONDecoder.raw_decode`. **Zero objects → reject; more than one → reject as
  ambiguous.** No `eval`. **All prior strict checks remain** (one winner, opposite loser, no
  tie, reasoning required, scores 0–5). `final_judgment.md` also asks Claude not to use a
  code fence. Tested offline only; **no real Claude/ddgs call in this phase**.
- **SUCCEEDED (Phase 7.11) — fifth controlled real run.** `results/real_run_20260602_2125/`:
  **`status: success`, winner: con.** All 4 child turns accepted (on-side, evidence-cited,
  ≤220 words, **`retry_count: 0`**, 20 evidence refs); the provider-backed Judge returned a
  valid verdict that passed strict validation (Phase 7.10 tolerant parsing). Artifacts
  (`transcript.jsonl`, `transcript.md`, `cost_report.json`; no `error_report.md`) are kept
  **untracked**; no secrets/PII. This is the **first genuine, evidence-backed real debate
  with a single content-derived winner** — but it is **2 turns/side only**, and the
  artifacts do not yet persist the Judge's reasoning/scores.
- **HONESTY FIX (Phase 7.13).** Corrected a now-stale provider-backed Judge `limitations`
  string (formerly "mock-tested; no real Claude run yet") to wording accurate for both the
  mock and real providers. The string never appeared in any artifact. No behavior change.
- **ARTIFACT ENHANCEMENT (Phase 7.14) — persist Judge reasoning/scores.** On a successful
  run `TranscriptWriter` now adds a **Final Judgment** section to `transcript.md` (winner,
  loser, reasoning, per-side 0–5 scores, tie-break, limitations) and writes a
  machine-readable **`final_judgment.json`** (only when a judgment exists; never on a failed
  run; `transcript.jsonl` unchanged). Verified offline (mock judgment); **no real Claude/ddgs
  call in this phase**. The existing `results/real_run_20260602_2125/` predates this and
  still records only the winner.
- **PENDING — a fresh evidence run + the full 10/side run.** Not yet executed. The next real
  run (which will produce the richer artifacts) **must use a fresh timestamped directory**,
  never reusing a prior run dir. 10/side remains a separate, later step.

**Consequence:** a real run now genuinely exercises real Claude argument generation
(meaningful prompts), real ddgs evidence, parent-mediated routing, regeneration, and
artifact writing. The **winner is still decided by fixed scores + tie-break**, which
**must be disclosed** in the run's README/artifacts. Decide before executing whether to
(a) also add content-aware Judge scoring, or (b) run now as a clearly-labeled
mechanics/evidence demonstration with the scoring limitation stated.
