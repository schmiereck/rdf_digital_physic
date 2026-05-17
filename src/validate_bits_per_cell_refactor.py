#!/usr/bin/env python3
"""
validate_bits_per_cell_refactor.py

Backward-compatibility validation for the bits-per-cell refactor.

With ``BITS_PER_CELL = 1`` the new ``engine.py`` step path must produce the
exact same head-on elastic collision as the legacy 1-bit pipeline did in
iter_195 with the iter_193 champion rule.

Test plan:
  1. Load the champion rule from archive/iter_193/iter_002/results/champion_rule.json
  2. Construct the standard two-glider head-on collision seed (offset=0).
  3. Run a 600-step simulation using:
       (a) the new HexagonalGrid + engine.step_grid path (bits_per_cell=1)
       (b) the legacy evolution.step_grid 2D path
       (c) the multi-bit-aware RecessionBiasedFitness with bits_per_cell=1
  4. Assert that all three agree on bit-count time-series and that the
     collision is a perfect elastic scattering:
       initial_bits == 6 == final_bits  (bit_error = 0)
       min_distance ~ 2.236  (~ sqrt(5))
       recession_score == 1.0
       initial_distance ~ final_distance ~ 47.518

A non-zero exit code signals a regression.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label as nd_label
from scipy.ndimage import center_of_mass as nd_com

REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

import engine  # noqa: E402
from engine import HexagonalGrid, build_lut, step_grid as engine_step  # noqa: E402
from rule import Rule  # noqa: E402
from evolution import rule_dict_to_lut, step_grid as legacy_step  # noqa: E402
from fitness import RecessionBiasedFitness  # noqa: E402


CHAMPION_PATH = (
    REPO_ROOT / "archive/iter_193/iter_002/results/champion_rule.json"
)

GRID_SIZE = 128
# Same seed as iter_195 / characterize_offset_collisions.py (offset = 0)
OBJECT_A = [(60, 40), (61, 40), (60, 41)]
OBJECT_B = [(67, 87), (68, 87), (67, 88)]
LABEL_STRUCT = np.ones((3, 3), dtype=np.uint8)
MARGIN = 1.0
SIM_STEPS = 400  # matches iter_193 training horizon (no torus wraparound)
EXPECTED_INITIAL_BITS = 6
EXPECTED_INITIAL_DISTANCE = 47.518417
EXPECTED_MIN_DISTANCE = math.sqrt(5)  # 2.2360679...
DIST_TOL = 1e-6


def make_seed_2d() -> np.ndarray:
    g = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in OBJECT_A + OBJECT_B:
        g[r % GRID_SIZE, c % GRID_SIZE] = 1
    return g


def two_largest_com_distance(grid: np.ndarray) -> float | None:
    if grid.ndim == 3:
        mask = (grid.sum(axis=-1) > 0).astype(np.uint8)
    else:
        mask = (grid > 0).astype(np.uint8)
    labels, n = nd_label(mask, structure=LABEL_STRUCT)
    if n < 2:
        return None
    sizes = sorted(
        ((lbl, int(np.sum(labels == lbl))) for lbl in range(1, n + 1)),
        key=lambda x: x[1],
        reverse=True,
    )
    top2 = [sizes[0][0], sizes[1][0]]
    coms = nd_com(mask, labels, top2)
    (r1, c1), (r2, c2) = coms
    return math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)


def run_engine_path(rule_dict: dict) -> dict:
    """Run via the new engine + HexagonalGrid at bits_per_cell=1."""
    rule = Rule(rule_dict, bits_per_cell=1)
    grid = HexagonalGrid.from_2d(make_seed_2d(), bits_per_cell=1)
    initial_distance = two_largest_com_distance(grid.data)
    initial_bits = grid.bit_count
    min_distance = initial_distance
    bit_series = [initial_bits]
    for _ in range(SIM_STEPS):
        grid.step(rule.lut)
        b = grid.bit_count
        bit_series.append(b)
        d = two_largest_com_distance(grid.data)
        if d is not None and d < min_distance:
            min_distance = d
    final_distance = two_largest_com_distance(grid.data)
    final_bits = grid.bit_count
    return {
        "path": "engine_HexagonalGrid",
        "initial_bits": initial_bits,
        "final_bits": final_bits,
        "bit_error": abs(initial_bits - final_bits),
        "initial_distance": float(initial_distance) if initial_distance else None,
        "min_distance": float(min_distance) if min_distance else None,
        "final_distance": float(final_distance) if final_distance else None,
        "bit_series_first10": bit_series[:10],
        "bit_series_last10": bit_series[-10:],
    }


def run_legacy_path(rule_dict: dict) -> dict:
    """Run via the legacy evolution.step_grid 2D path."""
    lut = rule_dict_to_lut(rule_dict)
    grid = make_seed_2d()
    initial_distance = two_largest_com_distance(grid)
    initial_bits = int(grid.sum())
    min_distance = initial_distance
    bit_series = [initial_bits]
    for _ in range(SIM_STEPS):
        grid = legacy_step(grid, lut)
        b = int(grid.sum())
        bit_series.append(b)
        d = two_largest_com_distance(grid)
        if d is not None and d < min_distance:
            min_distance = d
    final_distance = two_largest_com_distance(grid)
    final_bits = int(grid.sum())
    return {
        "path": "legacy_evolution_step_grid",
        "initial_bits": initial_bits,
        "final_bits": final_bits,
        "bit_error": abs(initial_bits - final_bits),
        "initial_distance": float(initial_distance) if initial_distance else None,
        "min_distance": float(min_distance) if min_distance else None,
        "final_distance": float(final_distance) if final_distance else None,
        "bit_series_first10": bit_series[:10],
        "bit_series_last10": bit_series[-10:],
    }


def run_fitness_path(rule_dict: dict) -> dict:
    """Run via RecessionBiasedFitness with bits_per_cell=1 (new kwarg)."""
    fit = RecessionBiasedFitness(
        horizon=SIM_STEPS,
        grid_size=GRID_SIZE,
        bits_per_cell=1,
    )
    out = fit.evaluate(rule_dict)
    return {"path": "RecessionBiasedFitness(bits_per_cell=1)", **out}


def main() -> int:
    print(f"Loading champion rule: {CHAMPION_PATH}")
    if not CHAMPION_PATH.exists():
        print(f"ERROR: champion rule not found at {CHAMPION_PATH}", file=sys.stderr)
        return 2
    data = json.loads(CHAMPION_PATH.read_text())
    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    print(f"  rule_dict size: {len(rule_dict)} entries")
    print(f"  engine.BITS_PER_CELL = {engine.BITS_PER_CELL}")

    print("\n[1] Engine path (HexagonalGrid + engine.step_grid, bits_per_cell=1)")
    eng = run_engine_path(rule_dict)
    print(f"    initial_bits  = {eng['initial_bits']}")
    print(f"    final_bits    = {eng['final_bits']}")
    print(f"    bit_error     = {eng['bit_error']}")
    print(f"    initial_dist  = {eng['initial_distance']:.6f}")
    print(f"    min_distance  = {eng['min_distance']:.6f}")
    print(f"    final_dist    = {eng['final_distance']:.6f}")

    print("\n[2] Legacy path (evolution.step_grid 2D)")
    leg = run_legacy_path(rule_dict)
    print(f"    initial_bits  = {leg['initial_bits']}")
    print(f"    final_bits    = {leg['final_bits']}")
    print(f"    bit_error     = {leg['bit_error']}")
    print(f"    initial_dist  = {leg['initial_distance']:.6f}")
    print(f"    min_distance  = {leg['min_distance']:.6f}")
    print(f"    final_dist    = {leg['final_distance']:.6f}")

    print("\n[3] RecessionBiasedFitness path (bits_per_cell=1)")
    fit = run_fitness_path(rule_dict)
    print(f"    fitness          = {fit.get('fitness'):.6f}")
    print(f"    approach_ok      = {fit.get('approach_ok')}")
    print(f"    recession_score  = {fit.get('recession_score'):.6f}")
    print(f"    initial_distance = {fit.get('initial_distance'):.6f}")
    print(f"    min_distance     = {fit.get('min_distance'):.6f}")
    print(f"    final_distance   = {fit.get('final_distance'):.6f}")
    print(f"    initial_bits     = {fit.get('initial_bits')}")
    print(f"    final_bits       = {fit.get('final_bits')}")
    print(f"    bit_error        = {fit.get('bit_error')}")

    print("\n[4] Consistency checks (engine vs legacy)")
    checks = []

    def chk(name: str, ok: bool, detail: str = ""):
        marker = "OK " if ok else "FAIL"
        print(f"    [{marker}] {name}{(' --' + detail) if detail else ''}")
        checks.append(ok)

    chk(
        "engine vs legacy initial_distance",
        abs(eng["initial_distance"] - leg["initial_distance"]) < DIST_TOL,
        f"d={abs(eng['initial_distance'] - leg['initial_distance']):.2e}",
    )
    chk(
        "engine vs legacy final_distance",
        abs(eng["final_distance"] - leg["final_distance"]) < DIST_TOL,
        f"d={abs(eng['final_distance'] - leg['final_distance']):.2e}",
    )
    chk(
        "engine vs legacy min_distance",
        abs(eng["min_distance"] - leg["min_distance"]) < DIST_TOL,
        f"d={abs(eng['min_distance'] - leg['min_distance']):.2e}",
    )
    chk(
        "engine vs legacy bit series prefix",
        eng["bit_series_first10"] == leg["bit_series_first10"],
        f"{eng['bit_series_first10']} vs {leg['bit_series_first10']}",
    )
    chk(
        "engine vs legacy bit series suffix",
        eng["bit_series_last10"] == leg["bit_series_last10"],
        f"{eng['bit_series_last10']} vs {leg['bit_series_last10']}",
    )

    print("\n[5] Physics checks (elastic collision)")
    chk("initial_bits == 6", eng["initial_bits"] == EXPECTED_INITIAL_BITS)
    chk("final_bits == 6 (bit conservation)", eng["final_bits"] == EXPECTED_INITIAL_BITS)
    chk("bit_error == 0", eng["bit_error"] == 0)
    chk(
        "initial_distance ~ 47.518",
        abs(eng["initial_distance"] - EXPECTED_INITIAL_DISTANCE) < 1e-3,
        f"got {eng['initial_distance']:.6f}",
    )
    chk(
        "min_distance ~ sqrt(5)",
        abs(eng["min_distance"] - EXPECTED_MIN_DISTANCE) < 1e-3,
        f"got {eng['min_distance']:.6f}",
    )
    chk(
        "approach: min < initial - MARGIN",
        eng["min_distance"] < eng["initial_distance"] - MARGIN,
    )
    chk(
        "elastic recession: final ~ initial",
        abs(eng["final_distance"] - eng["initial_distance"]) < 1e-3,
        f"|d|={abs(eng['final_distance'] - eng['initial_distance']):.2e}",
    )
    chk(
        "fitness.recession_score == 1.0",
        abs(fit.get("recession_score", 0.0) - 1.0) < 1e-9,
    )
    chk(
        "fitness.bit_error == 0",
        fit.get("bit_error") == 0,
    )

    all_ok = all(checks)
    print(f"\nResult: {'PASS' if all_ok else 'FAIL'}  ({sum(checks)}/{len(checks)} checks)")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
