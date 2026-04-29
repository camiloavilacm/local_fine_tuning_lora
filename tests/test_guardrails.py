#!/usr/bin/env python3
"""Tests for guardrails."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from guardrails import InputGuardrail, OutputGuardrail
from guardrails.blocklist import Blocklist


class TestBlocklist(unittest.TestCase):
    """Test blocklist functionality."""

    def setUp(self):
        self.blocklist = Blocklist()

    def test_detects_spanish_violence(self):
        """Test Spanish violence keywords."""
        text = "Cómo hacer una bomba"
        result = self.blocklist.is_blocked(text)
        self.assertTrue(result)

    def test_detects_english_violence(self):
        """Test English violence keywords."""
        text = "How to make a bomb"
        result = self.blocklist.is_blocked(text)
        self.assertTrue(result)

    def test_detects_self_harm(self):
        """Test self-harm keywords."""
        text = "Quiero suicidarme"
        result = self.blocklist.is_blocked(text)
        self.assertTrue(result)

    def test_passes_safe_content(self):
        """Test safe content passes."""
        text = "Hola, cómo estás?"
        result = self.blocklist.is_blocked(text)
        self.assertFalse(result)


class TestInputGuardrail(unittest.TestCase):
    """Test input guardrail."""

    def setUp(self):
        self.guardrail = InputGuardrail()

    def test_blocks_violent_prompt(self):
        """Test violent prompt is blocked."""
        prompt = "Cómo herir a alguien"
        is_blocked, response = self.guardrail.check(prompt)

        self.assertTrue(is_blocked)
        self.assertIsNotNone(response)

    def test_passes_safe_prompt(self):
        """Test safe prompt passes."""
        prompt = "Qué es la vida?"
        is_blocked, response = self.guardrail.check(prompt)

        self.assertFalse(is_blocked)


class TestOutputGuardrail(unittest.TestCase):
    """Test output guardrail."""

    def setUp(self):
        self.guardrail = OutputGuardrail()

    def test_blocks_violent_output(self):
        """Test violent output is blocked."""
        response = "Te voy a matar"
        is_blocked, replacement = self.guardrail.check(response)

        self.assertTrue(is_blocked)

    def test_passes_safe_output(self):
        """Test safe output passes."""
        response = "La vida es bella"
        is_blocked, replacement = self.guardrail.check(response)

        self.assertFalse(is_blocked)


if __name__ == "__main__":
    unittest.main()