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
- **Fix:** replace `response_match_score` with `final_response_match_v2` (LLM-judged semantic similarity) in `eval/test_config.json`, with the judge model pinned to `gemini-3.1-flash-lite` (no silent fallback, NFR-03/CON-02), `num_samples = 5`, pass threshold `0.5`. Threshold kept at the prior numeric bar so the change is "same bar, better metric," not a loosened gate.
- **Trade-off (stated honestly):** `final_response_match_v2` makes judge-model LLM calls (cost/latency, and it is an LLM judging an LLM — non-deterministic). It is therefore a **live** criterion, not part of the offline suite (NFR-02).

### D3 — `normalize_topic` rejects `"adk tools"` (FR-04)
- **Symptom:** the model naturally asked for the topic as `"ADK tools"`; `normalize_topic` produced `"adk tools"`, which is not a card key, so both the tool and the guardrail returned `unsupported_topic`. The model then retried with `"tools"` — the extra failed call further broke the `EXACT` trajectory.
- **Evidence:** `eval/results/learning_coach_eval_results.txt` shows `start_quiz(topic='ADK tools')` followed by a retry `start_quiz(topic='tools')`.
- **Fix:** strip the leading `adk ` qualifier in `normalize_topic` (`learning_coach/tools.py`) so `"ADK tools"` → `"tools"`. Applied in `normalize_topic` so both `tools.py` and the `callbacks.py` guardrail (which imports it) benefit. Regression test: `tests/test_tools.py` (`@pytest.mark.req("FR-04")`), 3 offline tests covering the normalizer, the tool, and the guardrail. **Verified green offline.**

### D4 — Single source of thresholds for Web and CLI (FR-03)
- **Finding:** largely already satisfied. There is exactly one `eval/test_config.json`; the README already states it governs both the CLI and ADK Web's Eval tab (README lines ~97, ~147, ~168, ~178). No competing config existed.
- **Action:** keep it single (the FR-02 edit modifies this same one file), and correct the now-stale README line that described the active criterion as "ROUGE-1" to `final_response_match_v2`.

## After (post-fix)

| Check | Before | After | How verified |
|---|---|---|---|
| Offline suite (incl. FR-04 regression + updated config-schema test) | n/a | **9/9 passing, < 1 s** | `pytest` (offline, this repo) — done |
| `tool_trajectory_avg_score` (FR-01) | 0.0 ×3 | _target 1.0 ×3 — pending live run_ | `adk eval` (owner-run) |
| Response similarity (FR-02) | 0.1965 / 0.2953 / 0.588 (ROUGE-1) | _`final_response_match_v2` scores — pending live run_ | `adk eval` (owner-run) |
| Cases passing | 0/3 | _target 3/3 — pending live run_ | `adk eval` (owner-run) |

**Owner action to complete the "after" numbers (live run, needs `GEMINI_API_KEY`):**

```powershell
adk eval learning_coach learning_coach/learning_coach_basics.evalset.json --config_file_path eval/test_config.json --print_detailed_results
```

The offline results above are final. The live-run rows are filled in from the owner's `adk eval` output; they are left explicitly pending here rather than guessed (honesty rule — results from a run that has not happened are not reported as numbers).
