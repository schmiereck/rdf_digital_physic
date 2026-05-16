#!/usr/bin/env python3
"""
run_iter_192_prescreen.py  —  iter_192 Strategy B, Step 1: Conservation Pre-screen.

Generate 10,000 random C2-symmetric rules and filter to those that perfectly
conserve bits over a 200-step two-glider collision simulation.  All passing
rules are saved to conserving_population.json for use by the screened
evolutionary search.

Outputs (under archive/iter_192/iter_002/results/):
  - conserving_population.json : list of rules that pass the conservation check
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import _try_build_c2_rule, rule_dict_to_lut, step_grid
from fitness import _make_staged_grid


# ── Paths ────────────────────────────────────────────────────────────────────

PROJECT_ROOT   = Path(__file__).parent.parent
OUTPUT_DIR     = PROJECT_ROOT / "archive" / "iter_192" / "iter_002" / "results"
CONSERVING_POP = OUTPUT_DIR / "conserving_population.json"


# ── Parameters ───────────────────────────────────────────────────────────────

NUM_RULES  = 10_000
SIM_STEPS  = 200
GRID_SIZE  = 128
DENSITY    = 8
RNG_SEED   = 192_002
LUT_SIZE   = 128


# ── Chromosome <-> rule_dict conversions ─────────────────────────────────────

def rule_dict_to_chromosome(rule_dict: dict) -> np.ndarray:
    lut = np.arange(LUT_SIZE, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def generate_c2_rule_density(
    rng: random.Random, density: int = DENSITY, max_attempts: int = 10_000,
) -> dict:
    for _ in range(max_attempts):
        pairs = [(rng.randint(1, 127), rng.randint(1, 127)) for _ in range(density)]
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(f"Failed to generate C2 rule with density {density}")


# ── Conservation check ────────────────────────────────────────────────────────

def check_conservation(rule_dict: dict, steps: int = SIM_STEPS) -> tuple[bool, int, int]:
    """Run `steps` on the two-glider grid; return (conserved, initial_bits, final_bits)."""
    lut          = rule_dict_to_lut(rule_dict)
    grid         = _make_staged_grid(GRID_SIZE)
    initial_bits = int(grid.sum())

    for _ in range(steps):
        grid = step_grid(grid, lut)

    final_bits = int(grid.sum())
    return final_bits == initial_bits, initial_bits, final_bits


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    print("=== iter_192 Pre-screen: Conservation Filter ===")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = random.Random(RNG_SEED)

    print(f"  Rules to test : {NUM_RULES}")
    print(f"  Sim steps     : {SIM_STEPS}")
    print(f"  Grid size     : {GRID_SIZE}x{GRID_SIZE} torus")
    print(f"  Rule density  : {DENSITY}")
    print(f"  RNG seed      : {RNG_SEED}")
    print(f"  Output        : {CONSERVING_POP}\n")

    conserving: list[dict] = []

    for i in range(NUM_RULES):
        rule_dict = generate_c2_rule_density(rng, density=DENSITY)
        conserved, initial_bits, final_bits = check_conservation(rule_dict)

        if conserved:
            chrom = rule_dict_to_chromosome(rule_dict)
            conserving.append({
                "index":        len(conserving),
                "rule_index":   i,
                "chromosome":   chrom.tolist(),
                "rule_dict":    {str(k): int(v) for k, v in rule_dict.items()},
                "initial_bits": initial_bits,
                "final_bits":   final_bits,
            })

        if (i + 1) % 1000 == 0:
            rate = 100.0 * len(conserving) / (i + 1)
            print(
                f"  Tested {i+1:6d}/{NUM_RULES}  "
                f"conserving so far: {len(conserving):4d}  ({rate:.2f}%)"
            )

    print(f"\n  Total tested    : {NUM_RULES}")
    print(f"  Conserving found: {len(conserving)} ({100.0*len(conserving)/NUM_RULES:.2f}%)")

    with open(CONSERVING_POP, "w") as f:
        json.dump(conserving, f, indent=2)
    print(f"  Saved to: {CONSERVING_POP}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
