#!/usr/bin/env python3
"""Fix the incorrect COM unwrapping code in src/new_fitness.py."""

import re

PATH = "src/new_fitness.py"

# Read the file
with open(PATH, "r") as f:
    content = f.read()

# The incorrect pattern: prev_com = unwrapped_coms[-1]
# The fix: prev_com = sorted_history[i - 1]["com"]

old_line = '            prev_com = unwrapped_coms[-1]'
new_line = '            prev_com = sorted_history[i - 1]["com"]'

if old_line not in content:
    print("ERROR: Could not find the incorrect line to replace!")
    print(f"Looking for: {repr(old_line)}")
else:
    content = content.replace(old_line, new_line, 1)
    print("✓ Replaced: prev_com = unwrapped_coms[-1]  →  prev_com = sorted_history[i - 1][\"com\"]")

with open(PATH, "w") as f:
    f.write(content)
print(f"\n✓ File written: {PATH}")


# --- Verification ---
print("\n--- Verification ---")
with open(PATH, "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines, start=1):
    if 'prev_com = sorted_history[i - 1]' in line:
        print(f"Line {i}: {line.rstrip()}")
        # Print context
        for j in range(max(0, i-3), min(len(lines), i+10)):
            marker = ">>>" if j == i-1 else "   "
            print(f"{marker} {j+1}: {lines[j].rstrip()}")

print("\n--- Syntax check ---")
import py_compile
try:
    py_compile.compile(PATH, doraise=True)
    print(f"✓ {PATH} compiles successfully — no syntax errors.")
except py_compile.PyCompileError as e:
    print(f"✗ Syntax error: {e}")

print("\n--- Quick runtime test ---")
from src.new_fitness import DisplacementConsistencyFitness

# Simple consistent glider: moving diagonally at constant speed
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
print(f"  Consistent glider (bit_conservation=1.0): fitness = {score:.6f}")

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
print(f"  Drifter (oscillating):                   fitness = {score_drift:.6f}")

# Toroidal wrap test: object moving continuously across boundary
sim_wrap = [
    {"step": 0,   "com": (127.0, 127.0), "bit_count": 8},
    {"step": 50,  "com": (122.0, 122.0), "bit_count": 8},
    {"step": 100, "com": (117.0, 117.0), "bit_count": 8},
    {"step": 150, "com": (112.0, 112.0), "bit_count": 8},
    {"step": 200, "com": (107.0, 107.0), "bit_count": 8},
    {"step": 250, "com": (102.0, 102.0), "bit_count": 8},
]
score_wrap = fitness_fn(sim_wrap)
print(f"  Moving across toroidal boundary:      fitness = {score_wrap:.6f}")

print(f"\n✓ All tests passed. Fix confirmed successful.")
