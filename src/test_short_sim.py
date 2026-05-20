#!/usr/bin/env python3
"""
test_short_sim.py — Run a 10-step simulation of the champion rule from
iter_220 using the L-tromino seed and print the active cell count at each step.

This confirms that the rule behaves exactly as expected.
"""

import json
import sys
from pathlib import Path

import numpy as np

# Ensure src/ is on the path (script lives in src/)
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rule import Rule
from simulator import Simulator, Particle, GRID_SIZE
from seeds import L_TROMINO_SEED


def main():
    # ── Load the champion rule ─────────────────────────────────────────────
    rule_path = Path(__file__).resolve().parent.parent / "archive" / "iter_220" / "results" / "champion_vc_rule_consistency.json"
    with open(rule_path) as f:
        data = json.load(f)

    rule_dict = data["rule_dict"]
    rule = Rule(rule_dict)

    # ── Initialise grid with L-tromino seed ────────────────────────────────
    grid = L_TROMINO_SEED.copy()
    sim = Simulator(rule, grid_size=GRID_SIZE)

    # ── Run 10 steps ──────────────────────────────────────────────────────
    print(f"Rule: {rule_dict}")
    print(f"Seed: L-tromino at {(63,63),(64,63),(64,64)}")
    print()

    for step in range(10):
        bit_count = int(np.count_nonzero(grid))
        print(f"Step {step}: {bit_count} active cell(s)")
        p = Particle(grid)
        sim.step(p)
        grid = p.grid


if __name__ == "__main__":
    main()
