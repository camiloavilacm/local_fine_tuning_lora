#!/bin/bash
# =============================================================================
# setup.sh - One-click setup for Local Book Expert
# =============================================================================
# This script sets up the environment for running the fine-tuned model locally.
# Requirements: Apple Silicon (M1/M2/M3/M4), macOS
# =============================================================================

set -e

echo "🚀 Setting up Local Book Expert..."
echo "===================================="

# Check architecture
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    echo "⚠️  WARNING: This system is $ARCH"
    echo "   This project requires Apple Silicon (M1/M2/M3/M4)"
    echo "   The project may not work correctly on Intel Macs."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Detect Python
if [ -f "/usr/bin/python3" ]; then
    PYTHON="/usr/bin/python3"
else
    PYTHON="python3"
fi

echo "📦 Installing dependencies..."
$PYTHON -m pip install --upgrade pip --quiet 2>/dev/null || true

# Try ARM64 Python first, fall back to regular Python
if command -v arch &> /dev/null; then
    arch -arm64 $PYTHON -m pip install -r requirements.txt --quiet 2>/dev/null || \
        $PYTHON -m pip install -r requirements.txt --quiet
else
    $PYTHON -m pip install -r requirements.txt --quiet
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p data/raw data/processed data/samples adapters logs

# Check for model
if [ ! -d "adapters/v1" ]; then
    echo ""
    echo "⚠️  No trained model found in adapters/v1/"
    echo "   To train a model:"
    echo "   1. Place your EPUB book in data/raw/"
    echo "   2. Run: python3 scripts/convert.py"
    echo "   3. Run: python3 scripts/synthesize.py"
    echo "   4. Run: mlx_lm.lora --model HuggingFaceTB/SmolLM2-1.7B-Instruct --train --data ./data/processed"
    echo ""
fi

echo "===================================="
echo "✅ Setup complete!"
echo ""
echo "📖 Next steps:"
echo "   1. Place your EPUB in data/raw/"
echo "   2. Run: python3 scripts/convert.py <book.epub> data/processed/train.jsonl"
echo "   3. Run: python app.py"
echo ""
echo "🌐 The app will be available at: http://localhost:7860"
echo "===================================="