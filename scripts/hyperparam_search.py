#!/usr/bin/env python3
"""
Hyperparameter Search
Grid search for LoRA hyperparameters.
"""

import itertools
import subprocess
import sys
from pathlib import Path
from datetime import datetime


class HyperparameterSearch:
    """Grid search for optimal hyperparameters."""

    PARAM_GRID = {
        'rank': [8, 16, 32],
        'learning_rate': [1e-4, 5e-4, 1e-3],
        'batch_size': [1, 2],
    }

    ITERATIONS = 500
    MODEL = "mlx-community/SmolLM2-1.7B-Instruct-4bit"

    def __init__(self, data_path: str, output_dir: str):
        self.data_path = data_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results = []

    def run_combination(self, params: dict) -> dict:
        """Run training with given parameters."""
        cmd = [
            "mlx_lm.lora",
            "--model", self.MODEL,
            "--data", self.data_path,
            "--iterations", str(self.ITERATIONS),
            "--rank", str(params['rank']),
            "--learning-rate", str(params['learning_rate']),
            "--batch-size", str(params['batch_size']),
            "--adapter-path", str(self.output_dir / f"rank{params['rank']}_lr{params['learning_rate']}"),
        ]

        print(f"\nRunning: {params}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

            loss = self._extract_loss(result.stdout)
            perplexity = self._extract_perplexity(result.stdout)

            return {
                'params': params,
                'loss': loss,
                'perplexity': perplexity,
                'success': loss is not None
            }
        except Exception as e:
            return {
                'params': params,
                'loss': None,
                'perplexity': None,
                'success': False,
                'error': str(e)
            }

    def _extract_loss(self, output: str) -> float:
        """Extract loss from output."""
        for line in output.split('\n'):
            if 'loss' in line.lower():
                try:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if 'loss' in p.lower() and i + 1 < len(parts):
                            return float(parts[i + 1])
                except Exception:
                    pass
        return None

    def _extract_perplexity(self, output: str) -> float:
        """Extract perplexity from output."""
        for line in output.split('\n'):
            if 'perplexity' in line.lower():
                try:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if 'perplexity' in p.lower() and i + 1 < len(parts):
                            return float(parts[i + 1])
                except Exception:
                    pass
        return None

    def search(self):
        """Run grid search."""
        combinations = list(itertools.product(
            self.PARAM_GRID['rank'],
            self.PARAM_GRID['learning_rate'],
            self.PARAM_GRID['batch_size']
        ))

        print(f"Running {len(combinations)} parameter combinations")
        print(f"Each with {self.ITERATIONS} iterations")
        print(f"Estimated time: {len(combinations) * 0.5:.1f} hours\n")

        for rank, lr, bs in combinations:
            params = {'rank': rank, 'learning_rate': lr, 'batch_size': bs}
            result = self.run_combination(params)
            self.results.append(result)

        self.save_results()

    def save_results(self):
        """Save results to file."""
        output = self.output_dir / f"hyperparam_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(output, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n✓ Results saved to {output}")

        best = min([r for r in self.results if r['success']], key=lambda x: x['perplexity'])
        print(f"\n🏆 Best parameters:")
        print(f"   Rank: {best['params']['rank']}")
        print(f"   LR: {best['params']['learning_rate']}")
        print(f"   Batch: {best['params']['batch_size']}")
        print(f"   Perplexity: {best['perplexity']:.2f}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python hyperparam_search.py <data_path> <output_dir>")
        sys.exit(1)

    search = HyperparameterSearch(sys.argv[1], sys.argv[2])
    search.search()


if __name__ == "__main__":
    main()