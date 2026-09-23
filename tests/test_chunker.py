"""Focused checks for the campus-post chunking strategy (no API calls)."""

import unittest
from unittest.mock import patch

import config
from chunker import fallback_split, split_documents
from ingest import Document, load_documents


class ChunkerTests(unittest.TestCase):
    def test_real_corpus_preserves_complete_posts_and_provenance(self):
        documents = load_documents("campus_life")
        chunks = split_documents(documents)
        self.assertEqual(len(documents), 88)
        self.assertEqual(len(chunks), len(documents))
        for document, chunk in zip(documents, chunks):
            with self.subTest(source=document.source):
                self.assertLessEqual(len(document.text), config.CHUNK_SIZE)
                self.assertEqual(chunk.text, document.text)
                self.assertEqual(chunk.source, document.source)
                self.assertEqual(chunk.index, 0)
                self.assertEqual(chunk.label, document.source + "#0")
                self.assertEqual(chunk.produced_by, "chunker.py::split_documents")
        self.assertEqual(chunks, split_documents(documents))

    def test_short_post_keeps_internal_whitespace(self):
        text = "  Study rooms\n\nFirst line.  Second line.\nFinal line.\n "
        self.assertEqual(split_documents([Document("short.txt", text)])[0].text, text.strip())

    def test_long_titled_post_preserves_paragraphs_and_all_body_text_once(self):
        title = "Library tips"
        paragraphs = [
            "Reserve a study room before arriving.",
            "Bring your student card to the desk.",
            "Return the key before the building closes.",
        ]
        document = Document("library.txt", title + "\n\n" + "\n\n".join(paragraphs))
        with patch.object(config, "CHUNK_SIZE", 90):
            chunks = split_documents([document])
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].text, title + "\n\n" + "\n\n".join(paragraphs[:2]))
        self.assertEqual(chunks[1].text, title + "\n\n" + paragraphs[2])
        self.assertEqual([chunk.index for chunk in chunks], [0, 1])
        for chunk in chunks:
            self.assertEqual(chunk.source, "library.txt")
            self.assertLessEqual(len(chunk.text), 90)
        bodies = [chunk.text.removeprefix(title + "\n\n") for chunk in chunks]
        self.assertEqual(" ".join(bodies).split(), " ".join(paragraphs).split())

    def test_large_paragraph_splits_only_between_complete_sentences(self):
        sentences = [
            "The first shuttle leaves at dawn.",
            "The second shuttle stops at the library!",
            "Does the final shuttle stop at the gym?",
        ]
        text = "Shuttle route\n\n" + " ".join(sentences)
        with patch.object(config, "CHUNK_SIZE", 60):
            chunks = split_documents([Document("route.txt", text)])
        self.assertEqual([chunk.text for chunk in chunks], ["Shuttle route\n\n" + sentence for sentence in sentences])

    def test_overlong_sentence_remains_whole(self):
        sentence = "The help desk " + "handles questions " * 12 + "every weekday."
        text = "Desk hours\n\n" + sentence + " Bring your ID."
        with patch.object(config, "CHUNK_SIZE", 60):
            chunks = split_documents([Document("desk.txt", text)])
        self.assertEqual([chunk.text for chunk in chunks], ["Desk hours\n\n" + sentence, "Desk hours\n\nBring your ID."])
        self.assertGreater(len(chunks[0].text), 60)

    def test_untitled_long_post_does_not_repeat_first_sentence(self):
        sentences = ["Each room has a desk.", "The library closes at nine.", "The cafe stays open later."]
        with patch.object(config, "CHUNK_SIZE", 35):
            chunks = split_documents([Document("untitled.txt", " ".join(sentences))])
        self.assertEqual([chunk.text for chunk in chunks], sentences)

    def test_empty_documents_are_skipped_and_sources_do_not_mix(self):
        documents = [Document("blank.txt", " \n\t"), Document("one.txt", "First post."), Document("two.txt", "Second post.")]
        chunks = split_documents(documents)
        self.assertEqual([(chunk.source, chunk.index, chunk.text) for chunk in chunks], [("one.txt", 0, "First post."), ("two.txt", 0, "Second post.")])
        self.assertEqual(split_documents([]), [])

    def test_invalid_chunk_size_fails_clearly(self):
        for size in (0, -1, 1.5, True):
            with self.subTest(size=size), patch.object(config, "CHUNK_SIZE", size):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    split_documents([Document("post.txt", "A post.")])

    def test_fallback_remains_available(self):
        chunks = fallback_split([Document("post.txt", "abcdefghij")], chunk_size=6, overlap=2)
        self.assertEqual([chunk.text for chunk in chunks], ["abcdef", "efghij", "ij"])
        self.assertTrue(all(chunk.produced_by == "chunker.py::fallback_split" for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
