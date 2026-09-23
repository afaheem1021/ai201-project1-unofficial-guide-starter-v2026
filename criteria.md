# Acceptance criteria — The Unofficial Guide

These targets are recorded in unit 1 **before the five-question calibration
and unit 2 evaluation**. The assignment's required starter demonstration is
recorded separately in `results/unit1_starter_answer.txt`.

Use the five `QUESTIONS` and five `OUT_OF_SCOPE` questions in `questions.py`,
the `campus_life` corpus, and the committed default settings. A gate refusal
is tested by criterion 3; it must not invent a source to satisfy criterion 2.
For criteria 2 and 5, evaluate the model's answer text, not the separate
`Sources retrieved` diagnostic line. In unit 2, each answer criterion's target
must hold in each of the three runs, not just in aggregate.

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:** Several housing and course files repeat similar vocabulary,
and some questions ask for multiple details, so four of five allows one retrieval
miss while requiring useful results across campus topics. A lower target would
tolerate too many routine failures; five of five would leave no room for an
ambiguous match.

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:** Every retrieved chunk already carries a filename that is
provided to the model, so requiring attribution on every substantive answer is
reasonable. Even one uncited answer would prevent the reader from checking it;
the fixed no-information refusal is evaluated separately under criterion 3.

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

**Why this target:** The five `OUT_OF_SCOPE` questions concern topics outside
these fictional campus posts, but four refusals allows one accidental semantic
match. A looser target would accept too much unrelated material; the cutoff will
be calibrated after recording this target, without changing it to fit results.

## 4. Sampled chunks retain the post's context and complete sentences

All 5 chunks printed by `python app.py --corpus campus_life chunks -n 5`
include their source post's title and at least one complete body sentence,
with no sentence cut in half at either end.

**Why this target:** These posts are short, and a title identifies which course,
dorm, or service the details describe, so losing it can make otherwise correct
sentences ambiguous. Requiring all five, rather than allowing one damaged chunk,
is reasonable for this corpus and tests whether the chunker preserves usable
context instead of merely producing nonempty text.

## 5. Answers are complete and supported by their citations

For at least 4 of the 5 questions in `QUESTIONS`, the generated answer addresses
every part of the question, and every factual claim is supported by at least
one source document cited in that answer. A refusal to an in-corpus question
counts as a failure for that question.

**Why this target:** Several questions combine details, such as shuttle
frequency and the skipped stop, so a plausible partial answer is not sufficient.
Four of five permits one generation error while requiring useful, checkable
answers; three of five would allow too many omissions, and five of five would
leave no allowance for model variability.

---

In unit 2, preserve these original targets. If a target cannot be measured,
append a clearly labeled revision and its reason; do not lower a target just
because the system missed it.
