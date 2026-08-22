#!/usr/bin/env python3
"""Debug script to verify imports work."""

import sys
import os
from pathlib import Path

print("=" * 60)
print("Debug: Checking Python imports")
print("=" * 60)

print(f"Current directory: {os.getcwd()}")
print(f"Python version: {sys.version}")
print(f"sys.path: {sys.path}")
print()

# Try importing fault_injection
try:
    import fault_injection
    print(f"[OK] fault_injection found at: {fault_injection.__file__}")
except ImportError as e:
    print(f"[FAIL] fault_injection not found: {e}")

# Try importing harness
try:
    import harness
    print(f"[OK] harness found at: {harness.__file__}")
except ImportError as e:
    print(f"[FAIL] harness not found: {e}")

# Try importing specific test
try:
    import fault_injection.floor_b2_reset
    print(f"[OK] floor_b2_reset found")
except ImportError as e:
    print(f"[FAIL] floor_b2_reset not found: {e}")

print()
print("=" * 60)