# Test Plan — Course Assistant

| Field | Value |
|---|---|
| Version | 0.1 (draft for owner approval) |
| Date | 2026-10-30 |
| Owner | Felipe Obando |
| Status | Draft — written after `docs/SRS.md` v0.6 (approved) and `docs/SOLUTION_DESIGN.md` v0.4 |
| Sources of truth | `docs/SRS.md` (what), `docs/SOLUTION_DESIGN.md` (how), `docs/BACKLOG.md` §3 (requirement → test/artifact). This plan **adds no requirement**; it only says how the existing ones are verified. If it disagrees with the SRS, the SRS wins. |

> **Purpose.** Define *how* the Course Assistant is tested before any check is encoded: the test levels, run modes, pass criteria, traceability and honesty rules — and then the detailed M1 plan. This is itself interview evidence (JD-01/JD-04: define acceptable behavior and a measurable evaluation plan before automating checks).

---

## 1. Testing strategy (whole project)

### 1.1 Test levels

| Level | What it covers | Network? | Where | Gate |
|---|---|---|---|---|
| **L0 — Offline unit** | Pure code: policy, schema/validator, retrieval coverage, quiz, review-queue/immutability, import boundary, env handling, `normalize_topic`. Uses the **fake LLM** and the in-memory/temp SQLite. | No | `tests/test_*.py` (pytest) | CI, must stay green; whole suite < 60 s (NFR-02) |
| **L1 — Trajectory evalsets** | Agent *behavior shape*: the tutor transfers then calls `search_lessons`; the grader path ends in `publication_policy`; no tool sets a final grade except the policy/CLI. | Model call (ADK eval) | `*.evalset.json` + `eval/test_config.json`, run via `adk eval` | Owner-run (live); reported, not in CI |
| **L2 — Live evaluation runs** | Measured quality against datasets: calibration, grounding/ablation/canary, integrity, injection, jailbreak, fairness. Produce the AIR reports. | Real Gemini (judge/grader) | `eval/*.py` → `eval/reports/*.json` | Owner-run (live); the evidence artifacts (DQ2: committed) |
| **Static / inspection** | Things verified by reading or by a non-behavioral test: import-boundary (SEC-04), env-key handling (SEC-02), doc presence (FR-05, SEC-06/07), traceability matrix. | No | tests + `scripts/traceability.py` + doc review | CI (traceability gate) |

**Determinism boundary in testing (ADR-001).** L0 asserts *code* decisions exactly (the policy, totals, coverage); L1/L2 *measure* LLM behavior with intervals — they never assert an exact model output as a hard gate. Grounding and jailbreak resistance are **measured, not enforced** (SRS §4.1.1).

### 1.2 Run modes and honesty

- Every run is labeled `fixture` (fake model / stub) or `live` (real model), recorded in the report envelope (AIR-22). Results from fixtures are never presented as real quality.
- Dataset ground truth carries `label_provenance` (`llm_reference` / `llm_generated`, never `human`).
- Small samples are reported with **Wilson 95% intervals**; a `0/n` result shows its upper bound, never "0%" or "proves" (honesty rule, `PROJECT_CHARTER.md` §1.4).
- Tuning happens on `dev` only; `holdout` runs once. Any change after seeing holdout is reported as a holdout-breaking event.

### 1.3 Conventions

- Every test carries its requirement id: `@pytest.mark.req("FR-04")`. `--strict-markers` is on; `req` and `live` are registered in `pyproject.toml`.
- Offline tests must not hit the network — they use the `FakeModelClient` / `EmptyRetriever` seams (SOLUTION_DESIGN §2).
- Live-only tests carry `@pytest.mark.live` and are excluded from the offline suite.
- Flat test file names (`tests/test_<area>.py`), one area per file (SOLUTION_DESIGN §1, DQ3).
- Never edit an expected value/label to make a test pass — report the failure (evaluation-integrity rule).

### 1.4 Traceability and CI

- `docs/BACKLOG.md` §3 is the requirement → test/artifact matrix. This plan does not duplicate it; it points at it.
- `scripts/traceability.py` (M10) fails CI if any **Must** requirement has neither a tagged test nor a declared artifact. Document-only Musts are satisfied by `inspection`.
- CI (`.github/workflows/ci.yml`) runs the **offline suite only** + the traceability gate. Live L1/L2 runs are manual local runs (free tier, no cloud job).

### 1.5 Environments & tooling

- Local: `python -m venv .venv`; `pip install -e ".[dev]"`; `pytest` (offline); `adk web` (Dev UI); `adk eval ...` (L1). Local SQLite for the review queue. No cloud (CON-01).
- The model id is pinned in `config.py` (CON-02); no silent fallback (NFR-03). Live runs need `GEMINI_API_KEY` from the environment (SEC-02), never logged.

### 1.6 Entry / exit criteria

- **Entry (per milestone):** its requirements exist in the SRS; needed datasets/content exist (or are explicitly stubbed `fixture`).
- **Exit (per milestone):** offline suite green; each Must has a passing tagged test or a committed report artifact; live reports (where applicable) generated with the AIR-22 envelope; limitations stated.
- **Feature freeze: Sun 2026-11-01 14:00 CR.** After it: bug fixes, docs, rehearsal only.

---

## 2. M1 — Phase-1 fixes (detailed plan)

M1 fixes the existing `learning_coach` evaluation setup (FR-01..05, SRS §6.1). `learning_coach` is frozen EVD-07 evidence; only M1 touches it. Evidence baseline: 6 stored runs in `learning_coach/.adk/eval_history/` (principal `1793233905`, matching `eval/results/learning_coach_eval_results.txt`): **before = 0/3 cases pass**, trajectory score 0.0, response-match 0.1965 / 0.2953 / 0.588.

| FR | Objective | Level | Test / artifact | Preconditions | Pass criteria |
|---|---|---|---|---|---|
| **FR-01** | Expected trajectories include `transfer_to_agent` before the specialist tool | L1 (behavior) + L0 (schema) | `learning_coach_basics.evalset.json` edited; verified live by `adk eval` (`tool_trajectory_avg_score`); schema validity asserted offline in `tests/test_learning_coach.py::test_evaluation_files_match_google_adk_schemas` | evalset edited for all 3 cases | Live: `tool_trajectory_avg_score = 1.0` on all 3 cases. Offline: evalset still schema-valid, 3 cases |
| **FR-02** | Replace ROUGE-1 `response_match_score` gate with `final_response_match_v2` (semantic, LLM-judge) | L1 (live) + L0 (config schema) | `eval/test_config.json` edited; before/after numbers recorded in `docs/PHASE1_FINDINGS.md`; offline config-criteria assertion updated in `test_learning_coach.py` | FR-01 done; judge model reachable for the live run | Live: the 3 cases pass the new criterion where they are genuinely correct (paraphrase no longer penalized). Offline: config schema test asserts the criteria set `{tool_trajectory_avg_score, final_response_match_v2}` |
| **FR-03** | ADK Web and CLI use one threshold source | Static / inspection | Single `eval/test_config.json`; README states which file governs | — | Exactly one `test_config.json` governs both; README line present. No second config reintroduced when editing for FR-02 |
| **FR-04** | `normalize_topic` no longer rejects `"adk tools"` | **L0 (offline unit, TDD)** | `tests/test_tools.py` (`@pytest.mark.req("FR-04")`): `normalize_topic` strips the `adk ` qualifier; `get_learning_card` and the guardrail both accept `"ADK tools"` | markers registered | 3 offline tests green; no regression in the existing suite; fix lives in `normalize_topic` so both `tools.py` and `callbacks.py` benefit |
| **FR-05** | `docs/PHASE1_FINDINGS.md` write-up | Inspection | The doc: 4 defects, evidence run ids, fix per defect, before/after numbers | FR-01/02/04 done; live rerun numbers available | Doc exists with all four defects, run ids, and before/after figures |

**M1 offline suite (L0, in CI):** `test_tools.py` (FR-04) + the existing `test_learning_coach.py` (agent wiring, tools, guardrail, quiz state, eval-file schema). Target: all green, < 60 s.

**M1 live run (L1, owner-run):** `adk eval learning_coach learning_coach/learning_coach_basics.evalset.json --config_file_path eval/test_config.json` — produces the after-fix numbers for FR-01/FR-02 that feed FR-05. **This is an owner action** (needs `GEMINI_API_KEY`); the agent prepares everything and leaves the numbers to be filled from the owner's run.

**Known coupling to flag:** the current `test_learning_coach.py::test_evaluation_files_match_google_adk_schemas` asserts `criteria == {tool_trajectory_avg_score, response_match_score}`. FR-02 changes that criterion, so this offline test must be updated in lockstep to `final_response_match_v2` — this is an expected test change, not a label edit.

**M1 exit:** offline green (FR-04 + updated schema test); FR-01/02 confirmed by the owner's live `adk eval`; `PHASE1_FINDINGS.md` written with before/after; FR-03 inspection note in README.

---

## 3. M2–M7 — strategy sketch (to be detailed per milestone)

Detailed plans are written when each milestone starts (datasets/design must exist first; sketching them fully now risks rework before the freeze). Focus and dominant level per milestone:

| Milestone | Test focus | Dominant level | Key ids |
|---|---|---|---|
| **M2** Lessons + retrieval + tutor | `search_lessons` coverage gate (code); tutor cites ⊆ retrieved (FR-15 fail-safe); grounding in/out-of-scope + ablation + canary; jailbreak resistance | L0 + L1 + L2 (live) | FR-10..16, AIR-02/14/14a/14b, AIR-03a/15a |
| **M3** Quiz (Should) | MCQ scoring, attempt limits, progress — pure code | L0 | FR-20..22 |
| **M4** Grader + policy | Schema/range/evidence validation; policy fail-closed (one test per fail-closed input, collect-all reasons); verbatim substitution; total computed by code | L0 (offline, fake model) | FR-30..37 |
| **M5** Teacher review | Persistence of every submission; immutability via single conditional write; confirm/correct; status lookup | L0 | FR-40..45 |
| **M6** Calibration + baseline | Exact agreement vs reference labels, false-pass/fail with Wilson; baseline comparison; retention rule on holdout; confidence histogram | L2 (live) + L0 harness | AIR-10..13, AIR-12a |
| **M7** Integrity / injection / fairness / jailbreak | Answer-key leak (string match); injection detector bypass vs policy gate (held-out); fairness name/phrasing pairs with noise control; tutor jailbreak | L2 (live) + L0 harness | AIR-03/03a/15/15a/16/17 |
| **M10** CI + traceability | Offline suite + traceability gate in CI | Static/CI | AIR-20/21, EVD-09 |

---

## 4. What these tests do NOT prove (eval-validity)

- **No human labels.** All ground truth is LLM-generated/self-checked; the reference pipeline uses the **same model** as the grader → self-consistency, not independent calibration (EVD-02). It cannot catch a bias shared across both passes.
- **Grounding & jailbreak are measured, not enforced** — a subtly wrong-but-plausible answer that still cites a valid chunk, or a novel jailbreak, can pass; reported with intervals, never claimed zero.
- **Small samples.** Live datasets are small (free tier); every rate carries a Wilson interval; "inconclusive" is a valid, reported outcome.
- **No load/perf/E2E in the Must.** Latency is a minimal p50/p90 line per report (AIR-22); Playwright E2E and cloud are `Could` (C1/C2), not covered unless built.
- Each generated report also carries a per-metric "what this does not measure" note (AIR-21).
