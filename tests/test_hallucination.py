#!/usr/bin/env python3
"""Hallucination detection test."""

import json
import sys
import unittest
from pathlib import Path


class TestHallucination(unittest.TestCase):
    """Test hallucination detection."""

    NON_EXISTENT_ENTITIES = [
        "¿Quién es María García?",
        "¿Qué pasó en la batalla de 1890?",
        "¿Cuál es el secreto de la fórmula X?",
    ]

    CORRECT_REJECTION_PHRASES = [
        "no mentioned",
        "no aparece",
        "no encontrado",
        "no tengo información",
        "not mentioned",
        "no sé",
    ]

    def test_correct_rejection(self):
        """Test model correctly rejects unknown entities."""
        response = "Lo siento, ese personaje no aparece en el libro."

        is_rejection = any(
            phrase.lower() in response.lower()
            for phrase in self.CORRECT_REJECTION_PHRASES
        )

        self.assertTrue(is_rejection)

    def test_hallucination_detection(self):
        """Test hallucination is detected."""
        response = "María García es la protagonista del libro, ella vive en el bosque y tiene 10 años."

        is_hallucination = not any(
            phrase.lower() in response.lower()
            for phrase in self.CORRECT_REJECTION_PHRASES
        )

        self.assertTrue(is_hallucination)


def main():
    """Run hallucination test."""
    entities = TestHallucination.NON_EXISTENT_ENTITIES

    print("Hallucination Detection Test")
    print("=" * 40)
    print(f"Non-existent entities to test: {len(entities)}")

    for i, entity in enumerate(entities):
        print(f"  {i+1}. {entity}")

    print("\nExpected behavior:")
    print("  - Correct: Model says entity not in book")
    print("  - Hallucination: Model invents details")


if __name__ == "__main__":
    main()