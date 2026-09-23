"""Regression checks for refusal-before-generation and blank model output."""

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import app
import config
import gate
import generate
from store import Result


def result(distance):
    return Result(
        text="Campus shuttle\n\nThe bus runs every 20 minutes.",
        source="shuttle.txt",
        label="shuttle.txt#0",
        distance=distance,
        produced_by="chunker.py::split_documents",
    )


class RelevanceGateTests(unittest.TestCase):
    def test_refusal_never_builds_prompt_or_calls_generator(self):
        for hits in ([], [result(0.9)], [result(0.6)]):
            with self.subTest(hits=hits), patch("store.search", return_value=hits), \
                    patch("generate.answer_from_chunks") as answer, \
                    patch("generate.build_prompt") as prompt:
                outcome = app.ask_pipeline("unrelated question", threshold=0.6)
                self.assertTrue(outcome["refused"])
                self.assertEqual(outcome["answer"], gate.REFUSAL)
                self.assertEqual(outcome["sources"], [])
                self.assertIsNone(outcome["prompt"])
                answer.assert_not_called()
                prompt.assert_not_called()

    def test_gate_uses_nearest_result_not_list_position(self):
        self.assertTrue(gate.check([result(0.9), result(0.3)], threshold=0.6).passed)
        self.assertFalse(gate.check([result(0.3)], threshold=0).passed)

    def test_supported_question_reaches_generator_once(self):
        hits = [result(0.2)]
        with patch("store.search", return_value=hits), \
                patch("generate.answer_from_chunks", return_value="Every 20 minutes (shuttle.txt).") as answer:
            outcome = app.ask_pipeline("How often is the shuttle?", threshold=0.6)
        self.assertFalse(outcome["refused"])
        self.assertIn("shuttle.txt", outcome["answer"])
        answer.assert_called_once_with("How often is the shuttle?", hits)


class GenerationTests(unittest.TestCase):
    def test_invalid_cached_response_is_refreshed(self):
        for cached in ("", "  ", None, 42):
            with self.subTest(cached=cached), tempfile.TemporaryDirectory() as folder, \
                    patch.object(config, "CACHE_DIR", Path(folder)), \
                    patch.object(config, "CACHE_ENABLED", True), \
                    patch.object(generate, "_session_calls", 0), \
                    patch.object(generate, "_call_times", []), \
                    patch.object(generate, "_get_client") as get_client:
                key = generate._cache_key("question", None)
                (Path(folder) / f"{key}.json").write_text(json.dumps({"response": cached}))
                get_client.return_value.models.generate_content.return_value = SimpleNamespace(
                    text="Every 20 minutes (shuttle.txt).", usage_metadata=None
                )
                self.assertEqual(generate.generate("question"), "Every 20 minutes (shuttle.txt).")
                get_client.return_value.models.generate_content.assert_called_once()
                self.assertEqual(generate._cache_read(key), "Every 20 minutes (shuttle.txt).")

    def test_empty_response_is_not_returned_or_cached(self):
        fake_client = SimpleNamespace(models=SimpleNamespace(
            generate_content=lambda **kwargs: SimpleNamespace(text=" ", usage_metadata=None)
        ))
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(config, "CACHE_DIR", Path(folder)), \
                patch.object(config, "CACHE_ENABLED", True), \
                patch.object(generate, "_client", fake_client), \
                patch.object(generate, "_session_calls", 0), \
                patch.object(generate, "_call_times", []):
            with self.assertRaisesRegex(RuntimeError, "no answer text"):
                generate.generate("question")
            self.assertEqual(list(Path(folder).iterdir()), [])


if __name__ == "__main__":
    unittest.main()
