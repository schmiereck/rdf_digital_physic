#!/usr/bin/env python3
"""
run_iter_189_fitness_validation.py

Validate MarginalDynamicCollisionFitness by showing it assigns fitness 0.0
to the iter_188 'micro-jitter' champion rule that exploited the original
DynamicCollisionFitness (which only required any approach/recession, with no
minimum margin).

The new function requires each phase to exceed a margin:
  - midpoint_distance < initial_distance - margin
  - final_distance    > midpoint_distance + margin
  - bits and objects conserved
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass

sys.path.insert(0, str(Path(__file__).parent))

from evolution import rule_dict_to_lut, step_grid

# ── Grid setup (identical to DynamicCollisionFitness in fitness.py) ──────────

_DYN_GRID_SIZE    = 64
_DYN_OBJECT_A     = [(30, 20), (31, 20), (30, 21)]
_DYN_OBJECT_B     = [(33, 43), (34, 43), (33, 44)]
_DYN_INITIAL_BITS = len(_DYN_OBJECT_A) + len(_DYN_OBJECT_B)  # 6
_DYN_INITIAL_OBJECTS = 2
_DYN_LABEL_STRUCTURE = np.ones((3, 3), dtype=np.uint8)


def _make_dynamic_collision_grid(grid_size: int = _DYN_GRID_SIZE) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in _DYN_OBJECT_A:
        grid[r % grid_size, c % grid_size] = 1
    for r, c in _DYN_OBJECT_B:
        grid[r % grid_size, c % grid_size] = 1
    return grid


def _two_object_com_distance(grid: np.ndarray) -> float | None:
    labels, n = label(grid, structure=_DYN_LABEL_STRUCTURE)
    if n != 2:
        return None
    coms = center_of_mass(grid, labels, [1, 2])
    (r1, c1), (r2, c2) = coms
    return math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)


# ── MarginalDynamicCollisionFitness ─────────────────────────────────────────

class MarginalDynamicCollisionFitness:
    """Fitness function that rewards a *dynamic* bit-conserving collision with
    a minimum displacement margin in each phase.

    Two 3-bit gliders are placed on a 64x64 toroidal grid:
      * Object 1 at (30,20), (31,20), (30,21)
      * Object 2 at (33,43), (34,43), (33,44)

    The simulation runs for ``horizon`` steps. Distances between the centres
    of mass of the two connected components are sampled at three time points:
    0 (initial), horizon // 2 (midpoint) and horizon (final).

    Fitness is 1.0 iff ALL four conditions hold, else 0.0:
      1. Approach   : midpoint_distance < initial_distance  - margin
      2. Recession  : final_distance    > midpoint_distance + margin
      3. Bit cons.  : final live cells  == 6
      4. Obj cons.  : final components  == 2

    The margin parameter (default 1.0) prevents micro-jitter exploits where
    the objects shift by a sub-pixel amount and satisfy the bare inequalities
    without undergoing a meaningful collision.
    """

    name = "MarginalDynamicCollisionFitness"

    def __init__(
        self,
        horizon: int = 100,
        grid_size: int = _DYN_GRID_SIZE,
        margin: float = 1.0,
        rule: dict | None = None,
    ) -> None:
        self.horizon   = int(horizon)
        self.grid_size = int(grid_size)
        self.margin    = float(margin)
        self.rule      = rule

    def evaluate(self, rule_dict: dict | None = None) -> dict:
        rule_dict = rule_dict if rule_dict is not None else self.rule
        if rule_dict is None:
            raise ValueError("MarginalDynamicCollisionFitness: no rule supplied")

        lut  = rule_dict_to_lut(rule_dict)
        grid = _make_dynamic_collision_grid(self.grid_size)

        initial_distance = _two_object_com_distance(grid)
        if initial_distance is None:
            return self._fail({
                "initial_distance":   None,
                "midpoint_distance":  None,
                "final_distance":     None,
                "final_bit_count":    int(grid.sum()),
                "final_object_count": 0,
            })

        midpoint_step     = self.horizon // 2
        midpoint_distance: float | None = None
        for step in range(1, self.horizon + 1):
            grid = step_grid(grid, lut)
            if step == midpoint_step:
                midpoint_distance = _two_object_com_distance(grid)

        final_bit_count   = int(grid.sum())
        _, final_object_count = label(grid, structure=_DYN_LABEL_STRUCTURE)
        final_object_count    = int(final_object_count)
        final_distance        = _two_object_com_distance(grid)

        metrics = {
            "initial_distance":   float(initial_distance),
            "midpoint_distance":  (
                float(midpoint_distance) if midpoint_distance is not None else None
            ),
            "final_distance": (
                float(final_distance) if final_distance is not None else None
            ),
            "final_bit_count":    final_bit_count,
            "final_object_count": final_object_count,
            "margin":             self.margin,
        }

        if midpoint_distance is None or final_distance is None:
            return self._fail(metrics)

        approach   = midpoint_distance < initial_distance  - self.margin
        recession  = final_distance    > midpoint_distance + self.margin
        bits_ok    = final_bit_count   == _DYN_INITIAL_BITS
        objects_ok = final_object_count == _DYN_INITIAL_OBJECTS

        metrics["approach"]   = bool(approach)
        metrics["recession"]  = bool(recession)
        metrics["bits_ok"]    = bool(bits_ok)
        metrics["objects_ok"] = bool(objects_ok)

        fitness = 1.0 if (approach and recession and bits_ok and objects_ok) else 0.0
        metrics["fitness"] = float(fitness)
        return metrics

    @staticmethod
    def _fail(metrics: dict) -> dict:
        metrics.setdefault("approach",   False)
        metrics.setdefault("recession",  False)
        metrics.setdefault("bits_ok",    False)
        metrics.setdefault("objects_ok", False)
        metrics["fitness"] = 0.0
        return metrics

    def __call__(self, rule_dict: dict | None = None) -> dict:
        return self.evaluate(rule_dict)


# ── Rule loading ─────────────────────────────────────────────────────────────

PROJECT_ROOT  = Path(__file__).parent.parent
_RULE_PRIMARY  = PROJECT_ROOT / "archive" / "iter_188" / "results" / "champion_rule.json"
_RULE_FALLBACK = PROJECT_ROOT / "archive" / "iter_188" / "results" / "dynamic_champion_rule.json"


def load_iter188_champion() -> dict:
    for path in (_RULE_PRIMARY, _RULE_FALLBACK):
        if path.exists():
            with open(path) as f:
                payload = json.load(f)
            rule_dict = {int(k): int(v) for k, v in payload["rule_dict"].items()}
            print(f"Loaded iter_188 champion from: {path}")
            return rule_dict
    raise FileNotFoundError(
        f"iter_188 champion rule not found at:\n"
        f"  {_RULE_PRIMARY}\n"
        f"  {_RULE_FALLBACK}"
    )


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    rule_dict = load_iter188_champion()

    fitness_fn = MarginalDynamicCollisionFitness(horizon=100, margin=1.0)
    metrics    = fitness_fn.evaluate(rule_dict)

    print(f"initial_distance  : {metrics['initial_distance']:.4f}")
    print(f"midpoint_distance : {metrics['midpoint_distance']}")
    print(f"final_distance    : {metrics['final_distance']}")
    print(f"final_bit_count   : {metrics['final_bit_count']}")
    print(f"final_object_count: {metrics['final_object_count']}")
    print(f"margin            : {metrics['margin']}")
    print(f"approach          : {metrics['approach']}")
    print(f"recession         : {metrics['recession']}")
    print(f"bits_ok           : {metrics['bits_ok']}")
    print(f"objects_ok        : {metrics['objects_ok']}")
    print(f"fitness           : {metrics['fitness']}")

    expected = 0.0
    if metrics["fitness"] == expected:
        print(f"\nSUCCESS: MarginalDynamicCollisionFitness correctly rejects "
              f"the micro-jitter exploit (fitness={metrics['fitness']})")
    else:
        print(f"\nFAILURE: expected fitness={expected}, got {metrics['fitness']}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
