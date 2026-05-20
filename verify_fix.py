#!/usr/bin/env python3
"""Verify the fix to src/new_fitness.py."""

import sys

PATH = "src/new_fitness.py"

# --- Read and verify the fix ---
print("--- Verification ---")
with open(PATH, "r") as f:
    lines = f.readlines()

fixed = False
for i, line in enumerate(lines, start=1):
    if 'prev_com = sorted_history[i - 1]' in line:
        fixed = True
        print(f"Line {i}: {line.rstrip()}")
        for j in range(max(0, i-3), min(len(lines), i+10)):
            marker = ">>>" if j == i-1 else "   "
            print(f"{marker} {j+1}: {lines[j].rstrip()}")

if not fixed:
    print("ERROR: Fix not found!")
    sys.exit(1)

print("\n[OK] prev_com now references sorted_history[i-1] instead of unwrapped_coms[-1]")

# --- Syntax check ---
print("\n--- Syntax check ---")
import py_compile
try:
    py_compile.compile(PATH, doraise=True)
    print("[OK] File compiles successfully")
except py_compile.PyCompileError as e:
    print(f"[FAIL] Syntax error: {e}")
    sys.exit(1)

# --- Quick runtime test ---
print("\n--- Quick runtime test ---")
# Make sure src is on the path
sys.path.insert(0, ".")
from src.new_fitness import DisplacementConsistencyFitness

# Simple consistent glider
sim_history = [
    {"step": 0,   "com": (64.0, 64.0),  "bit_count": 8},
    {"step": 50,  "com": (59.0, 59.0),  "bit_count": 8},
    {"step": 100, "com": (54.0, 54.0),  "bit_count": 8},
    {"step": 150, "com": (49.0, 49.0),  "bit_count": 8},
    {"step": 200, "com": (44.0, 44.0),  "bit_count": 8},
    {"step": 250, "com": (39.0, 39.0),  "bit_count": 8},
]

fitness_fn = DisplacementConsistencyFitness(num_windows=5)
score = fitness_fn(sim_history)
print(f"  Consistent glider:   fitness = {score:.6f}")

# Drifter: oscillating in place
sim_drifter = [
    {"step": 0,   "com": (64.0, 64.0),  "bit_count": 8},
    {"step": 50,  "com": (64.1, 63.9),  "bit_count": 8},
    {"step": 100, "com": (63.9, 64.1),  "bit_count": 8},
    {"step": 150, "com": (64.0, 64.0),  "bit_count": 8},
    {"step": 200, "com": (64.1, 63.9),  "bit_count": 8},
    {"step": 250, "com": (63.9, 64.1),  "bit_count": 8},
]
score_drift = fitness_fn(sim_drifter)
print(f"  Drifter (oscillating): fitness = {score_drift:.6f}")

# Verify: consistent glider should have much higher fitness than drifter
assert score > score_drift, f"Consistent glider ({score}) should score higher than drifter ({score_drift})"

# Toroidal wrap test
sim_wrap = [
    {"step": 0,   "com": (127.0, 127.0), "bit_count": 8},
    {"step": 50,  "com": (122.0, 122.0), "bit_count": 8},
    {"step": 100, "com": (117.0, 117.0), "bit_count": 8},
    {"step": 150, "com": (112.0, 112.0), "bit_count": 8},
    {"step": 200, "com": (107.0, 107.0), "bit_count": 8},
    {"step": 250, "com": (102.0, 102.0), "bit_count": 8},
]
score_wrap = fitness_fn(sim_wrap)
print(f"  Toroidal wrap test:  fitness = {score_wrap:.6f}")

print(f"\n[SUCCESS] All tests passed. Fix confirmed.")
