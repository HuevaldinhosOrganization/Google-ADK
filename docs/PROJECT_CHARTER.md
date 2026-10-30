# Project Charter — Course Assistant (tutor + graded open answers + teacher review)

| Field | Value |
|---|---|
| Version | 0.3 (aligned with SRS v0.4: retrieval ablation + canary facts) |
| Date | 2026-10-29 |
| Owner | Felipe Obando |
| Hard deadline | **Sun 2026-11-01 14:00 CR** (feature freeze). Mon–Wed = rehearsal only |
| Interview | **Confirmed:** Thu 2026-11-05 16:00–17:00 CR (1 hour) — see OD-06 |
| Status | **Approved 2026-10-29.** Code may now be written per `docs/SRS.md` |

> This file answers **why** the project exists, **who** it's for, and **what's in or out of scope**.
> For testable requirements, see `docs/SRS.md`. For epics/stories/tracking, see `docs/BACKLOG.md`.
> For module layout, prompts and schemas, see `docs/SOLUTION_DESIGN.md` (written after approval).

---

## 1. Purpose

### 1.1 Product
A small course assistant for an 8-lesson Python-basics course. **The student is assumed to have already studied the material; the assistant is a clarify-and-assess layer on top of the lessons, not a replacement for them — it does not teach the course.** A student asks a tutor questions to clarify what they studied, answers quizzes, and submits short open-ended answers. A grader scores open answers against a versioned rubric. Low-confidence or risky grades go to a human teacher before the student sees a final grade. The lesson text still lives in the system as the tutor's grounding source (FR-11, FR-15) and the basis for the rubrics; reading it in-app is optional reference, never a required or tracked step (this is a deliberate "not an LMS" choice — see §1.3).

### 1.2 Why this project exists (read this first)
This repository is the owner's **evidence** for an AI Senior SDET interview that is a conversation, not a coding exercise. Optimize for evidence the owner understands and can defend: tested, measured, explained, honest about gaps. When in doubt, choose the simpler design he can explain over the more impressive one he cannot.

The project must let him say, with artifacts:

| ID | Claim he must be able to defend | Artifact |
|---|---|---|
| EVD-01 | "I separated what code decides from what the LLM decides, and I can justify each line." | ADR-001, determinism table (SRS §4.1) |
| EVD-02 | "I built an LLM reference-label pipeline, calibrated the grader against it, and can explain exactly why that's a proxy for human judgment and not a replacement. The reference pipeline uses the **same model** as the grader (Gemini Flash Lite via AI Studio), differing only in prompt wording and a double pass — so what it measures is **self-consistency under reworded prompts, not independent calibration**. The failure mode it structurally cannot catch is any bias shared by that one model across both passes." | calibration report |
| EVD-03 | "I compared the LLM grader against a dumb baseline and kept the LLM only if it earned its place." | baseline vs LLM table |
| EVD-04 | "I tested for bias with paired inputs, not by opinion." | fairness report |
| EVD-05 | "I attacked my own grader with prompt injection and measured what leaked." | injection report |
| EVD-06 | "No LLM output can publish a final grade by itself; a human is in the loop where it matters." | policy tests + queue demo |
| EVD-07 | "I found that my first evals were wrong, and fixed them." | phase-1 write-up (existing 6 runs) |
| EVD-08 | "I can read a trace and explain why an agent did what it did." | one annotated trace |
| EVD-09 | "Every requirement maps to a test; releases are gated by evidence." | traceability table (BACKLOG.md), CI gate |
| EVD-10 | "I know what this does **not** do and what I would do next." | §6 Known limitations + roadmap |
| EVD-11 | "I red-teamed the **agent system** against jailbreaks, not just one agent: the tutor's role/hidden-data integrity is **measured** (AIR-03a/AIR-15a) and the grader's injection resistance is **measured** (EVD-05); the coordinator and the open_grader agent have no secrets or grade authority to steal — their compromise is **bounded by the determinism and import boundaries** (§4.1, SEC-03, SEC-04), not by a dataset, which I can explain rather than fake with filler coverage." | tutor jailbreak report (AIR-15a over AIR-03a; FR-16, SEC-08) + the boundary argument (SOLUTION_DESIGN §5.1) |

### 1.3 Non-goals
Not a real LMS. No authentication of real students, no real student data, no grading that has legal effect, no content generation of new exam questions, no multi-course support.

### 1.4 Honesty rule
README, reports and the talk track state only what code and stored reports prove. Results from fixtures or fake models are labelled `fixture`. Small samples are reported with intervals and never described as "proves".

---

## 2. Users and roles

| Role | Real or simulated | Does |
|---|---|---|
| Student | Simulated (synthetic personas) | Asks the tutor to clarify material they already studied, takes quizzes, submits open answers (lessons are available as optional reference, not a required step) |
| Teacher | **The owner**, live in the demo | Reviews pending grades, confirms or corrects |
| Maintainer | The owner | Versions rubrics and prompts, runs evals, reads traces |

Calibration ground truth is generated by an automated LLM reference-label pipeline (SRS §7.1), not by the Teacher role. This project has no human labeler at any stage — see §6 below for what that costs.

---

## 3. Scope (MoSCoW) and cut order

| Priority | Item |
|---|---|
| **Must** | M1 Phase-1 fixes of the existing repo evals · M2 Lessons + retrieval + grounded tutor · M4 Open-answer grader + publication policy · M5 Teacher review queue · M6 Calibration vs reference labels + keyword baseline · M7 Injection, answer-leak and fairness evals · M8 Honest README + ADR + talk track · M9 One annotated trace (promoted from Should — EVD-08 had no backing) · M10 CI running offline tests + traceability gate (promoted from Should — EVD-09 had no backing) |
| **Should** | M3 Deterministic quiz (downgraded from Must — backs no EVD claim by itself; kept as the one pure-code contrast case for EVD-01) · S1 Repeat runs on borderline cases (N=3) |
| **Could** | C1 Cloud Run deploy (Firestore) · C2 One Playwright test on a web wrapper · C3 Spanish-language answers |
| **Won't (roadmap)** | Real UI, auth, vector DB, question generation, email threads, multi-course, Vertex AI, human-labeled ground truth (see §6) |

**Cut order if time runs out (first to go → last):** C2 → C1 → C3 → S1 → M3. **Never cut:** M1, M2, M4, M5, M6, M7, M8, M9, M10.
**Fallback:** the calibration set is generated and reference-labeled entirely by an automated LLM pipeline (SRS §7.1) — there is no owner-labeling step to fall back from. Two exclusion mechanisms operate at different granularities and both apply: (a) per **criterion**, any criterion whose two reference passes disagree is flagged `uncertain` and dropped from the retention gate (SRS §7.1, AIR-01); (b) per **question**, if a question's double-pass self-consistency rate falls below 70%, that whole question's data is excluded. Mechanism (b) is the coarse backstop for a question the reference model cannot label stably even at the criterion level. Every exclusion is reported, not silently absorbed.

See `docs/BACKLOG.md` for how M1–M10 break down into stories, phases and tests.

---

## 4. Constraints

See `docs/SRS.md` §10 for the full constraints table (free tier, model id, Terraform-only infra, feature-freeze date, language, local-only talk-track file).

---

## 5. Delivery plan (CR time) and gates

| Phase | When | Content | Gate (evidence required to continue) |
|---|---|---|---|
| P0 | Thu 29 (today, compressed from the original Wed-night slot) | Approve this charter + SRS v0.2; open decisions (§7) resolved | Owner approval |
| P1 | Thu 29 | M1: fix the 4 defects, rerun evals, write PHASE1_FINDINGS | 3 cases pass, before/after numbers saved |
| P2 | Thu 29 – Fri 30 AM | M2 + M3 (S): lessons, retrieval, tutor, quiz, offline tests; rubrics and all calibration/grounding/integrity/injection/fairness datasets generated via the LLM pipeline, moved here from P3 so later phases aren't blocked; M10 scaffolded (traceability script running, even if not yet CI-gated) | Offline tests green; grounding report v0; datasets + reference labels committed with `label_provenance` |
| P3 | Fri 30 AM | M4+M5: grader, policy, queue, teacher CLI (datasets already exist from P2) | Policy tests green; demo of PUBLISH and REVIEW paths |
| P4 | Fri 30 PM | M6: calibration + baseline; apply retention rule | Report with `dev` and `holdout`, retention decision recorded |
| P5 | Sat 31 | M7: integrity, injection, fairness | Reports generated, gates evaluated |
| P6 | Sun 1 AM | M8: README, ADR, limitations, talk track; M9: one annotated trace; M10: CI gate wired to fail on untested Musts | Docs match reports; traceability gate green; **freeze 14:00** |
| P7 | Mon 2–Wed 4 | Rehearse; bug fixes only | Owner can explain every file |

Stop at the end of each phase and list the owner actions required. The only remaining owner action is approving this charter and the SRS — no hand-labeling, no dataset spot-approval.

**Schedule risk (stated, not hidden):** P1–P6 compress M1, M2, M4–M10 into roughly three days (Thu 29 – Sun 1). This is aggressive; the MoSCoW cut order in §3 is the mitigation, and the "never cut" list is what protects the EVD claims if time runs out. If a Must slips, the response is to drop `Could`/`Should` items in cut order and report reduced sample sizes honestly — not to skip a gate.

**EVD-01 and the quiz (M3):** M3 is a `Should` and is cuttable (last in the cut order before the never-cut list). EVD-01's determinism table uses MCQ scoring as its cleanest pure-code example, but it does not depend on it: citation validity (FR-15), the publication policy (FR-34), and retrieval (FR-11) are all code-owned and remain in the never-cut set, so EVD-01 survives even if M3 is cut. If M3 is cut, say in the ADR that MCQ scoring was the illustrative example and point to the policy instead.

---

## 6. Known limitations (to be stated in the README)

- 8 synthetic lessons and ~40 answers: results are indicative, with wide intervals.
- **Course scope is deliberately narrow** (SRS FR-10, FR-10a): variables, conditionals, loops, functions, lists, dicts, string methods, error handling — each lesson self-contained, none requiring cross-lesson synthesis to answer. This is a demo-evaluation choice, not a curriculum one: a cross-lesson topic (e.g. closures) would make the grounding check ambiguous, since a genuinely correct answer might legitimately need chunks outside the retriever's top-k. The real course this stands in for would need broader, overlapping topics and a retrieval strategy that handles that; this demo is scoped to avoid the problem rather than solve it.
- **No human labeler at any stage, and the reference model is the same as the grader.** All ground truth — calibration scores, grounding expectations, integrity/injection/fairness cases — is generated and self-checked by an LLM pipeline (SRS §7.1), not a person. This was a deliberate choice under the project's time constraints, not an oversight. The reference-label pipeline runs the **same model** as the grader under test (Gemini Flash Lite via AI Studio), differing only in prompt wording and a double pass. Two consequences stated plainly: (1) what the calibration measures is **self-consistency under reworded prompts, not independent calibration** — it is a weaker claim than "calibrated against an independent judge"; (2) the blind spot is not merely *correlated* bias between two models but bias **shared by one model** across both passes (e.g. the model being systematically lenient on a given answer pattern in both the reference and the grading role). A human grader, or even a genuinely different model tier, would not share that blind spot by construction; this setup cannot rule it out. The roadmap item is a real human-labeled set with inter-rater agreement, or at minimum a higher-tier reference model.
- Integrity and grounding checks are fully automated (string match / code-based citation check); there is no human read-through of outputs, so a subtly wrong-but-plausible answer or a paraphrased leak could pass undetected. The model's own knowledge of Python cannot be removed, so the tutor's grounding is a *measured property*, not an *enforced limit* — an answer sourced from memory that still cites a valid chunk is the specific case the automated check cannot catch (SRS §4.1.1). Since SRS v0.4 this is partly measured: a retrieval ablation (AIR-14a) and 4 canary facts (FR-10b, AIR-14b) test whether answers depend on retrieval. They cover only those 16 questions; elsewhere the risk remains a stated limitation.
- The Dev UI is not a product UI; there is no authentication — and the submission-status lookup has no login, so any student can query any submission id. Acceptable for a demo; listed here so it isn't discovered first by an interviewer.
- A keyword baseline is a weak adversary; beating it proves little by itself.
- Fairness pairs cover name and phrasing only; they do not cover other protected attributes.
- The injection detector is a static pattern list; its own bypass rate is reported separately from the policy gate precisely because a pattern list cannot be expected to catch novel attacks — the policy's confidence/borderline checks are the actual defense, the pattern list is a cheap first filter.
- Pass ≥4/6 with margin ±1 means only totals of 0–2 or 6 can ever reach PUBLISH, by construction — this makes the published false-pass rate look better than a wider publish band would. Stated here on purpose.
- Free-tier rate limits cap the number of repeats.
- Roadmap: real UI, auth, a real human-labeled calibration set with inter-rater agreement, larger dataset, per-slice gates, trace-level monitoring, email-thread flow.

---

## 7. Open decisions for the owner

| ID | Question | Resolution (2026-10-29) |
|---|---|---|
| OD-01 | Course language: English (lessons + answers). | **Resolved:** English |
| OD-02 | Rename the package or add `course_assistant/` next to `learning_coach/`? | **Resolved:** Add `course_assistant/`; keep `learning_coach/` as phase-1 evidence |
| OD-03 | Pass mark and borderline margin for the rubric. | **Resolved:** pass ≥4/6, margin ±1, rubrics locked to exactly 3 criteria (0–6 scale) so this is unambiguous (SRS FR-30) |
| OD-04 | Confidence threshold for auto-publish. | **Resolved:** 0.8, tuned on `dev` only. Correction from v0.1: the original wording ("recalibrate after P4") would have leaked the holdout set into tuning and invalidated EVD-02/03; any post-holdout change must now be reported explicitly as a holdout-breaking event, not folded in silently. |
| OD-05 | ~~Can you label 40 answers on Thu night?~~ | **Superseded.** No human labeling anywhere in this project (owner's explicit decision under time pressure). Ground truth is generated by the automated LLM reference pipeline (SRS §7.1). The fallback in §3 no longer depends on owner availability. |
| OD-06 | Confirm the interview date/time with Diego. | **Resolved:** confirmed Thu 2026-11-05, 16:00–17:00 CR (1 hour) |
| OD-07 | Which model does the reference-label pipeline use? | **Resolved:** the same model as the grader — Gemini Flash Lite, accessed via Google AI Studio with an API key. This makes the calibration a self-consistency measurement, not independent calibration (EVD-02, §6 reflect this). A higher-capability reference tier is roadmap, not in scope. |
| OD-08 | How does `keyword_baseline` map matched keywords to a 0–2 score per criterion? (SRS FR-37) | **Resolved (2026-10-29): locked** to 0 matched → 0; ≥1 but below half → 1; half or more → 2. Pre-registered before any holdout run so the comparison can't be gamed (AIR-11, EVD-03). The baseline is deliberately a dumb, non-AI control — a placebo the LLM grader must beat; an AI baseline would answer a different question. Owner may override this rule at doc-approval. |
| OD-09 | Do we measure and report latency / token cost per grade? | **Resolved (2026-10-29): yes.** Every report records p50/p90 per-grade latency and mean tokens-per-grade (AIR-22), with the free-tier sample-size caveat stated. This gives the role's operational-limits expectation (JD-02/JD-18) a minimal evidence line. |
| OD-10 | Promote the real-world-risk framing (SEC-07) to Must and add a one-page `RISK_REGISTER.md`? | **Resolved (2026-10-29): yes, both.** SEC-07 is now a Must, and `docs/RISK_REGISTER.md` is added (intended use, foreseeable misuse, controls → requirement ids, residual risk, human oversight). Directly on-target for the services/delivery-director panel. |

---

## 8. Out of scope for this document
Testable requirements (FR/AIR/SEC/NFR/CON) belong in `docs/SRS.md`. Epics, user stories, acceptance criteria and traceability belong in `docs/BACKLOG.md`. Module layout, prompts and schemas belong in `docs/SOLUTION_DESIGN.md`, written after approval. Nothing in this file authorizes code.
