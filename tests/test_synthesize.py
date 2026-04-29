#!/usr/bin/env python3
"""Tests for Q&A synthesizer."""

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from synthesize import QASynthesizer


class TestQASynthesizer(unittest.TestCase):
    """Test cases for Q&A synthesizer."""

    def setUp(self):
        self.synthesizer = QASynthesizer(min_sentence_length=10)

    def test_extract_sentences_splits_on_periods(self):
        """Test sentence extraction."""
        text = "This is sentence one. This is sentence two! Is this three?"
        result = self.synthesizer.extract_sentences(text)

        self.assertGreaterEqual(len(result), 2)

    def test_extract_sentences_filters_short(self):
        """Test short sentences are filtered."""
        text = "Short. This is a much longer sentence that should pass."
        result = self.synthesizer.extract_sentences(text)

        self.assertEqual(len(result), 1)

    def test_generate_qa_pairs_returns_list(self):
        """Test Q&A generation returns list."""
        text = "Lucas es un niño curioso. Él vive en el bosque. El bosque tiene secretos."
        result = self.synthesizer.generate_qa_pairs(text, num_pairs=2)

        self.assertIsInstance(result, list)
        self.assertLessEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()