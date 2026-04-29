#!/usr/bin/env python3
"""
Synthesize Q&A Pairs from Book Content
Generates training data for fine-tuning.
"""

import json
import random
import re
import sys
from pathlib import Path
from typing import List, Dict


class QASynthesizer:
    """Generate Q&A pairs from text content."""

    QUESTION_STARTERS = [
        "¿Qué",
        "¿Quién",
        "¿Cómo",
        "¿Por qué",
        "¿Cuándo",
        "¿Dónde",
        "¿Cuál",
        "¿Cuántos",
    ]

    def __init__(self, min_sentence_length: int = 20):
        self.min_sentence_length = min_sentence_length

    def extract_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) >= self.min_sentence_length]

    def extract_entities(self, text: str) -> List[str]:
        """Extract potential named entities (simple pattern)."""
        patterns = [
            r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b',
            r'\b[A-Z][a-z]+-(?:[A-Z][a-z]+)+\b',
        ]

        entities = []
        for pattern in patterns:
            entities.extend(re.findall(pattern, text))

        return list(set(entities))

    def generate_question(self, sentence: str, q_type: str) -> str:
        """Generate a question from a sentence."""
        templates = {
            'summary': f"Resume lo siguiente: {sentence[:100]}...",
            'detail': f"¿Qué información importante contiene este texto?",
            'character': "¿Qué personajes aparecen en esta sección?",
            'event': "¿Qué eventos se describen aquí?",
        }
        return templates.get(q_type, templates['summary'])

    def generate_qa_pairs(self, text: str, num_pairs: int = 3) -> List[Dict[str, str]]:
        """Generate Q&A pairs from text."""
        sentences = self.extract_sentences(text)
        if not sentences:
            return []

        pairs = []
        used_sentences = set()

        for _ in range(min(num_pairs, len(sentences))):
            available = [s for i, s in enumerate(sentences) if i not in used_sentences]
            if not available:
                break

            sentence = random.choice(available)
            used_sentences.add(sentences.index(sentence))

            q_types = ['summary', 'detail', 'character', 'event']
            q_type = random.choice(q_types)
            question = self.generate_question(sentence, q_type)

            prompt = f"<|user|>{question}<|assistant|>{sentence}"
            pairs.append({"text": prompt})

        return pairs

    def process_file(self, input_path: str, output_path: str, pairs_per_chapter: int = 3) -> int:
        """Process JSONL and add Q&A pairs."""
        if not Path(input_path).exists():
            print(f"Error: File not found: {input_path}")
            return 1

        all_pairs = []
        count = 0

        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                data = json.loads(line)
                text = data.get('text', '')

                if 'content:' in text.lower():
                    content = text.split('content:')[-1].strip()
                else:
                    content = text

                pairs = self.generate_qa_pairs(content, pairs_per_chapter)
                all_pairs.extend(pairs)
                count += 1

        with open(output_path, 'w', encoding='utf-8') as f:
            for pair in all_pairs:
                f.write(json.dumps(pair, ensure_ascii=False) + '\n')

        print(f"Generated {len(all_pairs)} Q&A pairs from {count} chapters")
        return 0


def main():
    if len(sys.argv) < 3:
        print("Usage: python synthesize.py <input.jsonl> <output.jsonl> [pairs_per_chapter]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    pairs = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    synthesizer = QASynthesizer()
    sys.exit(synthesizer.process_file(input_file, output_file, pairs))


if __name__ == "__main__":
    main()