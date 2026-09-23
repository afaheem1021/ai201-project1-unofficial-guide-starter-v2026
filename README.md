# The Unofficial Guide

Ahmed Faheem — `campus_life`

**Status:** the unit 1 build and calibration are complete. Five acceptance
criteria are recorded in [criteria.md](criteria.md), with the targets committed
before calibration. The unit 2 evaluation sections below remain reserved for
the next assignment.

Repository to use for both units:
https://github.com/afaheem1021/ai201-project1-unofficial-guide-starter-v2026

---

# Unit 1

## What This Does

The Unofficial Guide answers questions about dining, housing, classes, and
campus services using the 88 short posts in `campus_life`. These documents are
fictional course materials, not advice about a real university. It searches
local document embeddings and asks Gemini to answer from the retrieved text
with source filenames. A distance gate refuses unrelated questions before
calling Gemini.

Run it locally with Python 3.11–3.13:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env   # first setup only; enter your own key in this local file
python test.py
python app.py index
python app.py ask "is the housing lottery random?"
python app.py ask      # interactive questions; empty input exits
```

Keep `.env` private. It, the virtual environment, response cache, and local
vector store are excluded from Git. Rebuild the index after changing the
chunker or corpus. See [RUNNING.md](RUNNING.md) for all commands and
[setup verification](results/unit1_setup.md) for the initial checks.

## Chunking Strategy

**Chunk size:** 600-character soft budget, including a title when present.
**Overlap:** 0 characters of body text. For a longer titled post, its title is
repeated on each chunk as context; none of the current posts needs splitting.
**Function:** `chunker.py::split_documents`.

The 88 cleaned posts range from 178 to 549 characters, averaging 317. Reading
`dining_the_ridgeway_cafe.txt`, `course_cs_210.txt`,
`housing_innisfree_hall.txt`, and `transit_shuttle.txt` showed why titles and
related details belong together: the shuttle post, for example, ties service
frequency to a specific skipped stop. The 600-character budget keeps those
complete thoughts together, and zero body overlap avoids duplicating information
when a post already fits in one chunk. This strategy was recorded in commit
`9d5e7cd` before implementation.

The custom function retains a short post intact. Longer posts are packed by
paragraph, splitting an oversized paragraph at sentence punctuation when needed;
a single oversized sentence stays whole even if it exceeds the soft budget.
This is a simple punctuation heuristic, so abbreviation-heavy future documents
would need further review. Sources never mix, and each chunk retains its filename,
per-document index, and producing function. The starter's `fallback_split` is
still available for comparison using explicit size 800 and overlap 120.

| Implementation | Documents | Chunks | Average characters | Shortest | Longest |
|---|---:|---:|---:|---:|---:|
| Starter, size 800 / overlap 120 | 88 | 88 | 317 | 178 | 549 |
| Custom, size 600 / body overlap 0 | 88 | 88 | 317 | 178 | 549 |

The equal counts are intentional: every current post fits the budget, so
splitting solely to increase the count would remove context without a demonstrated
benefit. The custom strategy changes how future longer posts are handled.

Ingestion uses `ingest.py::clean_text` to normalize newlines, repeated spaces,
and excess blank lines while retaining paragraph boundaries. The provided
course corpus contains plain text, rather than scraped navigation or ads;
this cleaner is not a general-purpose HTML or boilerplate remover.

## Sample Chunks

Exact text from `python app.py chunks -n 5`; the full output is in
[the chunk transcript](results/unit1_chunks.txt).

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```text
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::split_documents`

```text
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::split_documents`

```text
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::split_documents`

```text
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::split_documents`

```text
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

These five samples retain their source titles and complete body sentences.
Each can answer a question on its own: (1) when a dropped course earns a W,
(2) how BIOL 160 is assessed, (3) the weekly reading for HIST 118,
(4) peak waits and when to arrive at Pellew Dining Hall, and (5) Innisfree Hall's
AC, laundry prices, or quieter wing. The BIOL source's incongruous opening
“I lived here” is present in the original; preserving a source does not certify
that every sentence in it is accurate.

## Sample Answer

**Question:** Can I use meal swipes at The Ridgeway Café, and how do I pay there?

**Answer:** the complete output below came from a real Gemini request through
`app.py::ask_pipeline` and `generate.py::answer_from_chunks` after re-indexing
with the custom chunker. The model citation is inside the answer; the separate
retrieved-source list only describes search results.

```text
You cannot use meal swipes at The Ridgeway Café; it costs declining balance only, and no meal swipes are accepted (dining_the_ridgeway_cafe.txt).

Sources retrieved: dining_kestrel_commons.txt, dining_north_kitchen.txt, dining_the_ridgeway_cafe.txt, dining_the_ridgeway_cafe_followup.txt, dining_verrill_street_grill.txt

1 model calls this session, 987 tokens (950 in, 37 out)
```

The [complete prompt and answer](results/unit1_sample_answer.txt) were captured
with `python app.py ask "Can I use meal swipes at The Ridgeway Café, and how do I pay there?" --show-prompt`.

**Relevance cutoff:** `THRESHOLD = 0.68`; **top-k:** `5`.
The gate passes only when the best cosine distance is strictly below 0.68.
It returns `I don't have enough information about that.` without calling Gemini
when the threshold is not met or retrieval is empty.

| Question | In corpus? | Best distance |
|---|---|---:|
| Can I use meal swipes at The Ridgeway Café, and how do I pay there? | Yes | 0.536254 |
| Why should I complete the CS 210 labs even though they are only 10% of the grade? | Yes | 0.418646 |
| Does Innisfree Hall have air conditioning, and which wing is quieter? | Yes | 0.418144 |
| How many other institutions does the interlibrary system cover, and how long do requests take? | Yes | 0.339755 |
| How often does the campus shuttle run on weekdays versus weekends, and which stop can be skipped? | Yes | 0.382798 |
| What is the capital of Mongolia? | No | 0.824593 |
| How do I change the oil in a diesel engine? | No | 0.934011 |
| Who won the 1994 World Cup? | No | 0.885860 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844232 |
| How do I write a for loop in Rust? | No | 0.895998 |

The covered questions range from **0.339755 to 0.536254**; the unrelated
questions range from **0.824593 to 0.934011**. The midpoint of the gap is
approximately 0.680424, rounded to **0.68** to leave roughly equal room on either
side. The original 0.60 also separates these ten questions, so this is a
justified calibration choice, not a demonstrated accuracy improvement or an
optimal threshold. Lowering it below the Café's 0.536254 best match would
refuse an answerable question; raising it above 0.824593 would let the Mongolia
question through. Unseen paraphrases and related-but-unanswered questions may
still be misclassified.

The first three retrievals were inspected in full, not just by their scores:

- Café: North Kitchen ranked first (0.536254), but the correct Café post ranked
  second (0.542672). The nearest venue accepts swipes; the requested venue does
  not, so filenames and precise entity matching matter.
- CS 210: the assessment post ranked first (0.418646) and explicitly says exams
  reuse lab problems; the full course post ranked second.
- Innisfree: the noise post ranked first (0.418144), but the main post ranked
  second (0.477856) and contains both the AC and quiet-wing details.

Top-k 5 is retained because the best result alone is insufficient for two of
these questions, and all five calibration questions have a complete answer
source within the returned set. This does not establish that five is optimal:
extra excerpts can distract the model, and a gate pass means similarity rather
than proof that every part of a question is answered. The grounding instruction
therefore requires claim-specific filenames, faithful numbers and qualifications,
and an explicit acknowledgment of missing details.

All five `OUT_OF_SCOPE` questions were also run through the complete pipeline:
**5/5 were refused before generation, with 0 model calls**. See the
[gate-check evidence](results/unit1_gate_checks.json). The
[full retrieval transcript](results/unit1_retrieval.txt) includes every returned
chunk and distance, and the [calibration JSON](results/unit1_calibration.json)
preserves unrounded values. Its `threshold_at_measurement` is 0.60 because the
distances were recorded before selecting the final 0.68 cutoff.

An extra grounding check asked: **“What hours does the campus shuttle operate
on weekends?”** Its best distance was 0.396, so it passed the gate. The initial
answer incorrectly assigned the weekday 7am–11pm hours to weekends. The grounding
instruction was tightened to match each claim to its exact conditions and to
state when a related source omits the requested detail. The next real response
was:

```text
The provided documents do not specify the exact operating hours for the campus shuttle on weekends, other than stating it runs every 40 minutes on weekends (transit_shuttle.txt).
```

The [failed attempt](results/unit1_missing_detail_before.txt) and
[recheck with the revised prompt](results/unit1_missing_detail_after.txt) are
both preserved. This one successful recheck does not prove the problem is
eliminated: a citation alone does not verify a claim, and related-but-unanswered
questions still depend on the model obeying the grounding instruction.

These ten questions are calibration data, not an independent evaluation of
future accuracy. The three-run acceptance evaluation belongs to unit 2 and has
not been run. The source-based test procedures are in the
[criteria self-check](results/unit1_criteria_review.md).

To reproduce the local checks:

```bash
python app.py index
python tools/calibrate.py          # real retrieval; no Gemini calls
python -m unittest discover -s tests -v
```

All **14 regression tests** pass. They cover exact preservation of the 88
short posts, long-post boundaries and provenance, overlong sentences, empty
inputs, rejection before generation, and blank model responses or cached values.
The original setup check also passed all 10 checks, including a real Gemini call.
The special-activity starter count is **26**; see
[the original setup record](results/unit1_setup.md).

## How I Used AI

**1. Setup and secret handling.** I asked Codex to verify setup, keep the
Gemini key out of Git, and commit using my account. It found an empty virtual
environment and a setup check that read the model setting before loading
`.env`. The resulting changes installed the missing packages, stored the key
in an ignored local file, fixed the model-setting check, and verified a real
Gemini response. Commits used my configured Git identity.

**2. Criteria and corpus review.** I asked Codex to complete the custom criteria
and review the five questions and the supplied criteria's explanations. It
checked each question against the source files and defined tests for preserving
chunk context and producing complete, source-supported answers. The review
clarified that a retrieved-source footer is not a model citation, that a refusal
fails an in-corpus question, and that each target must hold independently in each
of the next unit's three runs. These definitions were recorded before calibration.

No stretch features are planned for this unit.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
