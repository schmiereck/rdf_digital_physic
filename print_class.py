#!/usr/bin/env python3
"""Print the DisplacementConsistencyFitness class from src/new_fitness.py."""

import sys
import os

# Force UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from new_fitness import DisplacementConsistencyFitness

cls = DisplacementConsistencyFitness

print("=" * 72)
print(f"Class: {cls.__name__}")
print("=" * 72)
print()

print("-" * 72)
print("FULL CLASS SOURCE CODE")
print("-" * 72)
print(cls.__doc__)
print()
print("=" * 72)
print("INIT METHOD")
print("=" * 72)
print()
import inspect
print(inspect.getsource(cls.__init__))
print()
print("=" * 72)
print("__call__ METHOD")
print("=" * 72)
print()
print(inspect.getsource(cls.__call__))
print()
print("=" * 72)
print("_compute_conservation_score METHOD")
print("=" * 72)
print()
print(inspect.getsource(cls._compute_conservation_score))
print()
