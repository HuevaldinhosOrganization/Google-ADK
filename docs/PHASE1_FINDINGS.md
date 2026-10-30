# Phase-1 Findings — learning_coach evaluation fixes (M1)

| Field | Value |
|---|---|
| Milestone | M1 (SRS §6.1, FR-01..05) · evidence claim EVD-07 |
| Date | 2026-10-30 |
| Scope | The existing `learning_coach` evalset + eval config only. `learning_coach` is frozen phase-1 evidence; only M1 touches it. |
| Evidence baseline | 6 stored runs in `learning_coach/.adk/eval_history/` (`1793233140`, `1793233253`, `1793233551`, `1793233653`, `1793233905`, `1793234203`). Principal run **`1793233905`** matches `eval/results/learning_coach_eval_results.txt` (run dated 2026-10-28). |

> **What M1 is.** The six stored runs all failed (0/3 cases passing). Four defects in the *evaluation setup* (not the agent) caused those failures. This document records each defect, its evidence, the fix, and the before/after numbers — the EVD-07 claim: "I found that my first evals were wrong, and fixed them."

## Before (run `1793233905`, pre-fix)

| Case | `tool_trajectory_avg_score` (thr 1.0) | `response_match_score` (ROUGE-1, thr 0.5) | Result |
|---|---|---|---|
| explain_tools | 0.0 | 0.1965 | FAIL |
| explain_evaluation | 0.0 | 0.2953 | FAIL |
| start_quiz | 0.0 | 0.588 | FAIL |

**0/3 cases passed.** Every trajectory scored 0.0, and two of three response-match scores were far below threshold despite the answers being substantively correct.

## Defects, fixes and evidence

### D1 — Expected trajectories omit the `transfer_to_agent` hand-off (FR-01)
- **Symptom:** `tool_trajectory_avg_score = 0.0` on all three cases.
- **Root cause:** the root `learning_coach` agent delegates to a specialist (`concept_tutor` / `quiz_coach`) via `transfer_to_agent` before the specialist tool runs, but the evalset's expected `tool_uses` listed only the specialist tool. With `EXACT` match, the unlisted `transfer_to_agent` in the actual trajectory is a mismatch (see README line ~272).
- **Evidence:** actual trajectories in `eval/results/learning_coach_eval_results.txt` begin with `transfer_to_agent(agent_name=...)` then the specialist call; expected began with the specialist call.
- **Fix:** prepend the expected `transfer_to_agent` to each case's `tool_uses` in `learning_coach/learning_coach_basics.evalset.json` (`concept_tutor` for explain_tools/explain_evaluation, `quiz_coach` for start_quiz).

### D2 — ROUGE-1 response gate penalizes correct paraphrases (FR-02)
- **Symptom:** correct-but-reworded answers scored 0.1965 / 0.2953 (below the 0.5 threshold).
- **Root cause:** `response_match_score` is ROUGE-1 word overlap, a lexical metric — it is not a semantic-correctness check, so a correct answer worded differently scores poorly.
- **Fix:** replace `response_match_score` with `final_response_match_v2` (LLM-judged semantic similarity) in `eval/test_config.json`, with the judge model pinned to `gemini-3.1-flash-lite` (no silent fallback, NFR-03/CON-02), `num_samples = 3`, pass threshold `0.5`. Threshold kept at the prior numeric bar so the change is "same bar, better metric," not a loosened gate.
- **Trade-off (stated honestly):** `final_response_match_v2` makes judge-model LLM calls (cost/latency, and it is an LLM judging an LLM — non-deterministic). It is therefore a **live** criterion, not part of the offline suite (NFR-02).
- **Free-tier operational limit (observed 2026-10-30):** the first live run hit `429 RESOURCE_EXHAUSTED` — the free tier allows **15 generate_content requests/minute** for `gemini-3.1-flash-lite`, shared by the agent's own generation calls and the judge calls. `num_samples` was set to **5** initially (5 judge calls × 3 cases = 15, before counting agent calls) and lowered to **3** to fit the quota; ADK still retries with backoff. This is the concrete instance of AIR-22's "free-tier rate limits cap the sample size," and `num_samples = 3` is the recorded, defensible setting — reliability-vs-quota trade-off, not a tuned-to-win choice.

### D3 — `normalize_topic` rejects `"adk tools"` (FR-04)
- **Symptom:** the model naturally asked for the topic as `"ADK tools"`; `normalize_topic` produced `"adk tools"`, which is not a card key, so both the tool and the guardrail returned `unsupported_topic`. The model then retried with `"tools"` — the extra failed call further broke the `EXACT` trajectory.
- **Evidence:** `eval/results/learning_coach_eval_results.txt` shows `start_quiz(topic='ADK tools')` followed by a retry `start_quiz(topic='tools')`.
- **Fix:** strip the leading `adk ` qualifier in `normalize_topic` (`learning_coach/tools.py`) so `"ADK tools"` → `"tools"`. Applied in `normalize_topic` so both `tools.py` and the `callbacks.py` guardrail (which imports it) benefit. Regression test: `tests/test_tools.py` (`@pytest.mark.req("FR-04")`), 3 offline tests covering the normalizer, the tool, and the guardrail. **Verified green offline.**

### D4 — Single source of thresholds for Web and CLI (FR-03)
- **Finding:** largely already satisfied. There is exactly one `eval/test_config.json`; the README already states it governs both the CLI and ADK Web's Eval tab (README lines ~97, ~147, ~168, ~178). No competing config existed.
- **Action:** keep it single (the FR-02 edit modifies this same one file), and correct the now-stale README line that described the active criterion as "ROUGE-1" to `final_response_match_v2`.

### D5 — `EXACT` trajectory matching couples the test to the model's argument phrasing (FR-01/FR-04)
- **Observed (live run `1793384791`):** after the FR-01 + FR-04 fixes, `start_quiz` still failed `tool_trajectory_avg_score` (0.0). The model called `start_quiz(topic='ADK tools')` for the prompt "Start a quiz about ADK tools", but the expected arg was `topic='tools'`. `final_response_match_v2` passed (1.0) — the answer was correct; only the `EXACT` arg string differed.
- **Insight:** FR-04 makes **both** `"tools"` and `"ADK tools"` behaviorally correct (both resolve to the tools card). `EXACT` trajectory matching, however, compares the literal argument, so it tests the model's *phrasing*, not the *correctness* of the call. This is a known limitation of `EXACT` trajectory matching, worth stating rather than hiding.
- **Fix:** set the `start_quiz` expected arg to `"ADK tools"` — the model's actual, now-valid output for that prompt. (A more robust design would assert the tool was called and resolved to the right card rather than an exact arg string; out of scope for the frozen phase-1 demo, noted as a limitation.)

## After (post-fix)

Live run **`1793384791`** (2026-10-30, `num_samples = 3`), **before** the D5 arg fix:

| Case | `tool_trajectory_avg_score` (thr 1.0) | `final_response_match_v2` (thr 0.5) | tokens | duration | Result |
|---|---|---|---|---|---|
| explain_tools | 1.0 ✅ | 1.0 ✅ | 2361 | 4.66 s | **PASS** |
| explain_evaluation | 1.0 ✅ | 1.0 ✅ | 2389 | 11.17 s | **PASS** |
| start_quiz | 0.0 ❌ (arg `ADK tools` ≠ expected `tools`) | 1.0 ✅ | 2358 | 4.35 s | FAIL |

**2/3 passing** on that run; the single failure was the D5 argument-string mismatch, now fixed in the evalset.

| Check | Before | After |
|---|---|---|
| Offline suite (FR-04 regression + updated config-schema test) | n/a | **9/9 passing, < 1 s** (done) |
| Response similarity (FR-02) | 0.1965 / 0.2953 / 0.588 (ROUGE-1, 2 below threshold) | `final_response_match_v2` **1.0 on all 3** (semantic judge no longer penalizes paraphrase) |
| `tool_trajectory_avg_score` (FR-01) | 0.0 ×3 | 1.0 on 2/3; start_quiz → 1.0 expected after the D5 arg fix (**confirming re-run pending**) |
| Cases passing | 0/3 | 2/3 on run `1793384791`; **target 3/3 after the D5 fix — confirming re-run pending** |

The response-match and two trajectories are **confirmed** on a real run. The only outstanding number is the `start_quiz` trajectory after the D5 arg fix; a confirming re-run is needed (and must respect the free-tier 15 RPM limit — see D2).

**Owner action to confirm 3/3 (live run, needs `GEMINI_API_KEY`):**

```powershell
adk eval learning_coach learning_coach/learning_coach_basics.evalset.json --config_file_path eval/test_config.json --print_detailed_results
```
