#!/usr/bin/env python3
"""
Batch Inference - Process multiple prompts with guardrails
SageMaker batch transform style.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent))
from guardrails import InputGuardrail, OutputGuardrail


class BatchGenerator:
    """Batch inference with guardrails."""

    def __init__(self, model_path: str, adapter_path: str):
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.input_guardrail = InputGuardrail()
        self.output_guardrail = OutputGuardrail()

    def load_model(self):
        """Load MLX model (placeholder - mlx_lm.load)."""
        print(f"Loading model: {self.model_path}")
        print(f"Loading adapters: {self.adapter_path}")
        pass

    def generate(self, prompt: str, max_tokens: int = 256) -> str:
        """Generate response for a single prompt."""
        filtered_prompt = self.input_guardrail.filter(prompt)

        if "Lo siento" in filtered_prompt:
            return filtered_prompt

        response = self._model_inference(filtered_prompt, max_tokens)

        filtered_response = self.output_guardrail.filter(response)

        return filtered_response

    def _model_inference(self, prompt: str, max_tokens: int) -> str:
        """Run model inference."""
        try:
            from mlx_lm import generate
            response = generate(
                self.model_path,
                self.adapter_path,
                prompt=prompt,
                max_tokens=max_tokens,
            )
            return response
        except Exception as e:
            print(f"Warning: Model inference unavailable: {e}")
            return "Error: Model not loaded"

    def process_file(self, input_path: str, output_path: str) -> int:
        """Process batch prompts from file."""
        if not Path(input_path).exists():
            print(f"Error: Input file not found: {input_path}")
            return 1

        results = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                data = json.loads(line)
                prompt = data.get('prompt', '')

                print(f"Processing {i+1}: {prompt[:50]}...")
                response = self.generate(prompt)

                results.append({
                    'prompt': prompt,
                    'response': response,
                    'success': 'Error' not in response
                })

        with open(output_path, 'w', encoding='utf-8') as f:
            for result in results:
                f.write(json.dumps(result, ensure_ascii=False) + '\n')

        print(f"Processed {len(results)} prompts")
        return 0


def main():
    if len(sys.argv) < 4:
        print("Usage: python batch_generate.py <model_path> <adapter_path> <input.jsonl> [output.jsonl]")
        sys.exit(1)

    model = sys.argv[1]
    adapter = sys.argv[2]
    input_file = sys.argv[3]
    output_file = sys.argv[4] if len(sys.argv) > 4 else "results/batch_results.jsonl"

    generator = BatchGenerator(model, adapter)
    generator.load_model()
    sys.exit(generator.process_file(input_file, output_file))


if __name__ == "__main__":
    main()