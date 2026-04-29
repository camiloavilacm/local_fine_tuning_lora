#!/usr/bin/env python3
"""
MLX Setup for M3 Mac
Configures memory limits and hardware safeguards.
"""

import os
import sys
import platform


def check_metal_availability() -> bool:
    """Check if Metal is available."""
    try:
        import mlx.core as mx
        return mx.metal.is_available()
    except Exception:
        return False


def set_memory_limit(percent: float = 0.8) -> None:
    """Set MLX metal cache limit to prevent OS instability."""
    try:
        import mlx.core as mx

        total_memory = get_total_memory_mb()
        cache_limit = int(total_memory * percent)

        mx.metal.set_cache_limit(cache_limit * 1024 * 1024)
        print(f"✓ MLX cache limit set to {cache_limit} MB ({percent*100:.0f}% of RAM)")
    except Exception as e:
        print(f"Warning: Could not set cache limit: {e}")


def get_total_memory_mb() -> float:
    """Get total system memory in MB."""
    try:
        import subprocess
        result = subprocess.run(
            ['sysctl', '-n', 'hw.memsize'],
            capture_output=True,
            text=True
        )
        return int(result.stdout.strip()) / (1024 * 1024)
    except Exception:
        return 16384


def get_free_memory_mb() -> float:
    """Get currently free memory in MB."""
    try:
        import subprocess
        result = subprocess.run(
            ['vm_stat'],
            capture_output=True,
            text=True
        )
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Pages free:' in line:
                free_pages = int(line.split(':')[1].strip().replace('.', ''))
                return free_pages * 4096 / (1024 * 1024)
    except Exception:
        return 8192
    return 8192


def check_system_health() -> dict:
    """Check current system health."""
    health = {
        'platform': platform.system(),
        'total_memory_mb': get_total_memory_mb(),
        'free_memory_mb': get_free_memory_mb(),
        'metal_available': check_metal_availability(),
    }
    return health


def print_system_info() -> None:
    """Print system information."""
    health = check_system_health()

    print("=" * 50)
    print("M3 System Configuration")
    print("=" * 50)
    print(f"Platform: {health['platform']}")
    print(f"Total RAM: {health['total_memory_mb']:.0f} MB")
    print(f"Free RAM: {health['free_memory_mb']:.0f} MB")
    print(f"Metal Available: {health['metal_available']}")
    print("=" * 50)


def initialize_mlx() -> None:
    """Initialize MLX with memory safeguards."""
    print_system_info()

    if not check_metal_availability():
        print("Error: Metal not available. Cannot use MLX.")
        sys.exit(1)

    set_memory_limit(0.8)

    free = get_free_memory_mb()
    if free < 4000:
        print("Warning: Less than 4GB free RAM. Consider closing other apps.")
    else:
        print(f"✓ Sufficient free memory: {free:.0f} MB")


if __name__ == "__main__":
    initialize_mlx()