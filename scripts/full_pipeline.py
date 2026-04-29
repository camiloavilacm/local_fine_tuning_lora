#!/usr/bin/env python3
"""
Full Pipeline - Chains all preprocessing, training, and evaluation steps
SageMaker-style automated pipeline.
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from datetime import datetime


class FullPipeline:
    """Orchestrate the complete fine-tuning pipeline."""

    STEPS = [
        ("Step 1: Convert EPUB to JSONL", "convert.py"),
        ("Step 2: Scrub PII", "clean_pii.py"),
        ("Step 3: Synthesize Q&A Pairs", "synthesize.py"),
        ("Step 4: Setup MLX", "setup_mlx.py"),
        ("Step 5: Train Model", "mlx_lm.lora"),
        ("Step 6: Test Model", "mlx_lm.lora --test"),
    ]

    def __init__(self, project_root: str = ".."):
        self.project_root = Path(project_root)
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.start_time = datetime.now()

    def run_step(self, step_name: str, command: list, log_file: str) -> bool:
        """Run a single pipeline step."""
        print(f"\n{'=' * 60}")
        print(f"▶ {step_name}")
        print(f"{'=' * 60}")

        log_path = self.logs_dir / log_file
        with open(log_path, 'w') as log:
            try:
                result = subprocess.run(
                    command,
                    cwd=self.project_root,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                if result.returncode == 0:
                    print(f"✓ {step_name} completed successfully")
                    return True
                else:
                    print(f"✗ {step_name} failed with code {result.returncode}")
                    return False

            except Exception as e:
                print(f"✗ Error running {step_name}: {e}")
                return False

    def generate_samples(self) -> bool:
        """Generate sample data for testing."""
        samples = [
            {"text": "<|user|>¿Quién es el personaje principal?<|assistant|>El protagonista es Lucas, un niño curioso que explora el bosque."},
            {"text": "<|user|>¿Qué pasó en el capítulo 1?<|assistant|>Lucas descubrió una puerta secreta en el old árbol del bosque."},
            {"text": "<|user|>¿Dónde vive Lucas?<|assistant|>Lucas vive en una pequeña aldea rodeada de montañas."},
            {"text": "<|user|>¿Cuál es el propósito del libro?<|assistant|>El libro enseña sobre la amistad, la valentía y la naturaleza."},
            {"text": "<|user|>¿Qué aprende Lucas en su aventura?<|admin|>Lucas aprende que la verdadera magia está en confiar en sus amigos."},
        ]

        output = self.project_root / "data" / "samples" / "sample_train.jsonl"
        output.parent.mkdir(exist_ok=True)

        with open(output, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')

        print(f"✓ Generated {len(samples)} sample Q&A pairs")
        return True

    def run(self, interactive: bool = True) -> bool:
        """Run the full pipeline."""
        print("\n" + "=" * 60)
        print("🚀 FULL FINE-TUNING PIPELINE")
        print("=" * 60)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project: {self.project_root}")
        print("=" * 60)

        if interactive:
            print("\n⚠️  Running in INTERACTIVE mode (manual confirmation)")
            print("   For automatic mode, run with --auto flag")
        else:
            print("\n▶ Running in AUTOMATIC mode")

        self.generate_samples()

        if interactive:
            choice = input("\nContinue with pipeline? (y/n): ")
            if choice.lower() != 'y':
                print("Pipeline cancelled.")
                return False

        success = True

        for step_name, script in self.STEPS:
            if not self.run_step(step_name, ["python3", f"scripts/{script}"], f"{script}.log"):
                success = False
                if interactive:
                    cont = input("Continue despite failure? (y/n): ")
                    if cont.lower() != 'y':
                        break

        elapsed = datetime.now() - self.start_time
        print(f"\n{'=' * 60}")
        print(f"{'✅ PIPELINE COMPLETED' if success else '❌ PIPELINE FAILED'}")
        print(f"Elapsed time: {elapsed}")
        print("=" * 60)

        return success


def main():
    interactive = "--auto" not in sys.argv

    pipeline = FullPipeline()
    success = pipeline.run(interactive=interactive)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()