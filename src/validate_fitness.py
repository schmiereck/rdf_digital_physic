#!/usr/bin/env python3
"""
validate_fitness.py

Validation gallery for DisplacementConsistencyFitness.

Tests three rule categories to verify the fitness function can correctly
distinguish coherent motion (glider) from exploits (drifter, still life):

  1. v=1c elastic glider (iter_193) - expected: significantly positive score
  2. Drifter exploit (iter_218)     - expected: score near zero
  3. Still life (identity rule)     - expected: score near zero
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from new_fitness import DisplacementConsistencyFitness
from evolution import rule_dict_to_lut, step_grid, center_of_mass

PROJECT_ROOT = Path(__file__).parent.parent

# Standard 3-bit L-tromino seed, centered on 128x128 grid.
SEED_CELLS = [(63, 63), (64, 63), (64, 64)]
GRID_SIZE = 128
SIM_STEPS = 500
NUM_WINDOWS = 5


def make_seed_grid(cells=SEED_CELLS, grid_size=GRID_SIZE):
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in cells:
        grid[r, c] = 1
    return grid


def run_simulation(rule_dict, steps=SIM_STEPS, grid_size=GRID_SIZE):
    """Simulate rule_dict and return a sim_history list for fitness evaluation."""
    lut = rule_dict_to_lut(rule_dict)
    grid = make_seed_grid(grid_size=grid_size)

    history = []
    com = center_of_mass(grid)
    history.append({"step": 0, "com": com, "bit_count": int(grid.sum())})

    for step in range(1, steps + 1):
        grid = step_grid(grid, lut)
        com = center_of_mass(grid)
        history.append({"step": step, "com": com, "bit_count": int(grid.sum())})

    return history


# ── Rule gallery ────────────────────────────────────────────────────────────

# Resolve paths: use the canonical path if it exists, otherwise fall back to
# the nearest available alternative in the archive tree.
def _best_path(*candidates):
    """Return the first candidate path that exists."""
    for p in candidates:
        path = PROJECT_ROOT / p
        if path.exists():
            return path
    raise FileNotFoundError(f"None of the candidate paths exist: {candidates}")


def load_rule_dict(path):
    with open(path) as f:
        data = json.load(f)
    # Support both "rule_dict" and "rule" key names used across iterations.
    raw = data.get("rule_dict") or data.get("rule") or {}
    return {int(k): int(v) for k, v in raw.items()}


# 1. v=1c elastic glider — iter_193
glider_path = _best_path(
    "archive/iter_193/results/champion_rule.json",
    "archive/iter_193/iter_002/results/champion_rule.json",
)
rule_glider = load_rule_dict(glider_path)

# 2. Drifter exploit — iter_218
drifter_path = _best_path(
    "archive/iter_218/results/champion_g4_rule_083.json",
    "archive/iter_218/results/champion_rule.json",
    "archive/iter_218/results/champion_vc_rule.json",
)
rule_drifter = load_rule_dict(drifter_path)

# 3. Still life — iter_056 (identity rule: no swaps → cells never change)
still_path_candidates = (
    "archive/iter_056/results/rule_1.json",
)
try:
    still_path = _best_path(*still_path_candidates)
    rule_still = load_rule_dict(still_path)
    still_source = str(still_path.relative_to(PROJECT_ROOT))
except FileNotFoundError:
    # Identity rule: empty dict → every cell maps to its own current state.
    rule_still = {}
    still_source = "synthetic identity rule (no iter_056 JSON found)"

GALLERY = [
    ("v=1c elastic", rule_glider,  str(glider_path.relative_to(PROJECT_ROOT))),
    ("drifter",      rule_drifter, str(drifter_path.relative_to(PROJECT_ROOT))),
    ("still_life",   rule_still,   still_source),
]

# ── Evaluation ──────────────────────────────────────────────────────────────

fitness_fn = DisplacementConsistencyFitness(num_windows=NUM_WINDOWS)

print(f"Running validation gallery -- {SIM_STEPS} steps, 128x128 grid, "
      f"{NUM_WINDOWS} windows, 3-bit L-tromino seed")
print()

rows = []
for label, rule_dict, source in GALLERY:
    print(f"  [{label}]  source: {source}")
    history = run_simulation(rule_dict)
    score = fitness_fn(history)
    initial_bits = history[0]["bit_count"]
    final_bits   = history[-1]["bit_count"]
    initial_com  = history[0]["com"]
    final_com    = history[-1]["com"]
    net_disp = ((final_com[0] - initial_com[0])**2 +
                (final_com[1] - initial_com[1])**2) ** 0.5
    rows.append((label, score, initial_bits, final_bits, net_disp))
    print(f"         fitness={score:.4f}  net_disp={net_disp:.2f}  "
          f"bits: {initial_bits}->{final_bits}")
    print()

# ── Results table ────────────────────────────────────────────────────────────

print()
print("=" * 65)
print(f"{'Rule':<20} {'Fitness':>10} {'Net Disp':>10} {'Bits (0->500)':>14}")
print("=" * 65)
for label, score, ib, fb, nd in rows:
    print(f"{label:<20} {score:>10.4f} {nd:>10.2f}   {ib} -> {fb}")
print("=" * 65)
print()

# ── Verdict ──────────────────────────────────────────────────────────────────

glider_score = rows[0][1]
drifter_score = rows[1][1]
still_score  = rows[2][1]

PASS_THRESHOLD = 5.0   # glider must exceed this
EXPLOIT_THRESHOLD = 1.0  # drifter and still_life must be below this

verdict_glider  = "PASS" if glider_score  > PASS_THRESHOLD    else "FAIL"
verdict_drifter = "PASS" if drifter_score < EXPLOIT_THRESHOLD  else "FAIL"
verdict_still   = "PASS" if still_score   < EXPLOIT_THRESHOLD  else "FAIL"

print(f"  v=1c elastic > {PASS_THRESHOLD}  : [{verdict_glider}]  score={glider_score:.4f}")
print(f"  drifter    < {EXPLOIT_THRESHOLD}  : [{verdict_drifter}]  score={drifter_score:.4f}")
print(f"  still_life < {EXPLOIT_THRESHOLD}  : [{verdict_still}]  score={still_score:.4f}")
print()

all_pass = all(v == "PASS" for v in [verdict_glider, verdict_drifter, verdict_still])
print("OVERALL:", "PASS — DisplacementConsistencyFitness distinguishes glider from exploits."
      if all_pass else
      "FAIL — one or more rules did not score as expected.")
