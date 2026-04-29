"""
ML-based Content Classifier
Uses lightweight models for enhanced toxicity detection.
"""

import os
import sys
from typing import Dict, Optional


class ContentClassifier:
    """ML-based content classification for guardrails."""

    MODEL_NAME = "martin-ha/toxic-comment-model"

    def __init__(self, memory_threshold_mb: int = 14000):
        self.memory_threshold_mb = memory_threshold_mb
        self.model = None
        self.tokenizer = None
        self.available = False

    def _check_memory(self) -> bool:
        """Check if enough memory is available."""
        try:
            import subprocess
            result = subprocess.run(
                ['vm_stat'],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if 'Pages free:' in line:
                    free_pages = int(line.split(':')[1].strip().replace('.', ''))
                    free_mb = (free_pages * 4096) / (1024 * 1024)
                    return free_mb > self.memory_threshold_mb
        except Exception:
            pass
        return False

    def load(self) -> bool:
        """Load the classifier model."""
        if not self._check_memory():
            print("Not enough memory to load classifier")
            return False

        try:
            from transformers import pipeline
            self.classifier = pipeline(
                "text-classification",
                model=self.MODEL_NAME,
                device=-1,
                truncation=True,
                max_length=512
            )
            self.available = True
            print("✓ ML Classifier loaded")
            return True
        except Exception as e:
            print(f"Warning: Could not load classifier: {e}")
            return False

    def classify(self, text: str) -> Dict[str, float]:
        """
        Classify text for toxicity.
        Returns dict with categories and scores.
        """
        if not self.available:
            return {}

        try:
            result = self.classifier(text)
            return {item['label']: item['score'] for item in result}
        except Exception:
            return {}

    def is_toxic(self, text: str, threshold: float = 0.7) -> bool:
        """Check if text is toxic above threshold."""
        scores = self.classify(text)
        toxic_score = scores.get('toxic', 0.0)
        return toxic_score > threshold


def main():
    """Test the classifier."""
    classifier = ContentClassifier()

    print("Testing ML Content Classifier...")

    if classifier.load():
        test_texts = [
            "Hola, ¿cómo estás?",
            "Eres un idiota",
            "I want to kill myself",
        ]

        for text in test_texts:
            result = classifier.classify(text)
            print(f"\nText: {text}")
            print(f"Result: {result}")
            print(f"Toxic: {classifier.is_toxic(text)}")
    else:
        print("Classifier not available")


if __name__ == "__main__":
    main()