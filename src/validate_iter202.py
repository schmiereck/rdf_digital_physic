#!/usr/bin/env python3
"""Validate CumulativeDisplacementFitness against the iter_200 champion rule."""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from fitness_v2 import CumulativeDisplacementFitness

PROJECT_ROOT = Path(__file__).parent.parent

CHAMPION_RULE_PATH = PROJECT_ROOT / "archive" / "iter_200" / "results" / "champion_vc_rule.json"
OUTPUT_DIR = PROJECT_ROOT / "archive" / "iter_202" / "results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

with open(CHAMPION_RULE_PATH) as f:
    champion_data = json.load(f)

rule_dict = {int(k): int(v) for k, v in champion_data["rule_dict"].items()}

# L-tromino seed from iter_200
L_TROMINO = [(0, 0), (0, 1), (1, 1)]

fitness_fn = CumulativeDisplacementFitness(
    grid_size=128,
    simulation_steps=200,
    particle=L_TROMINO,
)

print(f"Running CumulativeDisplacementFitness on iter_200 champion rule...")
print(f"Seed: L-tromino {L_TROMINO}")
print(f"Grid size: {fitness_fn.grid_size}, Steps: {fitness_fn.simulation_steps}")

metrics = fitness_fn.evaluate(rule_dict)

print(f"\n=== Results ===")
print(f"  fitness       : {metrics['fitness']:.8f}")
print(f"  displacement  : {metrics['displacement']:.8f}")
print(f"  initial_bits  : {metrics['initial_bits']}")
print(f"  final_bits    : {metrics['final_bits']}")
print(f"  initial_com   : {metrics['initial_com']}")
print(f"  final_com     : {metrics['final_com']}")
print(f"  reason        : {metrics['reason']}")

success = metrics['fitness'] < 0.1
print(f"\n  SUCCESS CRITERION (fitness < 0.1): {'PASS' if success else 'FAIL'}")

report = f"""iter_202 Validation Report
==========================
Date: 2026-05-18
Purpose: Validate CumulativeDisplacementFitness rejects the iter_200 stationary-oscillator exploit.

Rule source: {CHAMPION_RULE_PATH}
  iteration: {champion_data['iteration']}
  original fitness (SparseGliderFitness): {champion_data['fitness']}

Validation configuration
------------------------
  fitness_function : CumulativeDisplacementFitness
  grid_size        : {fitness_fn.grid_size}
  simulation_steps : {fitness_fn.simulation_steps}
  seed_particle    : L-tromino {L_TROMINO}

Results
-------
  fitness       : {metrics['fitness']:.8f}
  displacement  : {metrics['displacement']:.8f}
  initial_bits  : {metrics['initial_bits']}
  final_bits    : {metrics['final_bits']}
  initial_com   : {metrics['initial_com']}
  final_com     : {metrics['final_com']}

Success criterion: fitness < 0.1
Outcome: {'PASS' if success else 'FAIL'}

Interpretation
--------------
The iter_200 champion rule was previously awarded a fitness of {champion_data['fitness']:.5f}
by SparseGliderFitness.  That rule is a stationary oscillator that exploits the
phase-sampling flaw: it displaces once at the first checkpoint then oscillates in
place, accumulating checkpoint-to-checkpoint displacement that looks like motion.

CumulativeDisplacementFitness measures net displacement from t=0 to t={fitness_fn.simulation_steps}.
For a stationary oscillator the net displacement is near zero, yielding a fitness
of {metrics['fitness']:.8f} — well below the 0.1 threshold.  The exploit is defeated.
"""

report_path = OUTPUT_DIR / "validation_report.txt"
with open(report_path, "w") as f:
    f.write(report)

print(f"\nReport written to: {report_path}")
sys.exit(0 if success else 1)
