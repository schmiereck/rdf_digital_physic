#!/usr/bin/env python3
"""
forensic_fitness_analysis.py

Forensic analysis of the iter_200 champion rule to determine whether
SparseGliderFitness was fooled by transient initial motion (the
"transient puffer" exploit hypothesis).

Approach:
  1. Load the champion rule from iter_200.1 (the correct location).
  2. Simulate 512 steps on the L-tromino seed, logging cumulative
     displacement from the initial Centre of Mass at checkpoints
     32, 64, 128, 256, 384, 512.
  3. Re-run SparseGliderFitness with the L-tromino seed to reproduce
     the originally reported fitness.
  4. Save displacement data to CSV.
"""

import csv
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from evolution import center_of_mass, rule_dict_to_lut, step_grid
from fitness_v2 import SparseGliderFitness

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

ARCHIVE_ROOT = Path(__file__).parent.parent / "archive"

# The task spec references iter_200; the file lives in iter_200.1
RULE_PATH = ARCHIVE_ROOT / "iter_200.1" / "results" / "champion_v_lt_c_rule.json"
OUT_CSV   = ARCHIVE_ROOT / "iter_201"   / "results" / "displacement_over_time.csv"

# ---------------------------------------------------------------------------
# Simulation parameters
# ---------------------------------------------------------------------------

GRID_SIZE   = 128
SIM_STEPS   = 512
CHECKPOINTS = [32, 64, 128, 256, 384, 512]

# ---------------------------------------------------------------------------
# Load rule
# ---------------------------------------------------------------------------

print("=" * 60)
print("Forensic Fitness Analysis — iter_200 champion rule")
print("=" * 60)
print(f"Rule file : {RULE_PATH}")

if not RULE_PATH.exists():
    sys.exit(f"ERROR: rule file not found at {RULE_PATH}")

with RULE_PATH.open() as fh:
    meta = json.load(fh)

rule_dict = meta["rule_dict"]
seed_cells = meta.get("seed_cells", [[-1, -1], [0, -1], [0, 0]])  # L-tromino offsets
reported_fitness = meta.get("fitness", None)

print(f"Seed      : {meta.get('seed_particle', 'L-tromino')}  ({seed_cells})")
print(f"Reported fitness: {reported_fitness}")
print()

# ---------------------------------------------------------------------------
# Build initial grid (L-tromino centred at grid_size//2)
# ---------------------------------------------------------------------------

def make_seed_grid(
    seed_offsets: list,
    grid_size: int = GRID_SIZE,
) -> np.ndarray:
    grid   = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for dr, dc in seed_offsets:
        r = (centre + dr) % grid_size
        c = (centre + dc) % grid_size
        grid[r, c] = 1
    return grid

grid          = make_seed_grid(seed_cells, GRID_SIZE)
lut           = rule_dict_to_lut(rule_dict)
initial_com   = center_of_mass(grid)
initial_bits  = int(grid.sum())

print(f"Initial bits      : {initial_bits}")
print(f"Initial CoM       : ({initial_com[0]:.4f}, {initial_com[1]:.4f})")
print()

# ---------------------------------------------------------------------------
# 512-step simulation with cumulative displacement checkpoints
# ---------------------------------------------------------------------------

checkpoint_set = set(CHECKPOINTS)
records        = []  # (step, cumulative_displacement)

print(f"{'Step':>6}  {'Bits':>6}  {'CoM (r, c)':>26}  {'Cum. Displacement':>18}")
print("-" * 65)

for step in range(1, SIM_STEPS + 1):
    grid = step_grid(grid, lut)

    if step in checkpoint_set:
        bits    = int(grid.sum())
        com     = center_of_mass(grid)
        cum_dis = math.sqrt(
            (com[0] - initial_com[0]) ** 2
            + (com[1] - initial_com[1]) ** 2
        )
        print(
            f"{step:>6}  {bits:>6}  "
            f"({com[0]:>11.4f}, {com[1]:>11.4f})  "
            f"{cum_dis:>18.6f}"
        )
        records.append({"step": step, "displacement": cum_dis})

print()

# ---------------------------------------------------------------------------
# Reproduce SparseGliderFitness score using the L-tromino seed
# ---------------------------------------------------------------------------

# Use the same seed as the rule was evolved with; default SparseGliderFitness
# uses the T-tromino (4 cells), so we override `particle`.
L_TROMINO_OFFSETS = [tuple(pair) for pair in seed_cells]

fitness_fn = SparseGliderFitness(
    grid_size=128,
    simulation_steps=200,
    checkpoint_every=50,
    particle=L_TROMINO_OFFSETS,
)

metrics = fitness_fn.evaluate(rule_dict)
repro_fitness = metrics["fitness"]

print("SparseGliderFitness reproduction (200 steps, 50-step checkpoints, L-tromino):")
print(f"  reason              : {metrics.get('reason')}")
print(f"  initial_bits        : {metrics.get('initial_bits')}")
print(f"  total_displacement  : {metrics.get('total_displacement', 'N/A'):.6f}")
print(f"  mean_sparsity       : {metrics.get('mean_sparsity', 'N/A'):.6f}")
print(f"  sparsity_scores     : {[round(s, 4) for s in metrics.get('sparsity_scores', [])]}")
print(f"  inter-chkpt disps   : {[round(d, 4) for d in metrics.get('displacements', [])]}")
print(f"  reproduced fitness  : {repro_fitness:.6f}")
print(f"  reported fitness    : {reported_fitness}")
print()

# ---------------------------------------------------------------------------
# Save CSV
# ---------------------------------------------------------------------------

OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
with OUT_CSV.open("w", newline="") as fh:
    writer = csv.DictWriter(fh, fieldnames=["step", "displacement"])
    writer.writeheader()
    writer.writerows(records)

print(f"CSV saved -> {OUT_CSV}")

# ---------------------------------------------------------------------------
# Analysis summary
# ---------------------------------------------------------------------------

final_displacement = records[-1]["displacement"] if records else 0.0
first_displacement = records[0]["displacement"]  if records else 0.0

print()
print("=" * 60)
print("FORENSIC SUMMARY")
print("=" * 60)
print(f"Displacement at step  32 (early): {records[0]['displacement']:.6f}")
print(f"Displacement at step  64        : {records[1]['displacement']:.6f}")
print(f"Displacement at step 128        : {records[2]['displacement']:.6f}")
print(f"Displacement at step 256        : {records[3]['displacement']:.6f}")
print(f"Displacement at step 384        : {records[4]['displacement']:.6f}")
print(f"Displacement at step 512 (final): {records[5]['displacement']:.6f}")
print()

# Check whether CoM displacement is constant across all forensic checkpoints,
# which is the signature of an oscillator whose period divides 32 steps.
displacements_at_checkpoints = [r["displacement"] for r in records]
spread = max(displacements_at_checkpoints) - min(displacements_at_checkpoints)

# SparseGliderFitness reported inter-checkpoint displacements
sparse_disps = metrics.get("displacements", [])
sparse_nonzero = any(d > 0.01 for d in sparse_disps)

print(f"CoM displacement spread across forensic checkpoints: {spread:.2e}")
print(f"SparseGliderFitness inter-checkpoint displacements : {[round(d, 4) for d in sparse_disps]}")
print()

com_locked = spread < 1e-6

if com_locked and sparse_nonzero:
    verdict = (
        "CONFIRMED (oscillator phase-sampling exploit, not a classic transient puffer).\n"
        "\n"
        "The forensic simulation shows the CoM is CONSTANT at all checkpoints\n"
        "that are multiples of 32 (spread = {:.2e}). This proves the champion\n"
        "is a stationary oscillator whose period divides 32 steps.\n"
        "\n"
        "SparseGliderFitness checkpoints are at steps 50, 100, 150, 200 --\n"
        "none of which are multiples of the oscillation period. The evaluator\n"
        "therefore samples the CoM at different oscillation phases and mistakes\n"
        "the phase-to-phase shift for genuine translational motion.\n"
        "\n"
        "This is subtler than a classic transient puffer (early motion that stops).\n"
        "Here the oscillation PERSISTS indefinitely, but the checkpoint schedule\n"
        "is phase-incoherent with the oscillation period, creating a systematic\n"
        "illusion of net displacement. The fitness function was deceived."
    ).format(spread)
elif final_displacement < 0.01:
    verdict = (
        "CONFIRMED (stationary oscillator).\n"
        "Cumulative displacement is near-zero at step 512; the pattern never translates."
    )
elif final_displacement > 2.0:
    verdict = (
        "NOT CONFIRMED. Displacement grows through step 512, consistent with\n"
        "genuine translational motion."
    )
else:
    verdict = (
        "AMBIGUOUS. Bounded displacement but mechanism unclear; further analysis needed."
    )

print("Verdict:", verdict)
