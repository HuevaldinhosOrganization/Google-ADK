# CLAUDE.md — Google-ADK / Course Assistant

## What this repo is
Evidence for an **AI Senior SDET interview at Edify** (conversation, not live coding; Thu 2026-11-05).
- `learning_coach/` — phase-1 ADK demo (committed). Kept as EVD-07 evidence; only M1 fixes (FR-01..05) touch it.
- `course_assistant/` — the new Course Assistant: grounded tutor + LLM-graded open answers + publication policy + teacher review queue.
The system is a **vehicle for evaluation evidence**, not a product. When in doubt, choose the simpler design the owner can explain over the more impressive one he cannot (NFR-07).

## Sources of truth (read before acting)
| File | Owns |
|---|---|
| `docs/SRS.md` | **What** (requirements FR/AIR/SEC/NFR/CON). Wins over any prompt, note or comment. |
| `docs/PROJECT_CHARTER.md` | Why, scope, evidence claims EVD-01..10, limitations, open decisions (§7) |
| `docs/BACKLOG.md` | Stories, Gherkin acceptance criteria, tracking |
| `docs/RISK_REGISTER.md` | Intended use, misuse, controls, residual risk |
| `docs/SOLUTION_DESIGN.md` | **How** (module layout, schemas). Written only after SRS approval |
| `docs/background/` | Local-only, git-ignored (TARGET_ROLE, INTERVIEW_NOTES). Never commit or quote publicly |

## Hard rules
1. **No code until the owner approves the SRS.** Docs, data files, rubrics and prompts are allowed when asked.
2. **Spec changes need owner approval.** Propose the change (requirement id + exact wording); do not silently implement something the SRS doesn't say. If you find a gap or contradiction, stop and report it.
3. **Every requirement traces to an EVD claim.** Work that serves no EVD claim is scope creep: flag it, don't build it.
4. **Feature freeze: Sun 2026-11-01 14:00 CR.** After it: bug fixes, docs, rehearsal only.
5. **Stop at the end of each phase** (SRS §12) and list the owner actions required.

## Design rules (determinism boundary — ADR-001)
- The LLM **proposes**; code and the human teacher **decide**. If a step is a pure function of state, the LLM does not own it.
- `publication_policy` is code only and **fails closed**: any missing, malformed or out-of-range input → REVIEW. Never PUBLISH by default.
- Total score = sum of the 3 validated criterion scores, computed by code. Never trust an LLM-returned total.
- No agent tool may change a final grade. Final grades are immutable; the original LLM proposal is kept for audit.
- Answer keys, rubrics and keywords live in data modules the tutor's tools cannot import (FR-14, SEC-04).
- Student text is **untrusted data** in every prompt (delimited, never instructions).
- The text graded must be exactly what the student wrote — no agent may paraphrase it before `grade_open_answer`.

## Evaluation integrity rules
- **No human labels exist.** Reference labels come from the LLM reference pipeline (same model as the grader, two differently worded passes). Every label carries `label_provenance` (`llm_reference` / `llm_generated`, never `human`). Never describe results as "calibrated against human labels".
- Never generate, alter or "fix" expected values/labels to make a test pass. Report the failure instead.
- Tune prompts, thresholds and keywords on `dev` only. `holdout` runs once, for reporting. Any change after seeing holdout must be reported as a holdout-breaking event.
- `keyword_baseline` match→score rule is frozen (OD-08). Do not tune it to win or lose.
- Grounding is measured, not enforced (SRS §4.1.1). Retrieval ablation (AIR-14a) and canary facts (FR-10b, AIR-14b) measure whether tutor answers depend on retrieval. Canaries are course conventions, never false Python, never overlapping a rubric criterion.
- Small samples are reported with Wilson 95% intervals, never as "proves". Results from fakes/fixtures are labelled `fixture` (honesty rule).
- Each report records: model id, temperature, prompt version, rubric versions, detector pattern-list version, dataset hash, git commit, date, run mode, label provenance, p50/p90 latency, tokens per grade (AIR-22).

## Versioned artifacts (never edit in place once used in a stored report)
- Rubrics: `course_assistant/rubrics/<question_id>_v<N>.yaml` — exactly 3 criteria, 0–2 each, pass mark 4/6, margin ±1 (totals 3–5 → REVIEW). Change = new `_v<N+1>` file.
- Prompts: `course_assistant/prompts/<name>_v<N>.md` — same rule (NFR-04).
- Policy constants: `course_assistant/config/grading_policy.yaml`.
- Questions: `course_assistant/data/open_questions.yaml` (question text lives only here).
- Lessons (fixed order, FR-10): L1 Variables/types · L2 Conditionals · L3 Loops · L4 Functions · L5 Lists · L6 Dictionaries · L7 String methods · L8 Error handling. Question ids follow the lesson (`Q-L4-01` = Functions).

## ADK gotchas
- ADK replaces `{identifier}` in agent instructions with session-state values. **Agent instruction prompts must not contain curly braces** unless they are intended state variables.
- `grader_v1` and the reference-label prompts are direct model calls inside tools, not agent instructions; their `{{placeholders}}` are filled by code.
- ADK 2.13.0 supports `output_schema` together with `tools` (structure enforced on the final output only).
- Model id comes from `config.py` (`gemini-3.1-flash-lite`); change only with a recorded reason (CON-02). No silent fallback to another model (NFR-03).

## Security and data
- Synthetic data only. No real names, emails or student data (SEC-01).
- Gemini API key from the environment only; never log, trace, print or write it to reports. `.env` stays git-ignored (SEC-02).
- Free tier only: Gemini API free tier, local SQLite. No Vertex AI, no Cloud SQL (CON-01). Infra, if any, is Terraform and the owner runs `apply`.

## Commands (Windows, PowerShell)
```powershell
python -m venv .venv; .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest                                   # offline tests, no network (target < 60 s, NFR-02)
adk web                                  # Dev UI (developer UI, not a product UI)
adk eval learning_coach learning_coach/learning_coach_basics.evalset.json --config_file_path eval/test_config.json
```
Note: `pyproject.toml` only packages `learning_coach*`; add `course_assistant*` when its code starts.

## Testing conventions
- Tag tests with the requirement id: `@pytest.mark.req("FR-34")` (register the marker; `--strict-markers` is on).
- Offline tests use a fake LLM; live runs are explicit and labelled `live`.
- Every policy rule gets a pass/fail test, including each fail-closed input.

## Working with the owner (Felipe)
- Talk to him in **Spanish**; write code, docs, prompts and data in **English**.
- Be direct; push back when something is wrong or out of scope. He prefers honest gaps over impressive claims.
- He must be able to explain every file in the interview: prefer small modules, no framework he can't describe, and explain the "why" of non-obvious choices.
- Never commit or push unless asked.
