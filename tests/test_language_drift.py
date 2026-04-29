#!/usr/bin/env python3
"""Language drift detection test."""

import re
import unittest


class TestLanguageDrift(unittest.TestCase):
    """Test for code-switching / language drift."""

    SPANISH_PROMPTS = [
        "¿Quién es el protagonista?",
        "Qué pasó en el capítulo",
        "Explain en español",
    ]

    ENGLISH_WORDS = [
        "the", "and", "is", "are", "was", "were",
        "chapter", "book", "story", "character",
    ]

    def test_code_switching_detection(self):
        """Test English words in Spanish response detected."""
        response = "El protagonista es the main character del libro."

        english_words = self._count_english_words(response)
        percentage = (english_words / len(response.split())) * 100

        self.assertGreater(percentage, 5.0)

    def test_clean_spanish(self):
        """Test clean Spanish doesn't trigger drift."""
        response = "El protagonista es el personaje principal del libro."

        english_words = self._count_english_words(response)
        percentage = (english_words / len(response.split())) * 100

        self.assertLess(percentage, 5.0)

    def _count_english_words(self, text: str) -> int:
        """Count English words in text."""
        words = text.lower().split()
        return sum(1 for w in words if w in self.ENGLISH_WORDS)

    def calculate_drift_rate(self, response: str) -> float:
        """Calculate code-switching percentage."""
        words = response.split()
        if not words:
            return 0.0

        english_count = self._count_english_words(response)
        return (english_count / len(words)) * 100


def main():
    """Run language drift test."""
    print("Language Drift Detection Test")
    print("=" * 40)

    test = TestLanguageDrift()

    test_responses = [
        "El libro tiene many chapters interesting",
        "El protagonista vive en una casa muy grande",
    ]

    for resp in test_responses:
        drift = test.calculate_drift_rate(resp)
        status = "⚠️  DRIFT" if drift > 5.0 else "✅ OK"
        print(f"  {status}: {drift:.1f}% English")


if __name__ == "__main__":
    main()