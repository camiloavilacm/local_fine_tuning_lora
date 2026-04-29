#!/usr/bin/env python3
"""
Model Weight Verification
Generate SHA-256 hash of adapter weights for provenance verification.
"""

import hashlib
import json
import os
import sys
from pathlib import Path
from datetime import datetime


def generate_sha256(file_path: str) -> str:
    """Generate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()

    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)

    return sha256_hash.hexdigest()


def verify_weights(adapter_path: str, manifest_path: str = "manifest.json") -> bool:
    """Verify adapter weights against manifest."""
    adapter_dir = Path(adapter_path)

    if not adapter_dir.exists():
        print(f"Error: Adapter path not found: {adapter_path}")
        return False

    safetensors_files = list(adapter_dir.glob("*.safetensors"))

    if not safetensors_files:
        print(f"Warning: No .safetensors files found in {adapter_path}")
        return False

    results = {}

    print("Generating hashes...")
    for file in safetensors_files:
        file_hash = generate_sha256(str(file))
        results[file.name] = {
            "hash": file_hash,
            "size_bytes": file.stat().st_size,
            "timestamp": datetime.now().isoformat()
        }
        print(f"  {file.name}: {file_hash[:16]}...")

    manifest = {
        "adapter_path": str(adapter_path),
        "generated_at": datetime.now().isoformat(),
        "algorithm": "sha256",
        "files": results,
        "total_files": len(results),
        "total_size_bytes": sum(f["size_bytes"] for f in results.values())
    }

    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)

    print(f"\n✓ Manifest saved to {manifest_path}")
    return True


def main():
    adapter_path = sys.argv[1] if len(sys.argv) > 1 else "./adapters/v1"
    manifest_path = sys.argv[2] if len(sys.argv) > 2 else "manifest.json"

    success = verify_weights(adapter_path, manifest_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()