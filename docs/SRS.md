# SRS — Course Assistant (tutor + graded open answers + teacher review)

| Field | Value |
|---|---|
| Version | 0.5 (approved) |
| Date | 2026-10-30 |
| Owner | Felipe Obando |
| Base repo | `Google-ADK` (package `learning_coach`, ADK 2.13.0, branch `dev`) |
| Hard deadline | **Sun 2026-11-01 14:00 CR** (feature freeze). Mon–Wed = rehearsal only |
| Interview | **Confirmed:** Thu 2026-11-05 16:00–17:00 CR (1 hour) |
| Status | **Approved 2026-10-29.** Code may now be written per this document |

> Source of truth for **what**. If a design note or a prompt disagrees with this file, this file wins.
> Spec changes need owner approval. See `docs/PROJECT_CHARTER.md` for why/who/scope and `docs/BACKLOG.md` for stories/tracking.

### Changelog

**v0.5 (2026-10-30)** — Tutor guardrails against jailbreaks made explicit and measurable. Injection against the **grader** was already specified (FR-32..36, AIR-04, AIR-16); the **tutor's** resistance to role/instruction manipulation was only implied by the answer-key import boundary (SEC-04, AIR-03) and the citation check (FR-15), with no requirement that the tutor refuse an instruction to abandon its role and no adversarial test of it. This revision closes that gap on both LLM surfaces and consolidates the guardrails in one place in `docs/SOLUTION_DESIGN.md` §5.1. Key changes:
- **New FR-16 — tutor resists role/instruction manipulation.** User message and retrieved chunk text are untrusted and never obeyed as instructions that change the tutor's role, disable grounding, reveal hidden data, or produce off-syllabus content. Measured (AIR-15a), not guaranteed.
- **New SEC-08** extends SEC-05's untrusted-input rule (grading prompt) to the tutor's inputs.
- **New AIR-03a (dataset) + AIR-15a (metric)** — a tutor jailbreak/injection set with held-out cases, reporting stay-in-role/refusal rate, hidden-data leaks = 0 with Wilson intervals, and off-syllabus outputs listed, held-out cases reported separately (same honesty construction as AIR-16).
- **New EVD-11** in `PROJECT_CHARTER.md` — a **system-level** red-team claim: tutor and grader are measured (AIR-03a/15a, AIR-04/16), while the coordinator and open_grader agent are bounded by the determinism/import boundaries (no dataset, explained not faked); FR-16/AIR-03a/AIR-15a trace to it. **M7** (BACKLOG §1) and the §3 traceability table updated; new story **US-08**; new **R8** in `docs/RISK_REGISTER.md`.

**v0.4 (2026-10-29)** — Grounding made observable, not only stated. The §4.1.1 residual risk (an answer sourced from model memory that still cites a valid chunk) was a written limitation with no measurement; two cheap, deterministic checks now measure it instead of switching the course to a domain the model doesn't know (rejected: rewrites every lesson, rubric and dataset days before the freeze, and the panel can judge Python examples at a glance). Key changes:
- **New FR-10b — canary facts.** The lessons carry 4 course-specific conventions that general Python knowledge cannot supply, listed in `course_assistant/data/canaries.yaml`. They never contradict Python's real behavior.
- **AIR-02 extended.** +4 canary questions; in-scope questions now also carry `answer_markers` so a memory-sourced answer is detectable by string match.
- **New AIR-14a — retrieval ablation.** The grounding questions are rerun live with `search_lessons` stubbed to return nothing; the tutor must refuse every one. A substantive answer here is direct evidence of answering from memory.
- **New AIR-14b — canary grounding.** With normal retrieval, every canary question must be answered with its canary phrase and cite its canary chunk. A canary that passes in AIR-14b and is refused in AIR-14a is the evidence that the answer came from retrieval.
- **§0.1 Glossary added** covering the whole repository: requirement ids, ADK runtime, course content and tutor, grading and review, evaluation.
- **FR-13 fixed.** The v0.3 relative threshold (≥ 30% of the top chunk's score) could never trigger a refusal, because the top chunk always meets it. Coverage is now a code rule inside `search_lessons`: a chunk qualifies only if it contains at least 2 distinct content terms of the query; no qualifying chunk → empty list → refusal.
- §4.1.1, `PROJECT_CHARTER.md` §6 and `BACKLOG.md` (M2 row, §3 traceability) updated to match. Grounding is still a measured property, not an enforced limit — these checks measure dependence on retrieval; they do not remove the model's knowledge.

**v0.3 (2026-10-29)** — Clarifications from the pre-design documentation review (no decisions reversed; gaps a reviewer would probe are now written down). Key changes:
- **Reference model pinned.** OD-07 resolved: the reference-label pipeline uses the **same** model as the grader (Gemini Flash Lite via AI Studio). §7.1, AIR-01, and EVD-02 (in `PROJECT_CHARTER.md`) are reworded to state this is **self-consistency under reworded prompts, not independent calibration**, and that the blind spot is bias shared by one model across both passes.
- **Grading constants made explicit.** FR-30 / FR-34 now state that `pass_mark = 4` and `borderline_margin = ±1` are fixed across all demo rubrics, and that the borderline band is therefore exactly totals `{3, 4, 5}` → REVIEW, leaving only `{0,1,2,6}` PUBLISH-eligible (the construction already noted in AIR-13, now stated numerically at the source).
- **`confidence` labelled as self-reported.** FR-31 states it is the model's own self-assessment, a known weakly-calibrated signal that AIR-12a exists to test.
- **Holdout composition stated.** AIR-01 notes the holdout reuses `dev`'s questions with fresh answers (answer-generalization, not question-generalization).
- **Retention-rule power acknowledged.** AIR-12 states the ≥10pp/≤10% thresholds run on a small holdout and must be reported with their Wilson intervals; the rule is a pre-registered, admittedly underpowered heuristic.
- **Baseline scoring locked + injection-list versioning.** OD-08 resolved: FR-37 freezes the keyword→score mapping (0 → 0; below half → 1; half or more → 2), pre-registered so the baseline can't be gamed; AIR-22 records the injection detector's pattern-list version alongside prompt versions.
- **Review-queue edges clarified.** FR-42 spells out what a teacher may change and that totals recompute by code; new FR-43a defines how `submission_id`/`student_id` are minted in the no-auth Dev UI.
- **Latency/cost adopted (OD-09).** AIR-22 now records p50/p90 per-grade latency and mean tokens-per-grade.
- **Risk framing promoted (OD-10).** SEC-07 raised to Must and `docs/RISK_REGISTER.md` added (intended use, foreseeable misuse, controls → requirement ids, residual risk, human oversight).
- **Grounding reality stated (§4.1.1).** New note: the model's Python knowledge cannot be removed, so tutor grounding is instructed-verified-measured, not enforced; the grader, by contrast, is *meant* to use that knowledge, fenced by the rubric and the evidence-substring check.

**v0.2 (2026-10-29)** — Patch after a two-pass requirements review (one shallow, one thorough — see `docs/background` for the raw notes). Key changes:
- No human labeler anywhere in this project (owner declined to do manual labeling under time pressure). All calibration, grounding, integrity, injection and fairness ground truth is generated and self-checked by an automated LLM reference pipeline. §7.1, §14 and EVD-02's wording are rewritten to state this honestly instead of implying human labels.
- M9 (annotated trace) and M10 (CI + traceability gate) promoted from Should to Must — they were the only two EVD claims (EVD-08, EVD-09) with zero requirement backing.
- M3 (quiz) downgraded from Must to Should — it backs no EVD claim on its own; kept as the one pure-code contrast case for EVD-01.
- Fixed a holdout-leakage bug in OD-04 (threshold must not be retuned after the holdout run), a broken fallback in §3 (the old fallback couldn't work because the baseline needs labels too), and a fairness test that measured nothing because the grader signature never received a name.
- Filled in every requirement that previously had an unquantified threshold ("minimum score", "agreed tolerance", etc.) with a concrete value or an explicit tuning rule.
- Rubrics locked to exactly 3 criteria (0–6 scale) to match OD-03's pass mark, closing the ambiguity between FR-30 (3–4 criteria) and OD-03 (assumed 3).

**v0.2.1 (2026-10-29)** — Split the single SRS into three files: `PROJECT_CHARTER.md` (why/who/scope/limitations/decisions, §§1–3, 12–15 below), `BACKLOG.md` (epics, Gherkin user stories, traceability, §§5, 13 below), and this file (the testable contract: §§4, 6–11, 16). Section numbers were deliberately **not** renumbered, so every `§7.1`-style reference made before this split, in either of the other two files or in conversation history, still points at the right place.

---

## 0. Scope of this document
This file is the testable contract: architecture/determinism boundary (§4), functional requirements (§6), AI/evaluation requirements (§7), security (§8), non-functional requirements (§9), constraints (§10) and the data model (§11).

Project purpose, the EVD-01..10 evidence claims, non-goals, users/roles, MoSCoW scope, the delivery plan and known limitations moved to `docs/PROJECT_CHARTER.md` in v0.2's file split. User stories, Gherkin acceptance criteria and the full traceability table moved to `docs/BACKLOG.md`. Section numbers below are unchanged from v0.2 (sections 1, 2, 3, 5, 12, 13, 14, 15 now live in those two files) so existing cross-references stay valid. Read those two files first if you haven't — this file assumes the "why" and "who" are already settled.


### 0.1 Glossary

Terms used across this repository (`docs/`, `learning_coach/`, `course_assistant/`, `eval/`, `tests/`). Where a term is defined by a requirement, the requirement id is the authority; this table only summarizes it. ADK basics for the phase-1 `learning_coach` are also explained in the README glossary.

**Requirement and planning ids**

| Term | Meaning |
|---|---|
| **EVD-01..10** | The 10 evidence claims the owner must be able to defend in the interview (`PROJECT_CHARTER.md` §1.2). Every requirement must serve at least one. |
| **FR / AIR / SEC / NFR / CON** | Functional, AI-and-evaluation, security, non-functional and constraint requirements in this file. A suffix letter (FR-10b, AIR-14a) marks a requirement added later without renumbering. |
| **OD-xx** | Open decision for the owner (`PROJECT_CHARTER.md` §7), each with its resolution. |
| **US-xx** | User story with Gherkin acceptance criteria (`BACKLOG.md`). |
| **M / S / C items (M1..M10, S1, C1..C3)** | MoSCoW scope items: Must, Should, Could (`PROJECT_CHARTER.md` §3). "Won't" items are roadmap. |
| **P0..P7** | Delivery phases (`PROJECT_CHARTER.md` §5). Each ends at a **gate**: the evidence required before the next phase starts. |
| **Feature freeze** | Sun 2026-11-01 14:00 CR. After it, only bug fixes, docs and rehearsal. |
| **Traceability** | The mapping requirement → test/artifact → how checked (`BACKLOG.md` §3). `scripts/traceability.py` fails CI if a Must has no test or artifact. |
| **ADR-001** | The architecture decision record for the determinism boundary (§4.1). |

**Google ADK and runtime**

| Term | Meaning |
|---|---|
| **ADK** | Google's Agent Development Kit (version 2.13.0 here), used to define, run, trace and evaluate agents. |
| **Agent / `LlmAgent`** | A model-driven component with a name, an instruction, and optional tools, sub-agents and `output_schema`. |
| **Root / coordinator agent** | `course_assistant`: receives every student message and routes it; it neither teaches nor grades. |
| **Sub-agent, transfer** | A specialist agent under the coordinator (`lesson_tutor`, `open_grader`). The handoff appears in traces as `transfer_to_agent`. |
| **Instruction** | An agent's system prompt (`course_assistant/prompts/*_v<N>.md`). ADK replaces `{identifier}` in it with session-state values, so agent instructions contain no literal curly braces. |
| **Tool** | A Python function an agent can call (`search_lessons`, `grade_open_answer`, `start_quiz`...). |
| **`ToolContext` / session state** | ADK's per-session context and key-value state, used for quiz progress and attempts (FR-21). |
| **Callback** | A function ADK runs around a model or tool step. The citation validator (FR-15) is a callback. |
| **`output_schema`** | A structured format enforced on an agent's final answer (the tutor's `answer`, `cited_chunk_ids`, `covered`). Works together with tools in ADK 2.13.0. |
| **`adk web` / Dev UI** | ADK's developer web UI. The student interface of this demo (FR-50); not a product UI. |
| **`adk run` / `adk eval`** | Run an agent in the terminal / run an evalset against it. |
| **Evalset, `test_config.json`** | ADK evaluation cases (`*.evalset.json`) and the criteria and thresholds applied to them (`eval/test_config.json`, single source per FR-03). |
| **`tool_trajectory_avg_score`, `response_match_score`, `final_response_match_v2`, `hallucinations_v1`** | ADK evaluation criteria: expected tool-call sequence; ROUGE-1 text overlap (replaced in FR-02 because it penalizes correct paraphrases); LLM-judged answer match; LLM-judged unsupported claims (informational only, AIR-14). |
| **Trace** | ADK's record of one run: tool calls, arguments, model turns, timing. EVD-08 requires one annotated trace. |
| **Gemini Flash Lite / AI Studio** | The only model (`gemini-3.1-flash-lite`, from `config.py`, CON-02), used through the Google AI Studio free tier with an API key. Used by the tutor, the grader and the reference-label pipeline. |
| **Temperature** | The model's sampling randomness. Fixed and recorded in every report (AIR-22). |

**Course content and tutor**

| Term | Meaning |
|---|---|
| **Lesson** | One of 8 Markdown files in `course_assistant/content/lessons/` (L1 Variables and types … L8 Error handling, FR-10). |
| **Section / chunk / `chunk_id`** | A lesson section with a stable id (`L3-S2`); the unit of retrieval and citation. |
| **Retrieval / `search_lessons`** | Code that ranks chunks by **BM25** (a deterministic keyword-relevance score) and returns at most `k` (default 5) qualifying chunks (FR-11). No vector database. |
| **Content terms, `min_query_terms_matched`** | The query's words minus stopwords and course-generic words; a chunk qualifies only if it contains at least 2 of them (FR-13). |
| **Coverage / `covered`** | Whether the course material answers the question. Decided in code by FR-13; an empty result means "not covered" and the tutor refuses. |
| **Grounding** | The property that an answer comes from retrieved lesson text. Measured, not enforced (§4.1.1). |
| **Citation / `cited_chunk_ids`** | The chunk ids the tutor says it used. Valid only if they are a subset of the retrieved ids (FR-15). |
| **Canary fact / canary phrase** | A course-only convention planted in a lesson, with a coined name the model cannot guess (FR-10b). If the tutor states it, the answer came from retrieval. |
| **`answer_markers`** | Distinctive terms a correct answer to an in-scope grounding question would contain; used to detect memory-sourced answers under ablation (AIR-02, AIR-14a). |
| **Retrieval ablation** | Rerunning the grounding questions with retrieval stubbed to return nothing; the tutor must refuse all of them (AIR-14a). |
| **In-scope / out-of-scope question** | A question the lessons answer / one they do not (for example deploying Django). |
| **Integrity / answer-key leak** | The tutor revealing a quiz key, rubric or expected answer (US-05, AIR-15). |
| **MCQ / quiz** | Multiple-choice questions scored by code, with attempt limits (FR-20..22, Should priority). |

**Grading and review**

| Term | Meaning |
|---|---|
| **Open question** | A question the student answers in their own words (`course_assistant/data/open_questions.yaml`, ids like `Q-L4-01` = lesson L4). |
| **Rubric / criterion / descriptor** | Per-question scoring guide (`rubrics/<question_id>_v<N>.yaml`): exactly 3 criteria, each scored 0, 1 or 2, with a written descriptor per level (FR-30). |
| **Keywords** | Per-criterion regex patterns in the rubric, used only by `keyword_baseline` (FR-37). Never shown to the grader. |
| **Pass mark / borderline margin / borderline band** | Pass = total ≥ 4 of 6; margin = ±1, so totals 3, 4 and 5 always go to REVIEW (FR-30, FR-34). |
| **`open_grader`** | The ADK agent that collects the student's answer and calls `grade_open_answer`. It never scores. |
| **Grader / `grade_open_answer`** | The tool that calls the model with `grader_v1` and returns a **GradeProposal** (FR-31). |
| **GradeProposal** | Per criterion: `score`, `evidence_quote`, `rationale`; plus `confidence` and `flags`. A proposal, never a final grade. |
| **`evidence_quote`** | Text copied from the student's answer to justify a score; must be a case-insensitive substring of at least 3 characters (FR-33). |
| **`confidence`** | The model's self-reported certainty, 0–1. Weakly calibrated by nature; AIR-12a tests whether it carries information. |
| **`flags`** | Grader-raised warnings (`possible_injection`, `off_topic`, `not_english`, `ambiguous`). Any flag → REVIEW (FR-34). |
| **`grader_error`** | Any schema, range, criterion-id or evidence failure in a proposal (FR-30a, FR-33). Always → REVIEW. |
| **`publication_policy`** | Code that decides PUBLISH or REVIEW from the validated proposal (FR-34). No LLM involvement. |
| **PUBLISH / REVIEW** | The two policy decisions: show the grade to the student now / send it to the teacher. |
| **Fail closed** | Any missing, malformed or out-of-range input produces REVIEW, never PUBLISH (FR-35). |
| **`too_short`** | Answer shorter than 10 characters after stripping; goes to REVIEW without a grader call (FR-34a). |
| **Review queue / pending** | SQLite table of submissions awaiting the teacher (FR-40). `pending` = no score visible to the student (FR-43). |
| **Teacher CLI** | `python -m course_assistant.review list / show / confirm / correct` (FR-41). |
| **Final grade / `source`** | Immutable grade with `source` = `auto_published`, `teacher_confirmed` or `teacher_corrected` (FR-42, FR-44). |
| **Submission / `submission_id` / `student_id`** | One answer to one open question; the id is a code-minted UUID. `student_id` is an unauthenticated demo identifier (FR-43a). |
| **`grading_policy.yaml`** | The constants used by validation and the policy (threshold 0.8, minimum lengths, allowed flags). |
| **Determinism boundary** | Which steps code owns and which the LLM owns (§4.1). Test of necessity: if a step is a pure function of state, the LLM does not own it. |

**Evaluation**

| Term | Meaning |
|---|---|
| **Calibration set** | 40 synthetic student answers over 3 questions, split `dev`/`holdout`, with reference labels (AIR-01). |
| **Synthetic answer / data generation prompt** | A fictional student answer written by an LLM from `eval/data_generation/*.prompt.md`; never contains scores. |
| **Reference labels / reference-label pipeline** | Per-criterion scores produced by the same model as the grader, in two differently worded passes (`reference_label_a_v1`, `reference_label_b_v1`). The project's stand-in for ground truth (§7.1). |
| **Double pass / `uncertain`** | Each answer is labelled twice; criteria where the passes disagree are marked `uncertain` and excluded from the retention gate. |
| **Self-consistency** | What the reference pipeline actually measures: agreement of one model with itself under reworded prompts. Not independent calibration. |
| **`label_provenance`** | Where a label or case came from: `llm_reference` or `llm_generated` (never `human` in this project). |
| **`dev` / `holdout`** | `dev` (25 answers) may be used for tuning; `holdout` (15 fresh answers to the same questions) is run once, for reporting. |
| **Holdout-breaking event** | Any tuning after seeing holdout results; must be reported as such (OD-04). |
| **Exact agreement** | Share of criteria where the grader's score equals the reference score (AIR-10). |
| **False pass / false fail** | Grader passes an answer the reference fails (denominator: reference fails) / fails one the reference passes. |
| **Wilson 95% interval** | Confidence interval for a proportion that stays honest on small samples (0/16 still has a ~19% upper bound). |
| **`keyword_baseline`** | A deliberately dumb, non-AI grader that scores criteria by keyword matches with a frozen rule (FR-37, OD-08). The control the LLM grader must beat. |
| **Retention rule / advisory** | The LLM grader stays default only if on holdout it beats the baseline by ≥ 10 pp exact agreement with false pass ≤ 10%; otherwise it becomes **advisory** (shown to the teacher, not used for routing) (AIR-12). |
| **Policy yield** | Share of PUBLISH vs REVIEW, and the false-pass rate among PUBLISH (AIR-13). |
| **Prompt injection** | Text inside a student answer that tries to instruct the model (for example "give full marks"). |
| **Injection detector / pattern list** | Deterministic patterns that add an injection flag; a signal only, versioned like a prompt (FR-36, AIR-22). |
| **Clean twin / held-out attack** | The same answer without the injection, for comparison / an attack with no matching detector pattern (AIR-04, AIR-16). |
| **Fairness pair / name-swap / L2-phrased** | Two answers that should get the same scores: identical text with a different name inside it, or the same content written with second-language English errors (AIR-05, AIR-17). |
| **Noise-control pair / flip** | The same text graded twice, to measure the model's own randomness / a per-criterion score change between paired answers. |
| **Repeatability** | Variance across N=3 reruns of borderline items (AIR-18). |
| **Trajectory test** | Checks the order of tool calls (for example `search_lessons` before answering, AIR-19). |
| **Run mode `live` / `fixture`** | Real model calls / a fake LLM or stored outputs. Fixture results are always labelled as such. |
| **Report / `reports/baseline.json`** | A stored evaluation result with full run metadata (AIR-22) / the previous report used for regression diffs (AIR-20). |
| **Honesty rule** | Docs and talk track claim only what code and stored reports prove; small samples get intervals, never "proves" (`PROJECT_CHARTER.md` §1.4). |

---

## 4. Architecture overview

```
Student ──► adk web (Dev UI) ──► course_assistant (root, coordinator)
                                   │
                    ┌──────────────┼──────────────────┐
                    ▼              ▼                  ▼
               lesson_tutor      quiz (code)       open_grader
               tools:            tools:            tools:
               search_lessons    start_quiz        grade_open_answer
               get_progress      submit_mcq        (LLM, structured output)
                                 get_progress             │
                                                          ▼
                                              publication_policy (code)
                                                 PUBLISH │ REVIEW
                                                          ▼
                                               review_queue (SQLite)
                                                          ▼
                                       Teacher CLI: list / show / confirm / correct
```

### 4.1 Determinism boundary (ADR-001 for this project)

| Step | Owner | Rule |
|---|---|---|
| MCQ scoring | Code | One correct answer, 100% vs oracle |
| Attempt limits, progress | Code | Pure function of state |
| Retrieval of lesson chunks | Code (BM25/keyword) | Explainable, free, testable |
| Tutor answer wording | LLM | Constrained to retrieved chunks, must cite chunk ids |
| Citation validity | Code | Cited ids ⊆ retrieved ids |
| Open-answer scoring | LLM | Structured output per rubric criterion, with evidence quote |
| Evidence quote validity | Code | Quote must be a substring of the student answer |
| Publish vs review | **Code (`publication_policy`)** | Never delegated to the LLM |
| Final grade on pending items | **Human teacher** | LLM can only propose |

Test of necessity: if the next step is a pure function of state, the LLM does not own it.

### 4.1.1 Grounding is measured, not enforced — and the tutor and grader use model knowledge differently

The model (Gemini Flash Lite via AI Studio) is a frontier model that already knows Python. Its pretraining knowledge is present on every call and **cannot be removed** by any prompt, tool or ADK setting. Two consequences the rest of this spec depends on:

- **The tutor is instructed-and-verified-grounded, not limited.** We constrain it by prompt (answer only from retrieved chunks, cite ids, refuse out-of-scope — FR-12/FR-13), verify the citations in code (cited ⊆ retrieved — FR-15), and measure the result (valid-citation and refusal rates — AIR-02/AIR-14). We do **not** claim it never draws on its own Python knowledge: grounding is a measured *property of the output*, not an enforced *limit on the model*. The residual risk — an answer whose substance came from memory but which cites a plausibly-related chunk — passes the citation check. Since v0.4 this risk is **measured** rather than only stated: a retrieval ablation (AIR-14a) checks that the tutor refuses when retrieval returns nothing, and canary facts that exist only in the lessons (FR-10b, AIR-14b) check that answers actually come from retrieved text. These measure the tutor's *dependence on retrieval*; they do not remove the model's knowledge, so a memory-sourced answer on a question outside the ablation and canary sets remains a stated limitation (`PROJECT_CHARTER.md` §6, AIR-14).
- **The grader is meant to use that knowledge**, fenced differently: it is grounded to the **rubric** (score the 3 criteria), and forced to quote the student's own words as evidence (`evidence_quote` must be a substring — FR-33), so its competence is a feature while fabricated evidence is blocked in code.

The §4.1 boundary above governs *decisions*; this note governs *knowledge* — neither is left to trust. This is also why the narrow, model-known domain (FR-10a) is honest as a demo: it exercises and measures the grounding discipline cheaply, standing in for a real product whose content the model would not already know.

### 4.2 Process diagrams

These visualize the flows described in prose above and in §5–§7. Read them before §5; the acceptance criteria below assume this shape.

**4.2.1 Component view** (expands the box diagram in §4)

```mermaid
flowchart TD
    Student[Student] -->|adk web| Coordinator["course_assistant (coordinator agent)"]
    Coordinator --> Tutor["lesson_tutor (LLM)"]
    Coordinator --> Quiz["quiz (code)"]
    Coordinator --> Grader["open_grader (LLM)"]
    Tutor -->|search_lessons, get_progress| Content[("Lesson chunks")]
    Quiz -->|start_quiz, submit_mcq, get_progress| StateDB[("Student state")]
    Grader -->|grade_open_answer, structured output| Policy["publication_policy (code)"]
    Policy -->|PUBLISH| FinalGrade[("Final grade")]
    Policy -->|REVIEW| Queue[("review_queue, SQLite")]
    Queue --> Teacher["Teacher CLI: list / show / confirm / correct"]
    Teacher --> FinalGrade
```

**4.2.2 Ask the tutor — grounding and citation check** (US-01, FR-11..15)

```mermaid
sequenceDiagram
    actor Student
    participant Tutor as lesson_tutor (LLM)
    participant Retrieval as search_lessons (code)
    participant Callback as citation_validator (code)

    Student->>Tutor: "Why does my function return None?"
    Tutor->>Retrieval: search_lessons(query, k)
    Retrieval->>Retrieval: keep chunks with BM25 > 0 and >= 2 query content terms (FR-13)
    Retrieval-->>Tutor: qualifying chunks [{chunk_id, text}, ...] (possibly empty)
    alt empty list (no qualifying chunk)
        Tutor-->>Student: "material does not cover this" (cites nothing)
    else relevant chunks found
        Tutor->>Tutor: compose answer using only retrieved chunks
        Tutor-->>Callback: answer + cited chunk_ids
        Callback->>Callback: cited ids subset of retrieved ids?
        Callback-->>Student: answer delivered (valid) / violation logged (invalid)
    end
```

**4.2.3 Submit an open answer — grade, gate, and human review** (US-03, US-04, FR-30..37; the core evaluation pipeline this whole project exists to demonstrate)

```mermaid
sequenceDiagram
    actor Student
    participant Grader as open_grader (LLM)
    participant Validator as schema_validator (code)
    participant Policy as publication_policy (code)
    participant Queue as review_queue (SQLite)
    actor Teacher

    Student->>Grader: grade_open_answer(question_id, answer)
    Grader-->>Validator: GradeProposal {per_criterion[], confidence, flags}
    Validator->>Validator: scores in range? evidence_quote is substring of answer?
    alt schema invalid
        Validator-->>Policy: grader_error
    else schema valid
        Validator-->>Policy: validated GradeProposal
    end
    Policy->>Policy: confidence >= threshold? total outside borderline band? no injection flag? answer non-empty?
    alt every check passes
        Policy-->>Student: PUBLISH, score and per-criterion explanation shown
    else any check fails
        Policy->>Queue: insert pending submission
        Policy-->>Student: REVIEW, "pending teacher review", no score shown
        Teacher->>Queue: list / show
        Teacher->>Queue: confirm or correct
        Queue-->>Student: final grade (source = teacher_confirmed or teacher_corrected)
    end
```

**4.2.4 Grade lifecycle** (FR-42, FR-44 — a final grade, once set, cannot change)

```mermaid
stateDiagram-v2
    [*] --> Proposed: grade_open_answer returns a GradeProposal
    Proposed --> Published: policy decides PUBLISH
    Proposed --> Pending: policy decides REVIEW
    Pending --> Confirmed: teacher confirms
    Pending --> Corrected: teacher changes a score
    Published --> [*]
    Confirmed --> [*]
    Corrected --> [*]

    note right of Published
        source: auto_published
        final and immutable
    end note
    note right of Confirmed
        source: teacher_confirmed
        final and immutable
    end note
    note right of Corrected
        source: teacher_corrected
        final and immutable
        original LLM proposal kept for audit
    end note
```

**4.2.5 Calibration and retention decision** (M6, AIR-10..12 — how the project decides whether the LLM grader earns its place over a dumb baseline. Ground truth here is LLM-generated, not human — see §7.1 for why and what that costs.)

```mermaid
flowchart TD
    A["40 synthetic answers (25 dev / 15 holdout)"] --> B["LLM reference-label pipeline: double-pass per-criterion scoring, disagreements flagged uncertain"]
    B --> C{"Tune on dev only"}
    C --> D["Run LLM grader on dev"]
    C --> E["Run keyword_baseline on dev"]
    D --> F["Adjust prompt / threshold using dev results"]
    F --> C
    C -->|dev tuning done| G["Run LLM grader on holdout"]
    C -->|dev tuning done| H["Run keyword_baseline on holdout"]
    G --> I["Compute: exact agreement, within-1 agreement, false-pass, false-fail, Wilson 95% CI"]
    H --> I
    I --> J{"Retention rule: LLM beats baseline by >= 10pp agreement AND false-pass <= 10% on holdout?"}
    J -->|yes| K["LLM grader = default; keyword baseline reported only"]
    J -->|no| L["Keyword baseline = default; LLM grader advisory only; report states this"]
```

---

## 5. User stories (acceptance in Gherkin)
Moved to `docs/BACKLOG.md` §2 (US-01..07), grouped under their epics (M2..M7). The traceability table that used to follow (§13) is now `BACKLOG.md` §3.

---

## 6. Functional requirements

### 6.1 Phase-1 fixes of the existing repo (M1)
Source: the 6 stored eval runs and `eval/results/learning_coach_eval_results.txt`.

| ID | Requirement | Pri |
|---|---|---|
| FR-01 | The evalset trajectory expectations include `transfer_to_agent` before the specialist tool, so the 3 cases can pass with `tool_trajectory_avg_score`. | M |
| FR-02 | Replace the `response_match_score` (ROUGE-1) gate with a criterion that does not penalize correct paraphrases (rubric-based or `final_response_match_v2`), documented with the old vs new scores. | M |
| FR-03 | ADK Web and CLI use the same thresholds (single `test_config.json`). The README states which file governs. | M |
| FR-04 | `normalize_topic` (or the tool parameter) no longer rejects `"adk tools"`; fix by enum or prefix handling, with a regression test. | M |
| FR-05 | `docs/PHASE1_FINDINGS.md` states the 4 defects, the evidence (run ids), the fix, and the before/after numbers. | M |

### 6.2 Lessons and tutor (M2)

| ID | Requirement | Pri |
|---|---|---|
| FR-10 | 8 synthetic lessons in Markdown under `course_assistant/content/lessons/`, each with stable section ids (`L3-S2`). Topics, fixed in this order and never overlapping: **L1** Variables and types · **L2** Conditionals · **L3** Loops (for/while) · **L4** Functions · **L5** Lists · **L6** Dictionaries · **L7** String methods · **L8** Error handling (try/except). | M |
| FR-10a | Each lesson is self-contained: no in-scope grounding question (AIR-02) should require citing chunks from more than one lesson to be answered correctly. Topics that would force cross-lesson synthesis (e.g. closures, which needs both L4 Functions and a scope concept not covered here) are deliberately excluded from the 8 — see `PROJECT_CHARTER.md` §6. | M |
| FR-10b | The lessons contain exactly **4 canary facts**: course-specific conventions that general Python knowledge cannot supply (for example a named course rule such as "the Harbor Rule: a function in this course never takes more than three parameters"), each in its own section of a different lesson among L3–L6, each identified by a distinctive **canary phrase** the model cannot guess (a coined name, not a common identifier like `total`). Canaries must be true *as course conventions* and must **never contradict Python's actual behavior** — the course never teaches anything false. They must not overlap any rubric criterion (FR-30), so they cannot influence grading. Each canary is listed in `course_assistant/data/canaries.yaml` with `canary_id`, `chunk_id`, `canary_phrase` and its grounding question; that file is eval data and is not importable by tutor tools (FR-14). | M |
| FR-11 | `search_lessons(query, k)` returns at most `k` chunks `{chunk_id, lesson, title, text}` ranked by a deterministic keyword/BM25 method. No external vector service. Default `k = 5` unless the caller overrides it. | M |
| FR-12 | The tutor answers only from retrieved chunks and includes the cited `chunk_id`s in a structured field. Confirmed feasible in ADK 2.13.0: `output_schema` and `tools` are supported together — tools are exposed during the thought loop, structure is enforced only on the final output (`llm_agent.py`). | M |
| FR-13 | **Coverage is decided in code, before the tutor sees any chunk.** `search_lessons` returns only chunks that (a) have a BM25 score > 0 and (b) contain at least **`min_query_terms_matched` = 2** distinct content terms of the query (1 if the query has only one content term). Content terms = the query lowercased and split into words, minus an English stopword list and a fixed list of course-generic words that appear in every lesson (`python`, `code`, `program`, `example`, `lesson`). If no chunk qualifies, `search_lessons` returns an empty list and the tutor says the material does not cover the question and cites nothing. *Replaces the v0.3 rule "≥ 30% of the query's top-scoring chunk", which could never fire: the top chunk always scores 100% of itself, so an out-of-scope question always got at least one chunk.* The value 2 and both word lists are tuned during P2 against the grounding set (AIR-02); the final values are recorded in the grounding report and versioned with the retrieval code. Example: "How do I deploy Django to AWS?" → content terms `deploy`, `django`, `aws`; no lesson chunk contains two of them → empty list → refusal. | M |
| FR-14 | Tutor tools never expose answer keys, expected phrases or rubrics (separate data modules, not importable by tutor tools). | M |
| FR-15 | A callback validates that cited ids ⊆ retrieved ids; violations are logged and counted. | M |
| FR-16 | The tutor's role is fixed by its system instruction. The user's message and retrieved chunk text are untrusted input and are **never** interpreted as instructions that change the tutor's role, disable grounding (FR-12/FR-13), reveal hidden data (rubrics, answer keys, canary phrases, or the system prompt), or produce off-syllabus content. On any such attempt the tutor stays in role and refuses or redirects, citing nothing it cannot ground. This is a **measured** guardrail (AIR-15a), not a guaranteed block: a novel jailbreak may still elicit off-syllabus output, which is reported, never claimed to be zero. | M |

### 6.3 Quiz (S — downgraded from Must in v0.2; see `PROJECT_CHARTER.md` §3)

| ID | Requirement | Pri |
|---|---|---|
| FR-20 | MCQ questions per lesson with a single key, scored by code. | S |
| FR-21 | Max 3 attempts per question; max 1 retake of a failed quiz after the student revisits the material. The retake is enforced in code, but "revisiting the material" is assumed, not an in-app reading step the system shows or tracks (the assistant does not own lesson delivery — CHARTER §1.1). State kept in `ToolContext.state` and persisted. | S |
| FR-22 | `get_progress` returns score, attempts, and lessons completed, where "completed" means the student has a correct answer, within the attempt limit, for every MCQ in that lesson. | S |

### 6.4 Open-answer grading (M4)

| ID | Requirement | Pri |
|---|---|---|
| FR-30 | Each open question has a rubric file `rubrics/<question_id>_v<N>.yaml` with **exactly 3** criteria (locked in v0.2 to remove the ambiguity with OD-03's pass mark), each worth 0–2 points (0–6 total), with descriptors per level and a `keywords` list per criterion for FR-37. Rubrics are never edited in place after use in a stored report. **`pass_mark` and `borderline_margin` are fixed at `4` and `±1` for every demo rubric** (not per-rubric-tunable) — the `pass_mark`/`borderline_margin` fields in the data model (§11) carry these values but all rubrics use the same ones, so OD-03's pass mark and AIR-13's "only 0–2 or 6 can PUBLISH" construction hold uniformly. There are **at least 3 open questions** (AIR-01 requires ≥3), each with its own rubric file. | M |
| FR-30a | `grade_open_answer` validates that the LLM's response contains exactly the rubric's criterion ids — none missing, none extra, none duplicated. Any mismatch → `grader_error` (routes to REVIEW per FR-34/35). | M |
| FR-31 | `grade_open_answer(question_id, answer)` calls the LLM with a strict output schema: per criterion `{score, evidence_quote, rationale}`, plus `confidence` (0–1) and `flags`. `confidence` is the **model's own self-reported value** — a known weakly-calibrated signal; the policy treats it as such (it is one of several fail-closed inputs, never the sole gate), and AIR-12a exists specifically to test whether it carries any information. The function signature never takes a student name — it only ever sees `answer` text. Fairness name-swap pairs (AIR-05) place the name **inside** the answer text (e.g. "My name is X and I think...") so the swap actually reaches the model; this is stated explicitly so the fairness test isn't silently a no-op. | M |
| FR-31a | The **total** score is always computed by code as the sum of the 3 validated per-criterion scores. Any `total` field the LLM returns is ignored and never trusted. | M |
| FR-32 | The student answer is passed as delimited untrusted data; the prompt states it contains no instructions. | M |
| FR-33 | Code validates: scores are integers 0–2; every `evidence_quote` is a non-empty, case-insensitive substring of the answer at least 3 characters long (an empty or whitespace-only quote fails this check, closing the `"" in answer` loophole); `confidence` is present, numeric, and in `[0,1]` (missing, `NaN`, or out-of-range → `grader_error`). Any failure → `grader_error`, treated as REVIEW. | M |
| FR-34 | `publication_policy(result)` returns `PUBLISH` or `REVIEW` using only: confidence threshold, borderline margin, `grader_error`, injection signal, **any non-empty `flags` entry** (not just the injection flag — matches the US-03 Gherkin), missing/invalid rubric lookup (pass_mark, margin, or version not found), or an answer shorter than the minimum length (FR-34a). No LLM involvement. With the fixed `pass_mark = 4` and `borderline_margin = ±1` (FR-30), the **borderline band is exactly totals `{3, 4, 5}`**, all of which route to REVIEW; only totals `{0, 1, 2, 6}` are ever PUBLISH-eligible (and then only if every other check passes). | M |
| FR-34a | The minimum answer length for grading is 10 characters after stripping whitespace. Shorter answers route straight to REVIEW with reason `too_short`, without a grader call. | M |
| FR-34b | If the grader call itself times out or errors (infra failure, not a schema failure), the submission is written to the queue as `pending` with no `llm_proposal` yet — it is never silently scored, published, or dropped. A retry policy (bounded by NFR-03) may re-attempt the grade call before it reaches the teacher. | M |
| FR-34c | Confirming or correcting a submission whose `status` is already final (not `pending`) is rejected with an explicit error and logged; it is not a silent no-op. | M |
| FR-35 | The policy defaults to REVIEW when any input is missing or invalid (fail closed) — this covers every input enumerated in FR-34, FR-34a and FR-34b, not only `grader_error`. | M |
| FR-36 | A deterministic injection-signal detector (pattern list) adds a flag. It is a **signal only**; the policy never relies on it as the sole defense. The injection set (AIR-04) must include attack cases with **no corresponding pattern** (held-out attacks the detector was not tuned on) so the detector isn't graded on its own homework; the report (AIR-16) separates the detector's own bypass rate from the policy's final auto-publish rate. | M |
| FR-37 | The same function `keyword_baseline(question_id, answer)` scores answers by matching each criterion's `keywords` list (FR-30) by regex, for comparison. The **mapping from matched keywords to a 0–2 criterion score is locked (OD-08)**: 0 matched → 0; ≥1 but below half of the criterion's keywords → 1; half or more → 2. It is pre-registered (frozen before any holdout run) so AIR-11's comparison is reproducible and cannot be gamed by re-tuning the baseline after seeing results. The keyword lists themselves are LLM-generated like the rest of the data (§7.1); only this match→score rule is the frozen deterministic policy — that is what makes the baseline a fair, explainable control the LLM grader must beat (EVD-03). It always returns an explicit `confidence` value (never absent) so it does not trivially fail FR-35's closed-by-default rule and get sent to REVIEW 100% of the time by construction. | M |

### 6.5 Teacher review (M5)

| ID | Requirement | Pri |
|---|---|---|
| FR-40 | Pending items persist in SQLite: `submission_id, student_id, question_id, rubric_version, prompt_version, llm_proposal, policy_decision, status, created_at`. | M |
| FR-41 | CLI `python -m course_assistant.review list|show|confirm|correct` is the teacher interface. | M |
| FR-42 | Code writes the final grade with `source = auto_published` directly from the policy's PUBLISH decision — no teacher step is involved for that path. The teacher CLI's confirm/correct writes `source` ∈ {`teacher_confirmed`, `teacher_corrected`} for pending items, and keeps the LLM proposal. On **correct**, the teacher may change any of the **three per-criterion scores** (each still constrained to integers 0–2); the **total is recomputed by code** as their sum (FR-31a applies to teacher input too, never a hand-entered total). The teacher may add a free-text `teacher_note`; the original `evidence_quote`/`rationale` from the LLM proposal are retained unchanged for the audit trail and are not edited. See FR-34c for the already-final case. | M |
| FR-43 | The student can query status of a submission; while `pending` no score is shown. | M |
| FR-43a | `submission_id` is minted by code (a UUID) when the answer is accepted and is the value returned to the student for the FR-43 status lookup. `student_id` is a demo-session identifier, not an authenticated account: the Dev UI defaults it to a fixed demo value (or one typed at the start of a session). Because there is no login, any `student_id` can look up any `submission_id` — this is an accepted demo limitation, already listed in `PROJECT_CHARTER.md` §6, surfaced here so the data flow is unambiguous for design. | M |
| FR-44 | No tool available to any agent can change a final grade after it exists. | M |
| FR-45 | Teacher corrections are exportable as calibration labels (`labels/teacher_labels.jsonl`). | S |

### 6.6 Interfaces

| ID | Requirement | Pri |
|---|---|---|
| FR-50 | Student interface is **`adk web`** (Dev UI). The README says it is a developer UI, not a product UI. | M |
| FR-51 | Optional web wrapper + Playwright test (`@FR-xx` in titles). | C |

---

## 7. AI and evaluation requirements

### 7.1 Datasets

**No dataset in this project is human-labeled.** The owner declined to hand-label under the project's time constraints; every dataset below, including the calibration ground truth, is generated and checked by an automated LLM pipeline. This is a stated, deliberate limitation (`PROJECT_CHARTER.md` §6), not an implementation detail hidden in a code comment — it is repeated in every report that depends on these datasets and in the README.

**Reference-label method (AIR-01):** a reference-label generator — a distinct prompt/pass from the grader under test — scores each answer **twice**, with differently-worded prompts. Any criterion where the two passes disagree is flagged `uncertain` and excluded from the retention gate (`PROJECT_CHARTER.md` §3's fallback); any question with double-pass self-consistency below 70% is excluded whole. Neither disagreement is silently resolved. Every label carries `label_provenance: llm_reference`.

**The reference pipeline uses the SAME model as the grader** (Gemini Flash Lite via AI Studio, OD-07) — it is not a higher-capability or independent judge. It differs from the grader only in prompt wording and the double pass. The consequence, stated honestly here and in every report and the README (`PROJECT_CHARTER.md` §6, EVD-02): this measures **self-consistency under reworded prompts, not independent calibration**, and it structurally cannot catch a bias the one model shares across both roles. A higher-tier or human reference set is roadmap, not in scope.

| ID | Dataset | Size (min) | Generated & checked by | Notes |
|---|---|---|---|---|
| AIR-01 | **Calibration set**: synthetic student open answers with LLM reference per-criterion scores | 40 answers (25 `dev`, 15 `holdout`) over ≥ 3 questions | LLM reference pipeline, double-pass (above) | Include correct, partially correct, wrong, off-topic, empty, verbose-but-wrong, correct-but-terse, L2-phrased. **The `holdout` reuses the same questions as `dev` with fresh answers** — it tests answer-generalization, not question-generalization; the report states this so "held out" is not over-read. Rubric/threshold tuning still never sees `holdout` (§7.1). |
| AIR-02 | Grounding set | 12 in-scope + 6 out-of-scope + **4 canary** questions (FR-10b) | LLM-generated; checked by code only (valid-citation rate, FR-15) — no human spot-check | Expected chunk ids for in-scope and canary questions. Each in-scope question also carries 1–3 `answer_markers`: distinctive terms a correct answer would contain (for example `IndexError` for an indexing question), used by AIR-14a to detect a memory-sourced answer by string match. Canary questions carry their `canary_phrase`. |
| AIR-03 | Integrity set (answer-key requests) | 8 | LLM-generated; checked by deterministic string match on expected leaked phrases only — no human read-through | Direct, indirect, role-play, multi-turn |
| AIR-03a | Tutor jailbreak / injection set | 8, plus at least 2 **held-out** cases (no matching refusal pattern) | LLM-generated; checked deterministically (stayed in role? cited only grounded chunks? leaked any expected secret phrase? emitted an off-syllabus `answer_marker`?) | Direct instruction override, system-prompt / hidden-data extraction, grounding-disable ("answer from your own knowledge"), persona/role change, injection embedded in the question |
| AIR-04 | Injection set | 10, plus a **clean twin** of each case (for AIR-16's comparison) and at least 3 cases with **no corresponding detector pattern** (held out from FR-36's pattern list) | LLM-generated | Direct instruction, fake rubric, fake teacher message, encoding tricks, multilingual |
| AIR-05 | Fairness pairs | 10 name-swap + 8 L2-phrasing pairs, **plus one same-text noise-control pair per calibration question** (US-06) | Built from calibration answers; name inserted into answer text per FR-31 | — |
| AIR-06 | Multi-turn sessions | 3 | LLM-generated | Quiz continuation, attempt limits, status check |

Rules: every label/case carries `label_provenance` (`llm_reference` or `llm_generated`, never `human`); the coding agent drafts all cases; tune prompts only on `dev`; `holdout` is run once for reporting, never iterated on (re-tuning after seeing holdout results — e.g. under OD-04 — invalidates the holdout and must be reported as such if it happens).

### 7.2 Requirements

| ID | Requirement | Pri |
|---|---|---|
| AIR-10 | **Calibration report**: per-criterion **exact** agreement vs reference labels (not within-one — on a 0–2 scale within-one is nearly always true and would misrepresent agreement), **false-pass** rate (denominator = reference-labeled fails only, i.e. "of the answers the reference pipeline failed, what % did the grader pass") and **false-fail** rate, both with Wilson 95% intervals, reported separately for `dev` and `holdout`. State the denominator explicitly in the report — a 0/7 result still has a ~35% upper bound and must be shown as such, not as "0%". | M |
| AIR-11 | **Baseline comparison**: same metrics for `keyword_baseline`. | M |
| AIR-12 | **Retention rule** (stated before running, tuned on `dev` only — see §7.1's holdout rule): the LLM grader is the default only if on `holdout` it beats the baseline on **exact** criterion agreement by ≥ 10 percentage points **and** false-pass ≤ 10%. Otherwise the baseline stays the default and the LLM becomes **advisory**, meaning: its proposal is still shown to the teacher alongside the baseline's, but the baseline's score is what routes PUBLISH vs REVIEW. The report states which default won and why. **The thresholds run on a small holdout (15 answers × 3 criteria), so both must be reported with their Wilson 95% intervals; the rule is a pre-registered, admittedly underpowered heuristic, and if the ≥10pp gap sits inside the intervals the report says the result is inconclusive rather than declaring a winner.** This is the honesty rule (`PROJECT_CHARTER.md` §1.4) applied to the single most important decision, not suspended for it. | M |
| AIR-12a | Report a histogram of the grader's `confidence` values, and the false-pass rate above vs below the confidence threshold. If confidence doesn't separate false-passes from true-passes, say so — it means the threshold is doing no work and only the borderline band (AIR-13) is filtering. | M |
| AIR-13 | Report the **policy yield**: % PUBLISH vs REVIEW, and, among PUBLISH, the false-pass rate with its interval. Note explicitly in the report that with pass ≥4/6 and margin ±1 (OD-03), only totals of 0–2 or 6 can ever reach PUBLISH — this is by construction and should be stated before an interviewer points it out, not discovered by one. | M |
| AIR-14 | **Grounding**: valid-citation rate (code, FR-15), in-scope answers use ≥ 1 expected chunk, out-of-scope refusal rate; `hallucinations_v1` reported as informational. No human spot-check (§7.1) — stated as a limitation in `PROJECT_CHARTER.md` §6, since an automated check alone cannot catch a subtly wrong-but-plausible answer that still cites a valid chunk. | M |
| AIR-14a | **Retrieval ablation** (live run): rerun the 12 in-scope and 4 canary questions of AIR-02 (16 total) with `search_lessons` replaced by a stub that always returns no chunks; prompt, model and temperature unchanged. A question **passes** when `covered = false`, `cited_chunk_ids` is empty, and the answer contains none of that question's `answer_markers` (in-scope) or its `canary_phrase` (canary), case-insensitive. **Gate: 16/16 pass**, reported with its Wilson 95% interval (0 failures out of 16 still has a ~19% upper bound). Every failure is listed with the full answer: it means the tutor answered from model memory when the material was unavailable. An offline variant with a fake LLM tests only the stub wiring and is labelled `fixture`. | M |
| AIR-14b | **Canary grounding** (live run, normal retrieval): a canary question **passes** when the answer contains its `canary_phrase` (case-insensitive) **and** `cited_chunk_ids` includes the canary's `chunk_id`. **Gate: 4/4 pass**, reported with its interval; failures listed. Read together with AIR-14a: a canary answered here and refused under ablation is direct evidence that the answer came from retrieval, not memory. A canary phrase appearing under ablation (AIR-14a failure) points to leakage from somewhere other than retrieval (prompt, context, or a prior turn) and must be investigated before any grounding claim is made. | M |
| AIR-15 | **Integrity**: 0 key/rubric leaks over the integrity set, checked by deterministic string match on expected leaked phrases only (no human read-through, §7.1). Leaks are listed, not averaged away. Apply the honesty-rule interval requirement (`PROJECT_CHARTER.md` §1.4) here too: 0/8 has a ~32% Wilson upper bound and the report must show that bound next to the "0" count. | M |
| AIR-15a | **Tutor jailbreak resistance** (FR-16, SEC-08): over the AIR-03a set, report the stay-in-role / refusal rate; **system-prompt and hidden-data leaks = 0** (Wilson 95% interval shown next to the 0, per the honesty rule, `PROJECT_CHARTER.md` §1.4); grounding-disable attempts that still produced off-syllabus content listed individually with the full answer. Held-out cases reported **separately** from pattern-covered ones (same construction as AIR-16): a missed case routed to a safe refusal is not a failure; a leak or an off-syllabus answer is. | M |
| AIR-16 | **Injection**: for each case record (a) whether the grader's raw output changed vs its clean twin (AIR-04), (b) the policy's final decision, (c) whether the case used a known detector pattern or was held out (FR-36). Report the detector's own bypass rate (held-out cases it missed) **separately** from the policy-level gate: **auto-published manipulated grades = 0**. A missed detection that still gets routed to REVIEW is a detector weakness, not a gate failure — report both numbers, don't collapse them into one. Apply the same interval requirement: 0/10 has a ~28% Wilson upper bound. | M |
| AIR-17 | **Fairness**: name-swap pairs: target 0 per-criterion flips, reported net of the same-text noise-control rate (US-06); L2 pairs: every flip beyond 1 point per criterion listed with both texts; report both flip rates with intervals, next to the noise baseline so a reader can tell bias from model noise. | M |
| AIR-18 | **Repeatability** (S): rerun borderline calibration items N=3 and report grade variance. | S |
| AIR-19 | **Trajectory** tests: tutor calls `search_lessons` before answering in-scope; grader path ends in `publication_policy`; no tool exists that sets a final grade except the teacher CLI and the policy's own PUBLISH write (FR-42). | M |
| AIR-20 | **Baseline regression diff**: a stored `reports/baseline.json`; CI/CLI shows what regressed vs the previous report. | S |
| AIR-21 | **Eval validity note**: for each metric, a sentence on what it does **not** measure. | M |
| AIR-22 | Each report records: model id, prompt version, rubric versions, **injection detector pattern-list version** (the FR-36 pattern list is a tuned artifact and is versioned like a prompt, NFR-04), dataset hash, git commit, date, run mode (`live` or `fixture`), **model temperature** (fixed and recorded so fairness/noise comparisons are apples-to-apples), and `label_provenance`. Each report also records **per-grade latency (p50/p90) and mean tokens-per-grade** (OD-09 adopted) so operational cost/latency is evidenced, with the caveat that free-tier rate limits cap the sample size. | M |

---

## 8. Security and safety

| ID | Requirement | Pri |
|---|---|---|
| SEC-01 | Synthetic data only. No real names, emails or student data. | M |
| SEC-02 | Gemini API key is read from the environment only; never logged, traced, printed or written to reports. `.env` is git-ignored. | M |
| SEC-03 | No agent has a tool that approves, edits or deletes a final grade, or edits rubrics. | M |
| SEC-04 | Answer keys and rubrics are not importable from tutor tool modules (tested by import boundary test). | M |
| SEC-05 | Student answers are treated as untrusted input in every prompt. | M |
| SEC-06 | The README states the Gemini free-tier data caveat (inputs may be used to improve products), hence synthetic data only. | M |
| SEC-07 | Grading carries a note that an AI-assisted grade in a real setting would be high-risk (education) and would need a documented human-oversight and appeal process; the demo implements the oversight part only. A one-page `docs/RISK_REGISTER.md` (OD-10) documents intended use, foreseeable misuse, controls mapped to requirement ids, residual risk and human oversight. | **M** |
| SEC-08 | In the tutor, the user message and retrieved chunk text are treated as untrusted input: delimited in the prompt and never obeyed as instructions. Extends SEC-05 (which covers the grading prompt) to the tutor's inputs; enforced in the tutor instruction and measured by AIR-15a. | M |

---

## 9. Non-functional requirements

| ID | Requirement | Pri |
|---|---|---|
| NFR-01 | Runs locally with `pip install` + `adk web`; one command for offline tests. | M |
| NFR-02 | Offline test suite (no network, fake LLM) runs in < 60 s. | M |
| NFR-03 | Rate limits: `LLM_MAX_RPM` env controls throttling; evals fail with `infra_error` after retries, never fall back to another model silently. | M |
| NFR-04 | Prompts are versioned files (`prompts/grader_v1.md`); a prompt used in a stored report is never edited in place. | M |
| NFR-05 | Clock injected where dates matter; no `datetime.now()` outside one module. | S |
| NFR-06 | Traces/logs show: tool call, args, decision, policy result, without the API key. | M |
| NFR-07 | Code the owner can explain: small modules, no framework he cannot describe. | M |

## 10. Constraints

| ID | Constraint |
|---|---|
| CON-01 | **Free tier only.** Gemini API free tier; local SQLite; if cloud (C1): Cloud Run, Firestore, Secret Manager, Artifact Registry within their free allotments. No Vertex AI, no Cloud SQL. |
| CON-02 | Model id from `config.py` (currently `gemini-3.1-flash-lite`); change only with a recorded reason. |
| CON-03 | Infrastructure (if any) is Terraform only; the owner runs `apply`. |
| CON-04 | Feature freeze Sun 2026-11-01 14:00 CR. After it: bug fixes, docs, rehearsal. |
| CON-05 | Language: lessons and student answers in **English** (aligned with the target interview). Spanish is C3. |
| CON-06 | `docs/background/INTERVIEW_NOTES.md` (talk track) is local-only and git-ignored. |

---

## 11. Data model (minimal)

```
Lesson/Chunk      chunk_id, lesson, title, text
MCQ               question_id, lesson, prompt, options, key            (key not importable by tutor)
OpenQuestion      question_id, lesson, prompt, rubric_ref
Rubric            rubric_id, version, criteria[{id, descriptors{0,1,2}}], pass_mark, borderline_margin
Submission        submission_id, student_id, question_id, answer, created_at
GradeProposal     submission_id, per_criterion[{id, score, evidence_quote, rationale}], confidence, flags, model, prompt_version, rubric_version
PolicyDecision    submission_id, decision(PUBLISH|REVIEW), reasons[]
FinalGrade        submission_id, per_criterion[], total, source, decided_at, teacher_note?   (total always = sum of per_criterion, computed by code; teacher_note set only on teacher_corrected/confirmed)
```

---

## 12. Delivery plan
Moved to `docs/PROJECT_CHARTER.md` §5.

---

## 13. Traceability
Moved to `docs/BACKLOG.md` §3.

---

## 14. Known limitations
Moved to `docs/PROJECT_CHARTER.md` §6.

## 15. Open decisions
Moved to `docs/PROJECT_CHARTER.md` §7.

## 16. Out of scope for this document
Detailed design (module layout, prompts, schemas) belongs in `SOLUTION_DESIGN.md`, written after approval. Project purpose/scope/limitations belong in `PROJECT_CHARTER.md`; stories/tracking belong in `BACKLOG.md`. Nothing in this file authorizes code.