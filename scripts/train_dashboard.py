#!/usr/bin/env python3
"""
Train Dashboard - SageMaker-style Terminal UI
Displays real-time training metrics with thermal monitoring.
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict


class TrainDashboard:
    """Terminal dashboard for training monitoring."""

    TEMP_THRESHOLD = 95
    TEMP_PAUSE_DURATION = 60

    def __init__(self):
        self.iteration = 0
        self.total_iterations = 1000
        self.loss = 0.0
        self.val_loss = 0.0
        self.perplexity = 0.0
        self.blocked_requests = 0
        self.code_switching = 0.0
        self.start_time = None
        self.paused = False

    def get_system_temp(self) -> Optional[float]:
        """Get M3 CPU temperature."""
        try:
            result = subprocess.run(
                ['osx-cpu-temp', '-c'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass

        try:
            result = subprocess.run(
                ['pmset', '-g', 'therm'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'CPU' in line:
                        parts = line.split()
                        for i, p in enumerate(parts):
                            if p.isdigit():
                                return float(p)
        except Exception:
            pass

        return None

    def get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage stats."""
        try:
            result = subprocess.run(
                ['vm_stat'],
                capture_output=True,
                text=True,
                timeout=5
            )

            free = 0
            active = 0

            for line in result.stdout.split('\n'):
                if 'Pages free:' in line:
                    free = int(line.split(':')[1].strip().replace('.', '')) * 4
                elif 'Pages active:' in line:
                    active = int(line.split(':')[1].strip().replace('.', '')) * 4

            total = 16 * 1024
            used = active / 1024
            available = (total - used)

            return {'used_mb': used, 'available_mb': available, 'total_mb': total}
        except Exception:
            return {'used_mb': 0, 'available_mb': 0, 'total_mb': 16384}

    def check_thermal_throttle(self) -> bool:
        """Check if thermal throttling is needed."""
        temp = self.get_system_temp()
        if temp and temp > self.TEMP_THRESHOLD:
            print(f"\n⚠️  Temperature {temp:.1f}°C exceeds threshold!")
            print(f"   Pausing for {self.TEMP_PAUSE_DURATION} seconds...")
            time.sleep(self.TEMP_PAUSE_DURATION)
            return True
        return False

    def calculate_eta(self) -> str:
        """Calculate estimated time to completion."""
        if self.start_time and self.iteration > 0:
            elapsed = time.time() - self.start_time
            rate = self.iteration / elapsed
            remaining = self.total_iterations - self.iteration
            eta_seconds = remaining / rate if rate > 0 else 0

            hours = int(eta_seconds // 3600)
            minutes = int((eta_seconds % 3600) // 60)
            return f"{hours:02d}:{minutes:02d}"
        return "--:--"

    def render(self) -> None:
        """Render the dashboard."""
        os.system('clear' if os.name == 'posix' else 'cls')

        progress = self.iteration / self.total_iterations if self.total_iterations > 0 else 0
        progress_bar = self._create_progress_bar(progress)

        memory = self.get_memory_usage()
        temp = self.get_system_temp()
        temp_str = f"{temp:.1f}°C" if temp else "N/A"

        eta = self.calculate_eta()

        print("┌" + "─" * 64 + "┐")
        print(f"│  📚 FINE-TUNING: SmolLM2-1.7B on Spanish Book             │")
        print("├" + "─" * 64 + "┤")
        print(f"│  Epoch: 1/1    Iter: {self.iteration:4d}/{self.total_iterations}    ETA: {eta}           │")
        print("├" + "─" * 64 + "┤")
        print(f"│  Loss: {self.loss:.4f}  |  Val Loss: {self.val_loss:.4f}  |  PPL: {self.perplexity:.2f}   │")
        print("├" + "─" * 64 + "┤")
        print(f"│  RAM: {memory['used_mb']:.1f}/{memory['total_mb']:.0f} GB  |  Temp: {temp_str}  |  Blocked: {self.blocked_requests}    │")
        print("├" + "─" * 64 + "┤")
        print(f"│  Code-Switching: {self.code_switching:.1f}%                                     │")
        print("├" + "─" * 64 + "┤")
        print(f"│  {progress_bar} {progress*100:.1f}%  │")
        print("└" + "─" * 64 + "┘")

    def _create_progress_bar(self, progress: float, width: int = 58) -> str:
        """Create a progress bar string."""
        filled = int(progress * width)
        bar = "█" * filled + "░" * (width - filled)
        return bar

    def update(self, iteration: int, loss: float, val_loss: float = 0.0) -> None:
        """Update dashboard with new metrics."""
        self.iteration = iteration
        self.loss = loss
        self.val_loss = val_loss
        self.perplexity = 2.71828 ** val_loss if val_loss > 0 else 0.0

        if self.start_time is None:
            self.start_time = time.time()

        self.check_thermal_throttle()
        self.render()

    def load_from_log(self, log_file: str) -> None:
        """Load metrics from training log file."""
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    if 'loss' in data:
                        self.iteration = data.get('iteration', 0)
                        self.loss = data.get('loss', 0.0)
                        self.val_loss = data.get('val_loss', 0.0)
        except Exception:
            pass


def main():
    """Main dashboard loop."""
    dashboard = TrainDashboard()

    log_file = sys.argv[1] if len(sys.argv) > 1 else "logs/training.log"

    print("Starting training dashboard...")
    print(f"Monitoring: {log_file}")
    print("Press Ctrl+C to exit\n")

    while True:
        try:
            dashboard.load_from_log(log_file)
            time.sleep(2)
        except KeyboardInterrupt:
            print("\nDashboard stopped.")
            break


if __name__ == "__main__":
    main()