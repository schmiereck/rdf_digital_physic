#!/usr/bin/env python3
"""
validate_fitness.py

Empirical validation of DisplacementConsistencyFitness.

Gallery:
  1. g10_f_rule_034_c2 (iter_193) — v=1c elastic collision rule  → expected HIGH score
  2. g10_rule_001      (iter_179) — v=1c glider                  → expected HIGH score
  3. g4_rule_083       (iter_218) — drifter exploit               → expected LOW / zero score

Exit code: non-zero if the drifter rule scores higher than either glider rule.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from new_fitness import DisplacementConsistencyFitness
from evolution import rule_dict_to_lut, step_grid, center_of_mass

PROJECT_ROOT = Path(__file__).parent.parent

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


def _best_path(*candidates):
    for p in candidates:
        path = PROJECT_ROOT / p
        if path.exists():
            return path
    raise FileNotFoundError(f"None of the candidate paths exist: {candidates}")


def load_rule_dict(path):
    with open(path) as f:
        data = json.load(f)
    raw = data.get("rule_dict") or data.get("rule") or {}
    return {int(k): int(v) for k, v in raw.items()}


# ── Rule gallery ─────────────────────────────────────────────────────────────

# 1. g10_f_rule_034_c2 — v=1c elastic collision rule (iter_193)
path_193 = _best_path(
    "archive/iter_193/iter_002/results/champion_rule.json",
    "archive/iter_193/results/champion_rule.json",
)
rule_193 = load_rule_dict(path_193)

# 2. g10_rule_001 — v=1c glider (iter_179)
path_179 = _best_path(
    "archive/iter_179/results/champion_rule.json",
)
rule_179 = load_rule_dict(path_179)

# 3. g4_rule_083 — drifter exploit (iter_218)
path_218 = _best_path(
    "archive/iter_218/results/champion_g4_rule_083.json",
    "archive/iter_218/results/champion_vc_rule.json",
    "archive/iter_218/results/champion_rule.json",
)
rule_218 = load_rule_dict(path_218)

GALLERY = [
    ("g10_f_rule_034_c2 [iter_193]", rule_193, str(path_193.relative_to(PROJECT_ROOT))),
    ("g10_rule_001      [iter_179]", rule_179, str(path_179.relative_to(PROJECT_ROOT))),
    ("g4_rule_083       [iter_218]", rule_218, str(path_218.relative_to(PROJECT_ROOT))),
]

# ── Evaluation ───────────────────────────────────────────────────────────────

fitness_fn = DisplacementConsistencyFitness(num_windows=NUM_WINDOWS)

print(f"DisplacementConsistencyFitness validation — {SIM_STEPS} steps, "
      f"{GRID_SIZE}x{GRID_SIZE} grid, {NUM_WINDOWS} windows, 3-bit L-tromino seed")
print()

rows = []
for label, rule_dict, source in GALLERY:
    print(f"  [{label}]")
    print(f"    source: {source}")
    history = run_simulation(rule_dict)
    score = fitness_fn(history)
    initial_bits = history[0]["bit_count"]
    final_bits = history[-1]["bit_count"]
    initial_com = history[0]["com"]
    final_com = history[-1]["com"]
    net_disp = ((final_com[0] - initial_com[0]) ** 2 +
                (final_com[1] - initial_com[1]) ** 2) ** 0.5
    rows.append((label, score, initial_bits, final_bits, net_disp))
    print(f"    fitness={score:.4f}  net_disp={net_disp:.2f}  bits: {initial_bits}->{final_bits}")
    print()

# ── Results table ─────────────────────────────────────────────────────────────

print()
print("=" * 70)
print(f"{'Rule':<38} {'Fitness':>10} {'Net Disp':>10} {'Bits 0->500':>12}")
print("=" * 70)
for label, score, ib, fb, nd in rows:
    print(f"{label:<38} {score:>10.4f} {nd:>10.2f}   {ib} -> {fb}")
print("=" * 70)
print()

# ── Verdict ───────────────────────────────────────────────────────────────────

score_193, score_179, score_218 = rows[0][1], rows[1][1], rows[2][1]

print(f"  g10_f_rule_034_c2 fitness : {score_193:.4f}")
print(f"  g10_rule_001      fitness : {score_179:.4f}")
print(f"  g4_rule_083       fitness : {score_218:.4f}")
print()

drifter_beats_193 = score_218 >= score_193
drifter_beats_179 = score_218 >= score_179

if drifter_beats_193 or drifter_beats_179:
    print("FAIL — drifter (g4_rule_083) scored >= one or both glider rules.")
    print(f"  drifter ({score_218:.4f}) >= g10_f_rule_034_c2 ({score_193:.4f}): {drifter_beats_193}")
    print(f"  drifter ({score_218:.4f}) >= g10_rule_001 ({score_179:.4f}): {drifter_beats_179}")
    sys.exit(1)
else:
    print("PASS — drifter scored lower than both glider rules.")
    print(f"  glider margin over drifter: "
          f"iter_193={score_193 - score_218:.4f}, iter_179={score_179 - score_218:.4f}")
