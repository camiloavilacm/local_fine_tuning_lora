# Project Implementation Guide

## Goal
Local fine-tuning of SmolLM2-1.7B-Instruct-4bit on Spanish EPUB book (El_gran_libro_de_Lucia.epub) using MLX + LoRA on Apple Silicon M3 (16GB RAM).

## Constraints & Preferences
- Python3 (not python)
- Spanish language for all output
- SmolLM2-1.7B-Instruct-4bit model
- Lowest RAM usage (willing to wait longer)
- LoRA rank: 16, iterations: 1000, batch size: 1, learning rate: 1e-4

---

## Implementation Phases

### Phase 1: Project Setup
- [x] Create directory structure
- [x] Create requirements.txt
- [x] Create .gitignore
- [x] Create LICENSE

### Phase 2: Data Processing
- [x] Create scripts/convert.py (EPUB → JSONL)
- [x] Create scripts/synthesize.py (Text → Q&A)
- [x] Create tests/test_convert.py
- [x] Create tests/test_synthesize.py
- [x] Run convert.py on El_gran_libro_de_Lucia.epub (73 chapters → 219 Q&A pairs)

### Phase 3: Privacy & PII
- [x] Create scripts/clean_pii.py
- [x] Create data/samples/sample_train.jsonl

### Phase 4: SageMaker-Style Features
- [x] Create scripts/train_dashboard.py
- [x] Create scripts/full_pipeline.py
- [x] Create config/train_config.yaml
- [x] Create config/guardrails_config.yaml

### Phase 5: Guardrails
- [x] Create scripts/guardrails/__init__.py
- [x] Create scripts/guardrails/blocklist.py
- [x] Create scripts/guardrails/input_filter.py
- [x] Create scripts/guardrails/output_filter.py
- [x] Create scripts/guardrails/classifier.py
- [x] Create tests/test_guardrails.py

### Phase 6: Inference
- [x] Create scripts/batch_generate.py
- [x] Create scripts/serve_model.py
- [x] Create scripts/hyperparam_search.py

### Phase 7: Hardware Safety
- [x] Create scripts/setup_mlx.py

### Phase 8: Security & Provenance
- [x] Create scripts/verify_weights.py

### Phase 9: Evaluation
- [x] Create tests/test_rag_eval.py
- [x] Create tests/test_hallucination.py
- [x] Create tests/test_language_drift.py
- [x] Create evals/before_after_comparison.txt

### Phase 10: Documentation
- [x] Create README.md

---

## Key Files

| File | Purpose |
|------|---------|
| `scripts/convert.py` | EPUB → JSONL converter |
| `scripts/synthesize.py` | Q&A pair generator |
| `scripts/clean_pii.py` | P.I.I. scrubber |
| `scripts/train_dashboard.py` | Real-time metrics UI |
| `scripts/full_pipeline.py` | Automated pipeline |
| `scripts/guardrails/` | Content filtering |
| `config/train_config.yaml` | Training configuration |
| `config/guardrails_config.yaml` | Guardrail settings |

---

## Training Command

```bash
mlx_lm.lora \
  --model mlx-community/SmolLM2-1.7B-Instruct-4bit \
  --data ./data/processed \
  --adapter-path ./adapters/v1 \
  --iterations 1000 \
  --rank 16 \
  --batch-size 1 \
  --learning-rate 1e-4
```

---

## Evaluation Metrics

### Primary Metrics
| Metric | Target | Frequency |
|--------|--------|-----------|
| Training Loss | Decreasing | Every 10 iterations |
| Validation Loss | Decreasing | Every 100 iterations |
| Loss Delta | < 0.5 | Every 100 iterations |
| Test Perplexity | < 40 | After training |

### Quality Metrics (Post-Training)
| Metric | Target | Test File |
|--------|--------|-----------|
| Code-Switching Rate | < 5% | test_language_drift.py |
| Semantic Similarity | > 70% | test_rag_eval.py |
| Hallucination Rate | < 10% | test_hallucination.py |

---

## Dependencies

```
mlx-lm
mlx-explore
wandb
tqdm
ebooklib
beautifulsoup4
numpy
safetensors
```

---

## Current Status

✅ All core scripts created
✅ All test files created (20 passing)
✅ All configuration files created
✅ Documentation complete
✅ EPUB converted (73 chapters → 219 Q&A pairs)
✅ P.I.I. scrubbed
✅ Training complete (1000 iterations)
✅ Checkpoints saved (every 100 iterations)
✅ Model metadata created
✅ SHA-256 hash verification complete

---

## Training Results

| Metric | Value |
|--------|-------|
| Iterations | 1000 |
| Train Loss | 0.170 |
| Validation Loss | 2.545 |
| Val Perplexity | 12.75 |
| Peak Memory | 4.44 GB |
| Checkpoints | 10 (every 100 iters) |

---

## Files Generated

- `adapters/v1/adapters.safetensors` - Final model weights
- `adapters/v1/metadata.json` - Model card
- `manifest.json` - SHA-256 verification