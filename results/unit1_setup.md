# Unit 1 setup verification

Verified on 2026-09-22 before changing the starter chunker.

- Repository: `afaheem1021/ai201-project1-unofficial-guide-starter-v2026`, verified fork of the CodePath starter.
- Git author and committer: Ahmed Faheem; GitHub CLI authenticated as `afaheem1021`.
- Python: 3.13.15, in the project `.venv`.
- Installed all seven direct requirements from `requirements.txt`; `python -m pip check` passed.
- `python test.py`: **10 passed, 0 failed, 0 warnings, 0 skipped**.
- Real local embedding: `all-MiniLM-L6-v2`, 384 dimensions.
- Chroma cosine nearest-neighbor round trip passed.
- Real generation check: `gemini-3.5-flash-lite` replied `Ready.`
- `.env` is ignored, untracked, and readable/writable only by its owner. No key is included here.

## Special activity

Before changing chunking, `python app.py --corpus advice_threads chunks -n 1` reported **26 chunks total**.

The digits to retain for the activity are **26**. This is a starter measurement, not the later custom chunker count.

## Starter pipeline

`python app.py index` loaded 88 documents / 27,908 characters and stored
88 chunks made by `chunker.py::fallback_split`: average 317 characters,
shortest 178, longest 549. The original settings were size 800, overlap 120,
top-k 5, and cutoff 0.6.

The required first question, `is the housing lottery random?`, returned a real
Gemini answer citing `admin_housing_lottery.txt`; see
[complete starter output](unit1_starter_answer.txt). This starter demonstration
precedes the acceptance-criteria milestone, as required; the five test questions
have not been evaluated.

The editor sandbox initially prevented ONNX from creating its macOS working
directory. Re-running with normal filesystem access succeeded. This was an
execution-environment restriction, not a corpus or chunking failure.

Setup-check repairs: resolve the optional model override after loading `.env`,
and treat a blank API response as a failure. Both behaviors passed isolated
regression checks using mocked responses and no external requests.
