# The Unofficial Guide

Ahmed Faheem — `campus_life`

**Status:** setup and the starter demonstration are verified. Five acceptance
criteria and their explanations are recorded in [criteria.md](criteria.md)
before calibration. The custom chunker and
calibration are the next implementation steps.

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

**Current starter settings:** 800 characters with 120-character overlap.
**Planned custom strategy, recorded before implementation:** a 600-character
soft budget and zero body-text overlap, keeping a complete short post together.
For longer documents, split at paragraph or sentence boundaries, preserving
complete sentences rather than cutting at an exact character position.

The 88 cleaned posts range from 178 to 549 characters, averaging 317. Reading
`dining_the_ridgeway_cafe.txt`, `course_cs_210.txt`,
`housing_innisfree_hall.txt`, and `transit_shuttle.txt` showed why the title and
related details belong together: the shuttle post, for example, ties service
frequency to a specific skipped stop. A 600-character budget accommodates each
current post with its context. Zero overlap avoids duplicating body text when a
complete post already forms one chunk. The starter also produces 88 chunks;
retaining that count would be an intentional choice, not evidence that the
chunker was never replaced.

Ingestion uses `ingest.py::clean_text` to normalize newlines, repeated spaces,
and excess blank lines while retaining paragraph boundaries. These provided
course documents contain plain text, with no navigation, ads, or HTML in the
reviewed sources. This is not a general-purpose web-page cleaner.

The strategy above was recorded before implementation; samples will be copied
from the custom chunker after it is implemented.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `` — produced by: ``

```
```

**Chunk 2** — source: `` — produced by: ``

```
```

**Chunk 3** — source: `` — produced by: ``

```
```

**Chunk 4** — source: `` — produced by: ``

```
```

**Chunk 5** — source: `` — produced by: ``

```
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**

**Answer:**

```
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
|  |  |  |

## How I Used AI

**1. Setup and secret handling.** I asked Codex to verify setup, keep the
Gemini key out of Git, and commit using my account. It found an empty virtual
environment and a setup check that read the model setting before loading
`.env`. The resulting changes installed the missing packages, stored the key
in an ignored local file, fixed the model-setting check, and verified a real
Gemini response under my Git identity.

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
