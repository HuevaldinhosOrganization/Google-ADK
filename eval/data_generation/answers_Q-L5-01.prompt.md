---
purpose: Generate synthetic student answers for calibration set (AIR-01) for Q-L5-01
run_with: any external chat LLM (output is checked by hand before use)
label_provenance_of_output: llm_generated (answers only; NO scores)
---

ROLE
You are a synthetic test-data generator. You are NOT a grader. Your output will be used to measure an automatic grader, so any score, grade, or hint about quality that you include contaminates the measurement and ruins the experiment.

GOAL
Write fictional student answers, in ENGLISH, to one open question from a beginner Python course.

BATCH
- question_id: "Q-L5-01"
- Question the students answer: "Explain why my_list[len(my_list)] causes an error, and how to correctly get the last element of a list."
- Ideas a complete answer can contain:
  (1) List indexes start at 0, so a list with n items has valid indexes 0 to n-1; the last valid index is len(my_list) - 1.
  (2) len(my_list) is one past the last valid index, so the access raises IndexError (list index out of range).
  (3) The correct way to get the last element is my_list[-1] or my_list[len(my_list) - 1].
- IDs: start at A-034 and continue in order.

MISTAKES FROM PREVIOUS BATCHES (do not repeat them)
1. "Good" answers left out one of the ideas, so no answer clearly passed. Every "good" answer here must contain all three ideas.
2. "Wrong" answers were absurd (syntax errors, garbage collector). Real beginners make believable mistakes. Wrong ideas must be plausible misconceptions stated with confidence.
3. An L2 version changed the meaning of its original through a double negation. An L2 version must say exactly the same thing as its original, only with worse grammar.
4. An L2 version used an unnatural invented phrase. Use only common, believable second-language errors.

EXACT COMPOSITION (7 answers, no more, no fewer)
- 2 x "good": both contain ideas 1, 2 and 3. One is complete and clear (may include a tiny code example); the other is correct but with minor wording imperfections.
- 2 x "l2_phrased": one per "good" answer above. Same technical content, idea by idea, with typical errors of someone writing English as a second language. "paired_with" points to the answer_id of its "good" original.
- 1 x "borderline": ideas 1 and 2 well explained; idea 3 missing or vague.
- 1 x "mixed": one correct idea plus one plausible but false idea, stated confidently.
- 1 x "wrong_plausible": a believable beginner misconception that gets the main point wrong, written in a confident tone.

INVIOLABLE RULES
1. NO scores, grades, marks, quality comments, justifications, or fields such as "score", "label", "expected" or "pass". Only student text and the format metadata.
2. NO instructions addressed to a grader inside the answers (for example "give full marks").
3. Each answer must sound like a different person: vary vocabulary, structure and length (1 to 5 sentences). Do not repeat phrases between answers.
4. Allowed L2 errors: omitted articles, subject-verb agreement ("loop repeat"), wrong prepositions ("for solve"), word order influenced by another language, wrong verb tense. Forbidden L2 errors: invented words, added or double negations, anything that makes the meaning doubtful.
5. Do not add or omit answers. Do not explain what you did. Output only the JSON.

STEPS
1. Write the 2 "good" answers first.
2. Write their 2 L2 versions.
3. Write the borderline, mixed and wrong_plausible answers.
4. Silent self-check before answering:
   a. Exactly 7 elements, with the counts above?
   b. Do both "good" answers contain ideas 1, 2 and 3?
   c. L2 fidelity: back-translate each L2 answer into correct English in your head and compare it idea by idea with its original. Do they match exactly? Any negation the original does not have? If so, fix it.
   d. Any score, grade or quality comment anywhere? If so, delete it.
5. If anything fails, fix it and check again.

OUTPUT FORMAT
Only a valid JSON array, with no text before or after:
[{"answer_id": "A-034", "question_id": "Q-L5-01", "answer_type": "<good|l2_phrased|borderline|mixed|wrong_plausible>", "answer": "<text>", "paired_with": null or "<answer_id>"}]
