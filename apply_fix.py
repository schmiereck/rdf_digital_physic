#!/usr/bin/env python3
"""Apply the COM unwrapping fix to src/new_fitness.py.

Bug: Line 241 uses prev_com = unwrapped_coms[-1]
     which causes the unwrapped COM to accumulate artifacts.

Fix:  Line 241 should use prev_com = sorted_history[i - 1]["com"]
      to reference the previous raw (pre-unwrap) COM position.
"""

import sys
import py_compile

PATH = "src/new_fitness.py"

# ── 1. Open and read ────────────────────────────────────────────────
with open(PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"[INFO] Read {len(lines)} lines from {PATH}")

# ── 2. Replace the buggy line ───────────────────────────────────────
old_line = '            prev_com = unwrapped_coms[-1]\n'
new_line = '            prev_com = sorted_history[i - 1]["com"]\n'

found = False
for i, line in enumerate(lines):
    if line == old_line:
        lines[i] = new_line
        print(f"[FIX] Line {i+1}: unwrapped_coms[-1]  ->  sorted_history[i - 1][\"com\"]")
        found = True
        break

if not found:
    print("[FIX] Could not find exact line. Trying substring match...")
    for i, line in enumerate(lines):
        if 'prev_com = unwrapped_coms[-1]' in line:
            lines[i] = line.replace('prev_com = unwrapped_coms[-1]',
                                     'prev_com = sorted_history[i - 1]["com"]')
            print(f"[FIX] Line {i+1}: {lines[i].rstrip()}")
            found = True
            break

if not found:
    print("[ERROR] Fix could not be applied!")
    sys.exit(1)

# ── 3. Save back ───────────────────────────────────────────────────
with open(PATH, "w", encoding="utf-8") as f:
    f.writelines(lines)
print(f"[INFO] Saved updated content to {PATH}")

# ── 4. Verify the fix exists ───────────────────────────────────────
with open(PATH, "r", encoding="utf-8") as f:
    updated_lines = f.readlines()

found = False
for i, line in enumerate(updated_lines):
    if 'prev_com = sorted_history[i - 1]["com"]' in line:
        found = True
        print(f"[VERIFY] Line {i+1}: {line.rstrip()}")

if not found:
    print("[VERIFY] ERROR: Fix not found in saved file!")
    sys.exit(1)
else:
    print("[VERIFY] OK: Fix confirmed present in file.")

# ── 5. Print lines 240-255 ─────────────────────────────────────────
print("\n--- Lines 240-255 of the updated file ---")
for i in range(239, min(255, len(updated_lines))):
    print(f"  {i+1}: {updated_lines[i].rstrip()}")

# ── 6. Syntax check ────────────────────────────────────────────────
print("\n--- Syntax check ---")
try:
    py_compile.compile(PATH, doraise=True)
    print("[OK] No syntax errors.")
except py_compile.PyCompileError as e:
    print(f"[FAIL] Syntax error: {e}")
    sys.exit(1)

# ── 7. Quick runtime test ──────────────────────────────────────────
print("\n--- Quick runtime test ---")
sys.path.insert(0, ".")
from src.new_fitness import DisplacementConsistencyFitness

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

assert score > score_drift, \
    f"Consistent glider ({score}) should score higher than drifter ({score_drift})"

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

print(f"\n[SUCCESS] Fix applied and verified successfully.")
