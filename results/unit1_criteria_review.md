# Criteria self-check before calibration

The five questions, expected phrases, and targets were reviewed against the
source files before searching the vector store for these questions. Criteria
were committed in `ea278ec` before the custom chunker and calibration.

## How each criterion can be tested

1. Retrieve the top five chunks for each question. Count a question only when
   **one chunk** contains all facts needed for its answer; do not combine
   partial answers across chunks for this criterion. Target: at least 4/5.
2. Inspect each substantive model answer for at least one source filename.
   The CLI's separate `Sources retrieved` footer does not count as a citation.
   Fixed gate refusals are tested under criterion 3 and must not fabricate sources.
3. Run each of the five distinct `OUT_OF_SCOPE` questions through the gate once.
   Count only refusals made before generation, with the fixed no-information
   response. A model refusing after the gate passes does not count. Target: 4/5.
4. Run the exact sample command in criterion 4, archive source filenames and
   chunk indices, and compare each chunk with its source. The title must be in
   the chunk text, followed by a complete body sentence, with no cut sentence
   at either end. All three checks must hold for all five samples.
5. Compare each answer to every required fact below, then check each additional
   factual claim against the source document actually cited in the answer.
   An in-corpus refusal fails that question. Target: at least 4/5 per run.

For unit 2, each answer target must hold in each of the three independent runs.
The deterministic retrieval/chunk/gate checks do not become stronger evidence
merely by repeating an identical input and index.

## Source-derived answer checklist

| Question topic | Complete answer requires | Source |
|---|---|---|
| Ridgeway Café | No meal swipes; declining balance only. | `dining_the_ridgeway_cafe.txt` |
| CS 210 labs | Exams reuse lab problems despite labs being only 10% of the grade. | `course_cs_210.txt`, `course_cs_210_exams.txt` |
| Innisfree Hall | No air conditioning; the short wing is quieter. | `housing_innisfree_hall.txt` |
| Interlibrary system | Eleven other institutions; requests take about a week. | `admin_library_holds.txt` |
| Shuttle | Every 20 minutes on weekdays, every 40 minutes on weekends; Fenwick Court can be skipped when the driver is behind. | `transit_shuttle.txt` |

The `expects` phrases are screening clues, not sufficient proof of a correct
answer. For example, `week` does not establish the eleven-institution detail.
Weekend shuttle operating hours are absent from the source and must not be
inferred from weekday operating hours.

## Final check against the course checklist

The [official criteria self-check](https://courses.codepath.org/courses/ai201/pages/criteria_self_check)
was consulted during the final write-up. The original targets remain unchanged.
Each target identifies a count or visible behavior, a fixed sample, a checking
procedure, and a corpus-specific reason. Together they cover retrieval, source
naming, refusal, chunk context, and factual answer quality; criterion 3 covers
failure behavior. Criterion 4 counts usable source-context chunks; criterion 5
counts fully supported answers, with completeness and claim support defining a
passing answer rather than scoring separate pipeline stages together.

Two readers may still differ on whether a paraphrase is supported. The fixed
source-derived checklist above and claim-by-claim reading reduce that ambiguity;
`expects` alone must not be treated as an automatic correctness scorer. A missing
answer part or a wrong qualifier is a failure even when the expected phrase and
a source filename both appear.
