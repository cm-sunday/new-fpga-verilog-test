"""Test package for Silicon Dreams Module 1 and Module 2."""

import sys
from pathlib import Path

# ============================================================
# FIX: Ensure test directory is in sys.path
# ============================================================
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
    print(f"[FIX] Added to sys.path: {current_dir}")

__version__ = "2.0.0"