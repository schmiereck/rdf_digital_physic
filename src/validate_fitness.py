#!/usr/bin/env python3
"""
validate_fitness.py

Validates that SparseGliderFitness correctly rejects the grid-filling exploit
discovered in iter_197.2 (old fitness: 16.70 under the previous scheme).

Expected result: fitness == 0.0 because the exploit rule inflates the bit count
from 4 (the T-tromino) to ~16 384 (the entire grid) within the first 50 steps,
tripping the hard bit-conservation gate at the first checkpoint.
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from fitness_v2 import SparseGliderFitness, _make_particle_grid
from evolution import rule_dict_to_lut, step_grid

PROJECT_ROOT = Path(__file__).parent.parent
CHAMPION_RULE_PATH = (
    PROJECT_ROOT / "archive" / "iter_197.2" / "results" / "champion_rule.json"
)

# ── Load exploit rule ────────────────────────────────────────────────────────

with open(CHAMPION_RULE_PATH) as f:
    data = json.load(f)

rule_dict = {int(k): int(v) for k, v in data["rule"].items()}
particle_offsets = [tuple(p) for p in data["particle"]]
old_fitness = data["fitness"]

print("=" * 60)
print("Exploit rule loaded from iter_197.2")
print("=" * 60)
print(f"  Old fitness (old scheme) : {old_fitness:.6f}")
print(f"  Reported mean_bit_count  : {data['metrics']['mean_bit_count']:.2f}")
print(f"  Seed bit count (expected): {len(particle_offsets)}")
print(f"  Grid size                : 128 x 128 = {128 * 128} cells")
print()

# ── Quick bit-count trace to observe the exploit ─────────────────────────────

GRID_SIZE = 128
SIM_STEPS = 200
CHECKPOINT_EVERY = 50

grid = _make_particle_grid(particle_offsets, GRID_SIZE)
initial_bits = int(grid.sum())
print(f"Simulation trace (bit count at each checkpoint):")
print(f"  Step   0: {initial_bits:6d} bits")

lut = rule_dict_to_lut(rule_dict)
checkpoints = set(range(CHECKPOINT_EVERY, SIM_STEPS + 1, CHECKPOINT_EVERY))
for step in range(1, SIM_STEPS + 1):
    grid = step_grid(grid, lut)
    if step in checkpoints:
        print(f"  Step {step:3d}: {int(grid.sum()):6d} bits")

print()

# ── Evaluate with SparseGliderFitness ────────────────────────────────────────

fitness_fn = SparseGliderFitness(
    grid_size=GRID_SIZE,
    simulation_steps=SIM_STEPS,
    checkpoint_every=CHECKPOINT_EVERY,
    particle=particle_offsets,
)

result = fitness_fn.evaluate(rule_dict)

print("SparseGliderFitness evaluation:")
print(f"  fitness : {result['fitness']:.6f}")
print(f"  reason  : {result['reason']}")
if result["reason"] == "bit_conservation_failed":
    print(f"  failed at step {result['step_failed']}")
    print(f"  bit count: {result['initial_bits']} -> {result['current_bits']}")
else:
    print(f"  total_displacement : {result['total_displacement']:.4f}")
    print(f"  mean_sparsity      : {result['mean_sparsity']:.6f}")
    print(f"  sparsity_scores    : {result['sparsity_scores']}")
    print(f"  displacements      : {result['displacements']}")
print()

# ── Verdict ──────────────────────────────────────────────────────────────────

print("=" * 60)
if result["fitness"] < 1e-9:
    print("PASS: SparseGliderFitness assigns fitness = 0.0 to the exploit.")
    print("      The sparsity/bit-conservation gate successfully rejects it.")
else:
    print(f"FAIL: Exploit received non-zero fitness {result['fitness']:.6f}")
print("=" * 60)
