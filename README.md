# Local Book Expert - Fine-Tuned LLM on Apple Silicon

A local fine-tuning project for creating a personalized book chatbot using MLX + LoRA on Apple Silicon (M1/M2/M3/M4).

## 🛠️ Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/camiloavilacm/local_fine_tuning_lora.git
cd local_fine_tuning_lora

# 2. Setup (one-click)
bash setup.sh

# 3. Place your EPUB in data/raw/
#    Then process: python3 scripts/convert.py data/raw/yourbook.epub data/processed/train.jsonl

# 4. Train the model (optional - skip if you already have trained adapters)
mlx_lm.lora --model HuggingFaceTB/SmolLM2-1.7B-Instruct --train --data ./data/processed \
  --adapter-path ./adapters/v1 --iters 1000

# 5. Run the Chat UI
python app.py
```

🌐 **Access:** http://localhost:7860

---

## Features

### Core Training
- **MLX + LoRA** - Efficient fine-tuning on M3 Mac (16GB RAM)
- **SmolLM2-1.7B-Instruct-4bit** - Memory-efficient base model
- **Spanish EPUB** - Process books with `convert.py` and `synthesize.py`

### SageMaker-Style Features
- **Train Dashboard** - Real-time terminal UI with metrics
- **WandB Integration** - Experiment tracking
- **Checkpointing** - Save every 100 iterations
- **Model Versioning** - `adapters/v1/`, `adapters/v2/`
- **Full Pipeline** - Automated preprocess → train → test

### Safety & Guardrails
- **Input Guardrail** - Block toxic/inappropriate prompts
- **Output Guardrail** - Filter model responses
- **P.I.I. Scrubber** - Remove personal data from training data
- **Content Blocklist** - Spanish + English keywords

### Hardware Safety
- **Thermal Monitoring** - Pause if M3 > 95°C
- **VRAM Safeguard** - Prevent WindowServer crashes
- **Memory Guard** - 80% cache limit

### Security & Provenance
- **SHA-256 Hash Verification** - Verify adapter integrity
- **Model Card** - Metadata with training details

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run full pipeline (interactive)
python3 scripts/full_pipeline.py

# 3. Or run steps manually:
python3 scripts/convert.py data/raw/book.epub data/processed/train.jsonl
python3 scripts/clean_pii.py data/processed/train.jsonl data/processed/train_clean.jsonl
python3 scripts/synthesize.py data/processed/train_clean.jsonl data/processed/train_qa.jsonl
python3 scripts/setup_mlx.py

# 4. Train
mlx_lm.lora --model mlx-community/SmolLM2-1.7B-Instruct-4bit \
  --data ./data/processed \
  --adapter-path ./adapters/v1 \
  --iterations 1000 --rank 16 --batch-size 1 --learning-rate 1e-4

# 5. Test
mlx_lm.lora --model mlx-community/SmolLM2-1.7B-Instruct-4bit \
  --adapter-path ./adapters/v1 \
  --data ./data/processed --test

# 6. Generate
mlx_lm.generate --model mlx-community/SmolLM2-1.7B-Instruct-4bit \
  --adapter-path ./adapters/v1 \
  --prompt "¿Quién es el protagonista?"
```

## Project Structure

```
local_fine_tuning_lora/
├── scripts/
│   ├── convert.py              # EPUB → JSONL
│   ├── synthesize.py           # Text → Q&A pairs
│   ├── clean_pii.py            # P.I.I. scrubber
│   ├── setup_mlx.py            # Hardware setup
│   ├── train_dashboard.py      # Terminal UI
│   ├── full_pipeline.py        # Auto pipeline
│   ├── batch_generate.py      # Batch inference
│   ├── serve_model.py          # Local endpoint
│   ├── hyperparam_search.py    # Grid search
│   ├── verify_weights.py       # Hash verification
│   └── guardrails/             # Safety filters
├── data/
│   ├── processed/              # Training data
│   └── samples/                # Sample Q&A
├── config/
│   ├── train_config.yaml
│   └── guardrails_config.yaml
├── tests/
├── evals/                      # Evaluation results
└── adapters/                  # Model weights
```

## Configuration

### Training (train_config.yaml)
```yaml
model:
  name: mlx-community/SmolLM2-1.7B-Instruct-4bit

lora:
  rank: 16
  alpha: 16

training:
  iterations: 1000
  batch_size: 1
  learning_rate: 1e-4
```

### Guardrails (guardrails_config.yaml)
```yaml
enabled: true
filters:
  violence:
    enabled: true
  self_harm:
    priority: high
```

## Evaluation Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Test Loss | < 2.0 | Lower is better |
| Test Perplexity | < 40 | Exponential of loss |
| Loss Delta | < 0.5 | Val Loss - Train Loss |
| Code-Switching | < 5% | English in Spanish |
| Hallucination | < 10% | Made-up facts |

## Tests

```bash
python3 -m pytest tests/ -v
```

## License & Copyright

**MIT License** - See LICENSE file.

> ⚠️ **Important**: The fine-tuned adapters are for personal/educational use only. The original book content is copyrighted. Do not distribute the book text or derived datasets.

## Requirements

- macOS with Apple Silicon (M1/M2/M3)
- 16GB RAM minimum
- Python 3.9+
- Xcode Command Line Tools