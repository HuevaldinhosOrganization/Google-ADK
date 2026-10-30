# Risk Register — Course Assistant

| Field | Value |
|---|---|
| Version | 0.1 |
| Date | 2026-10-29 |
| Owner | Felipe Obando |
| Status | Draft (OD-10). Structure follows EU-AI-Act risk-documentation practice; **this is not a compliance claim** |

> This register names the ways the system can cause harm, the controls that reduce each risk (mapped to requirement ids in `SRS.md`), the risk that **remains** after those controls, and where a human stays in the loop. It is the document a delivery/services leader reads to decide whether the system is safe to use, and for what. It is deliberately honest about residual risk — see the honesty rule (`PROJECT_CHARTER.md` §1.4).

---

## 1. Intended use

A study-and-assessment aid for a narrow, self-contained 8-lesson Python-basics course (`PROJECT_CHARTER.md` §1.1). It clarifies material the student has already studied, runs deterministic quizzes, and **proposes** grades on short open answers. A human teacher confirms or corrects any grade the system is not confident about. It is a demonstration on synthetic data.

## 2. Not intended use (out of scope)

Not a real LMS; not for real students, real grades with legal effect, high-stakes certification, or any decision made without the human-review path. No authentication, no real personal data. Using it as an autonomous grader with the teacher path disabled is **outside intended use** and unsupported.

## 3. Reasonably foreseeable misuse

- Disabling or ignoring the teacher-review queue and treating auto-published grades as final for high-stakes decisions.
- Feeding real student data into a free-tier model (addressed by synthetic-only policy and the README caveat).
- Reading a single demo run's numbers as a general accuracy claim rather than an indicative result with wide intervals.
- A student embedding instructions in an answer to inflate a grade (prompt injection).

## 4. Risk table

| ID | Risk | Primary controls (→ requirement ids) | Residual risk after controls | Human oversight |
|---|---|---|---|---|
| R1 | **A wrong grade is published** (a should-fail answer passes, or vice-versa) | Policy fails closed on low confidence / borderline band {3,4,5} / errors (FR-34, FR-35); calibration vs reference labels with intervals (AIR-10); must beat a keyword baseline to stay the default (AIR-11/12) | A **confidently-wrong** low/high grade with no flags can still auto-publish; measured as the false-pass rate with its Wilson interval, never claimed to be zero | Borderline / low-confidence grades route to the teacher before the student sees anything (FR-34, US-03) |
| R2 | **Prompt injection** in a student answer manipulates the grade | Answer passed as delimited untrusted data (FR-32); deterministic injection-signal detector adds a flag (FR-36); any flag forces REVIEW (FR-34); held-out attacks measure the detector honestly (AIR-16) | A novel attack can change the grader's raw output; the **gate-level** guarantee is that auto-published manipulated grades target **0**, reported separately from the detector's own bypass rate | Flagged / suspicious submissions go to the teacher; the detector is a first filter, not the defense |
| R3 | **Unfair grading** by name or writing style | Grader never receives a name except inside the answer text (FR-31); fairness pairs with a same-text noise control (AIR-05, AIR-17, US-06) | Only **name and phrasing** invariance is tested — not protected demographics (the domain has none); flips are reported net of model noise, with intervals | Maintainer reviews the fairness report before release; flips beyond threshold are listed, not averaged away |
| R4 | **Answer-key or rubric leak** via the tutor | Keys/rubrics not importable from tutor tool modules (SEC-04, import-boundary test); integrity set checked by string match (AIR-03, AIR-15) | A **paraphrased** leak could pass an automated string check; no human read-through (stated limitation) | Maintainer reviews the integrity report; leaks are listed individually with a Wilson upper bound next to any "0" |
| R5 | **Excessive agency** — the AI changes a final grade | Determinism boundary: publish/review is code, never the LLM (§4.1); no agent tool can set, edit or delete a final grade (FR-44, SEC-03); final grades immutable (FR-42) | None by design for the final-grade write path; verified by a test that asserts no such tool exists | The teacher is the only actor who can set a non-auto-published final grade |
| R6 | **Evaluation is self-fooling** (the judge shares the grader's bias) | dev/holdout split; no re-tuning after holdout (OD-04); double-pass self-consistency exclusion (§7.1) | The reference pipeline uses the **same model** as the grader → it measures self-consistency, not independent calibration, and cannot catch bias shared across both passes (EVD-02, `PROJECT_CHARTER.md` §6) | Roadmap: a human-labeled or higher-tier reference set |
| R7 | **Data privacy** | Synthetic data only (SEC-01); API key from environment, never logged (SEC-02); free-tier data caveat stated (SEC-06) | Demo-only; no real data ever enters the system | Maintainer enforces synthetic-only; `.env` git-ignored |
| R8 | **Tutor jailbreak** — a hostile prompt makes the tutor abandon its role (override instructions, extract the system prompt / hidden data, disable grounding and answer off-syllabus from memory, or adopt a new persona) | Fixed role in the tutor instruction; user message and chunk text are untrusted and never obeyed as instructions (FR-16, SEC-08); keys/rubrics/canaries not importable (SEC-04); cited ids ⊆ retrieved (FR-15); red-team set with held-out cases measures it honestly (AIR-03a, AIR-15a) | A **novel** jailbreak can still elicit off-syllabus content; the grounding guarantee is measured, not enforced (§4.1.1) — hidden-data leaks target **0** with a Wilson upper bound, off-syllabus outputs listed, never claimed zero | The tutor is a reference/advisory surface with no grade authority (the graded path is the one with the HITL queue); maintainer reviews the tutor jailbreak report before any claim |

## 5. Human oversight summary

The system **recommends and routes; a human decides** the grades that matter. Three oversight points:
1. **Teacher review queue** — every uncertain, borderline, or flagged grade is held for a human (FR-40–45); the student sees no score until it is resolved.
2. **Immutability + audit** — a final grade cannot be changed by any AI tool, and the original LLM proposal is kept for audit (FR-42, FR-44).
3. **Maintainer release gate** — no capability is declared "working" without its report, and CI fails if a Must requirement has no test (M10).

## 6. Residual risk statement (for any release recommendation)

The dominant residual risk is **R1 (a confidently-wrong grade auto-publishing)** and **R6 (self-fooling evaluation)**. Both are measured, reported with intervals, and bounded by the human-review path — not eliminated. Any release recommendation states the current false-pass rate with its interval and names these two residual risks explicitly.
