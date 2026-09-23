#!/usr/bin/env python3
"""Milestone 4: record real retrieval distances without calling Gemini.

Run after `python app.py index`: `python tools/calibrate.py`.
This is calibration evidence, not the three-run evaluation for unit 2.
"""

import json
import subprocess
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config
from questions import QUESTIONS, OUT_OF_SCOPE
from store import search


def main():
    if len(QUESTIONS) != 5 or len(OUT_OF_SCOPE) != 5:
        raise ValueError("Calibration requires five in-corpus and five out-of-scope questions.")
    if any(not q["question"].strip() or not q["expects"].strip() for q in QUESTIONS):
        raise ValueError("Fill in every question and expected phrase before calibration.")

    rows = []
    transcript = ["Unit 1 retrieval calibration — no generation calls\n"]
    groups = [(True, [q["question"] for q in QUESTIONS]), (False, OUT_OF_SCOPE)]
    for in_corpus, questions in groups:
        for question in questions:
            results = search(question, corpus=config.CORPUS, top_k=config.TOP_K)
            if not results:
                raise RuntimeError("No results. Build the index before calibrating.")
            rows.append({
                "question": question,
                "in_corpus": in_corpus,
                "best_distance": min(r.distance for r in results),
                "results": [asdict(r) for r in results],
            })
            transcript.append(f"Question: {question}\nIn corpus: {in_corpus}\n")
            for rank, result in enumerate(results, 1):
                transcript.append(
                    f"{rank}. {result.label} | cosine distance {result.distance:.6f}\n"
                    f"Produced by: {result.produced_by}\n{result.text}\n"
                )

    in_distances = [r["best_distance"] for r in rows if r["in_corpus"]]
    out_distances = [r["best_distance"] for r in rows if not r["in_corpus"]]
    summary = (
        f"In-corpus best distances: {min(in_distances):.6f}–{max(in_distances):.6f}\n"
        f"Out-of-scope best distances: {min(out_distances):.6f}–{max(out_distances):.6f}\n"
        f"Gap between groups: {min(out_distances) - max(in_distances):.6f}\n"
        "Choose a cutoff after inspecting the retrieved text. These ten examples\n"
        "are calibration data, not an independent measure of generalization.\n"
    )
    transcript.append(summary)
    evidence = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "corpus": config.CORPUS,
        "embedding_model": config.EMBEDDING_MODEL,
        "chunk_size": config.CHUNK_SIZE,
        "chunk_overlap": config.CHUNK_OVERLAP,
        "top_k": config.TOP_K,
        "distance_metric": "cosine",
        "threshold_at_measurement": config.THRESHOLD,
        "rows": rows,
    }
    config.RESULTS_DIR.mkdir(exist_ok=True)
    (config.RESULTS_DIR / "unit1_calibration.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (config.RESULTS_DIR / "unit1_retrieval.txt").write_text(
        "\n".join(transcript), encoding="utf-8"
    )
    print("\n".join(transcript))


if __name__ == "__main__":
    main()
