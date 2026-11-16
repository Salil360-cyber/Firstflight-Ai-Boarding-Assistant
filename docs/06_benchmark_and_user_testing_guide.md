# Guide: AI tool benchmark and user testing

**Status: to do.** The 54 questions, the scoring sheet and the rubric are ready. No tool has been tested yet and no user test has been run, so there are no results to report.

These two steps cannot be done for you: the scores have to come from really running the tools and really watching people use the assistant.

## Part A: benchmark 4 AI tools on 54 policy questions

Tools: Gemini (AI Studio), ChatGPT, Microsoft Copilot, NotebookLM.
File: `benchmark/AI_Tool_Benchmark_Scoring.xlsx` (sheet **Scoring** has one row per question per tool, 216 rows; sheet **Rubric** explains the scores).

1. Give every tool the same set-up: the system prompt from `docs/02_prompt_library.md` plus the policy handbook. In NotebookLM, upload the handbook as the source.
2. For each question, start a fresh chat, paste the question exactly as written, and copy the reply into the `tool_answer (paste)` column.
3. Score it using the Rubric sheet and fill in `score`, `issue_type` and `notes`.
4. Do all 54 questions on one tool before moving to the next. Expect about 45 minutes per tool.
5. Note the date and the model name shown by each tool; results change as tools are updated.

What to report when done:

| Report | Why |
|---|---|
| Average score per tool | Overall accuracy |
| Score by language (en, hi, ar) | The questions include 8 Hindi and 8 Arabic |
| Score by expected behaviour (answer, hand-off, refuse personal data, not covered) | Shows whether a tool guesses or over-shares |
| Number of unsafe answers per tool | The most important single number |

Do not write "tool X was best" anywhere until all 216 rows are scored.

## Part B: user testing with 5 people

Do this after the assistant is built (`docs/03_build_the_assistant_in_ai_studio.md`).

1. Find 5 people; at least 2 who have never flown or have flown once.
2. Give each person these 5 tasks and do not help them:
   - Find out when you must reach the airport for a domestic flight.
   - Find out how much bag you can carry on a Lite fare.
   - Ask one question in Hindi (or Arabic if they speak it).
   - Ask it to cancel your ticket.
   - Ask something you really want to know before a first flight.
3. For each task note: completed or not, time taken, where they got confused, what they said.
4. Ask 3 questions at the end: What was confusing? What would you change? Would you use this instead of calling? (1 to 5)
5. Make one round of changes to the prompt or the screen, and write down what you changed and why.

Do not use real names in the repo; write Tester 1 to Tester 5.

What to save: `user_testing/results.md` with the task table, the three biggest problems found, and the changes made.
