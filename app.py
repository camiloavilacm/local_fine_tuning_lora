#!/usr/bin/env python3
"""
Entry point for the Book Expert Chat UI.
Run: python app.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from chat_ui import main

if __name__ == "__main__":
    main()