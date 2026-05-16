#!/usr/bin/env python3
"""
fitness_functions.py

A library of fitness functions for evaluating cellular-automaton rules on the
128x128 toroidal hexagonal grid used throughout this project.

CollisionFitness
----------------
Rewards rules that produce *elastic* head-on collisions between two 3-bit
L-tromino gliders. The score combines bit conservation and object
conservation using a symmetric, clipped formula that peaks at 1.0:

    bit_ratio = min(initial/final, final/initial)
    obj_ratio = min(2/final_objs, final_objs/2)
    fitness   = bit_ratio * obj_ratio

A perfect elastic collision (two 3-bit objects emerge from two 3-bit objects)
yields 1.0. Annihilation, fusion, or explosion all push the score below 1.0.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import label

from evolution import rule_dict_to_lut, step_grid
from fitness_simple_motion import BaseFitness


# ── Configuration ────────────────────────────────────────────────────────────

GRID_SIZE = 128          # toroidal grid edge length
SIM_STEPS = 100          # simulation steps per evaluation

# Seed 1: standard L-tromino anchored at (48, 64). Moves East (+row).
# Shape: (r, c), (r+1, c), (r+1, c+1).
_GLIDER_A = [(48, 64), (49, 64), (49, 65)]

# Seed 2: 180-rotated L-tromino anchored at (80, 64). Moves West (-row).
# Rotated shape: (r, c), (r, c+1), (r+1, c+1).
_GLIDER_B = [(80, 64), (80, 65), (81, 65)]

INITIAL_BIT_COUNT = len(_GLIDER_A) + len(_GLIDER_B)  # 6
INITIAL_OBJECT_COUNT = 2

# 8-connectivity structuring element for scipy.ndimage.label — required so
# diagonally-adjacent live cells of a tromino are counted as one object.
_LABEL_STRUCTURE = np.ones((3, 3), dtype=np.uint8)


def _make_collision_grid(grid_size: int = GRID_SIZE) -> np.ndarray:
    """Return a `grid_size`x`grid_size` toroidal grid seeded with both gliders."""
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in _GLIDER_A:
        grid[r % grid_size, c % grid_size] = 1
    for r, c in _GLIDER_B:
        grid[r % grid_size, c % grid_size] = 1
    return grid


class CollisionFitness(BaseFitness):
    """Fitness function for discovering rules with elastic head-on collisions.

    Two 3-bit L-tromino gliders are placed on a 128x128 toroidal grid on a
    direct collision course (one at row 48, one at row 80, both at column 64).
    After running the rule for 100 steps the bit count and connected-component
    count are measured.

    Score formula (higher is better, 1.0 is ideal)::

        fitness = (initial_bit_count / final_bit_count)
                  * (2 / final_object_count)

    Edge cases:
      * final_bit_count == 0     -> fitness = 0.0   (annihilation)
      * final_object_count == 0  -> fitness = 0.0   (empty grid)

    The class is callable. The ``rule`` argument may be supplied at
    construction time (so it acts as a configured functor) or passed directly
    to ``__call__`` / ``evaluate``.
    """

    name = "CollisionFitness"

    def __init__(
        self,
        rule: dict | None = None,
        grid_size: int = GRID_SIZE,
        steps: int = SIM_STEPS,
    ) -> None:
        self.rule = rule
        self.grid_size = grid_size
        self.steps = steps
        self._initial_bits = INITIAL_BIT_COUNT
        self._initial_objects = INITIAL_OBJECT_COUNT

    # ── core evaluation ──────────────────────────────────────────────────

    def evaluate(self, rule_dict: dict | None = None) -> dict:
        """Run the head-on collision and return the fitness metrics.

        Parameters
        ----------
        rule_dict : dict | None
            CA rule mapping neighbourhood index -> output state. If omitted,
            ``self.rule`` (passed at construction) is used.
        """
        rule_dict = rule_dict if rule_dict is not None else self.rule
        if rule_dict is None:
            raise ValueError("CollisionFitness: no rule supplied")

        lut = rule_dict_to_lut(rule_dict)
        grid = _make_collision_grid(self.grid_size)

        for _ in range(self.steps):
            grid = step_grid(grid, lut)

        final_bit_count = int(grid.sum())

        if final_bit_count == 0:
            return {
                "fitness":             0.0,
                "initial_bit_count":   self._initial_bits,
                "final_bit_count":     0,
                "final_object_count":  0,
            }

        _, final_object_count = label(grid, structure=_LABEL_STRUCTURE)
        if final_object_count == 0:
            return {
                "fitness":             0.0,
                "initial_bit_count":   self._initial_bits,
                "final_bit_count":     final_bit_count,
                "final_object_count":  0,
            }

        initial_bit_count = self._initial_bits
        bit_ratio = min(initial_bit_count / final_bit_count, final_bit_count / initial_bit_count) if final_bit_count > 0 else 0
        obj_ratio = min(2 / final_object_count, final_object_count / 2) if final_object_count > 0 else 0
        fitness = bit_ratio * obj_ratio

        return {
            "fitness":             float(fitness),
            "initial_bit_count":   self._initial_bits,
            "final_bit_count":     final_bit_count,
            "final_object_count":  int(final_object_count),
        }

    # ── callable sugar ───────────────────────────────────────────────────

    def __call__(self, rule_dict: dict | None = None) -> dict:
        return self.evaluate(rule_dict)


# ── Module-level convenience wrapper ────────────────────────────────────────

def evaluate(rule_dict: dict) -> dict:
    """Evaluate *rule_dict* with the default CollisionFitness settings."""
    return CollisionFitness().evaluate(rule_dict)
