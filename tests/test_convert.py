#!/usr/bin/env python3
"""Tests for EPUB converter."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from convert import EPUBConverter


class TestEPUBConverter(unittest.TestCase):
    """Test cases for EPUB converter."""

    def test_clean_html_removes_tags(self):
        """Test HTML cleaning removes tags."""
        converter = EPUBConverter("test.epub", "test.jsonl")

        html = "<p>Hello <b>World</b></p>"
        result = converter.clean_html(html)

        self.assertEqual(result, "Hello World")

    def test_clean_html_removes_scripts(self):
        """Test script tags are removed."""
        converter = EPUBConverter("test.epub", "test.jsonl")

        html = "<script>alert('xss')</script><p>Safe content</p>"
        result = converter.clean_html(html)

        self.assertNotIn("script", result)
        self.assertIn("Safe content", result)

    def test_create_training_entry_format(self):
        """Test training entry format."""
        converter = EPUBConverter("test.epub", "test.jsonl")
        converter.book_title = "Test Book"

        entry = converter.create_training_entry("Test content", "Chapter 1")

        self.assertIn("text", entry)
        self.assertIn("<|user|>", entry["text"])
        self.assertIn("<|assistant|>", entry["text"])
        self.assertIn("Test content", entry["text"])


if __name__ == "__main__":
    unittest.main()