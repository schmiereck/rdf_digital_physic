#!/usr/bin/env python3
"""
fitness_functions.py

A library of fitness functions for evaluating cellular-automaton rules on the
128×128 toroidal hexagonal grid used throughout this project.

Currently provides:
  CollisionFitness — rewards rules that produce elastic head-on collisions
                     between two L-tromino gliders (bit conservation).
"""

import numpy as np

from evolution import rule_dict_to_lut, step_grid
from fitness_simple_motion import BaseFitness

GRID_SIZE = 128
SIM_STEPS = 200

# Glider A: standard L-tromino anchored at (32, 64), moves East.
_GLIDER_A = [(32, 64), (33, 64), (33, 65)]

# Glider B: 180°-rotated L-tromino anchored at (96, 64), moves West.
_GLIDER_B = [(96, 64), (95, 64), (95, 63)]

INITIAL_BIT_COUNT = len(_GLIDER_A) + len(_GLIDER_B)  # 6


def _make_collision_grid() -> np.ndarray:
    """Return a 128×128 grid seeded with both head-on gliders (6 bits total)."""
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in _GLIDER_A:
        grid[r, c] = 1
    for r, c in _GLIDER_B:
        grid[r, c] = 1
    return grid


class CollisionFitness(BaseFitness):
    """Fitness function for discovering rules with elastic head-on collisions.

    Two 3-bit L-tromino gliders are placed on a direct, head-on collision
    course (one at row 32, one at row 96, both at column 64) on a 128×128
    toroidal hexagonal grid.  The simulation runs for 200 steps — enough time
    for the particles to travel toward each other, collide, and (potentially)
    separate again.

    Scoring:
      * 1.0  if the final bit count equals the initial bit count (6),
             indicating that no bits were created or destroyed — the hallmark
             of a perfectly elastic collision.
      * 0.0  for any other final bit count (inelastic, annihilation, or growth).

    Parameters
    ----------
    grid_size : int
        Side length of the square toroidal grid.  Default 128.
    steps : int
        Number of simulation steps.  Default 200.

    Returns (from evaluate)
    -----------------------
    dict with keys:
      fitness           : float — 1.0 (elastic) or 0.0 (inelastic / other)
      initial_bit_count : int   — always 6
      final_bit_count   : int   — observed bit count after `steps` steps
    """

    name = "CollisionFitness"

    def __init__(self, grid_size: int = GRID_SIZE, steps: int = SIM_STEPS):
        self.grid_size = grid_size
        self.steps = steps
        # Scale glider positions proportionally when grid_size != 128
        scale = grid_size / 128
        half = grid_size // 2
        a_anchor = (round(32 * scale), half)
        b_anchor = (round(96 * scale), half)
        self._glider_a = [
            (a_anchor[0],     a_anchor[1]),
            (a_anchor[0] + 1, a_anchor[1]),
            (a_anchor[0] + 1, a_anchor[1] + 1),
        ]
        self._glider_b = [
            (b_anchor[0],     b_anchor[1]),
            (b_anchor[0] - 1, b_anchor[1]),
            (b_anchor[0] - 1, b_anchor[1] - 1),
        ]
        self._initial_bits = len(self._glider_a) + len(self._glider_b)

    def evaluate(self, rule_dict: dict) -> dict:
        """Evaluate a rule by running the head-on collision and checking bit conservation.

        Parameters
        ----------
        rule_dict : dict
            Mapping from neighbourhood-state index (int) to output-state index (int),
            as produced by the C2-symmetric rule generator in ``evolution.py``.

        Returns
        -------
        dict
            ``fitness``           : 1.0 if elastic, else 0.0
            ``initial_bit_count`` : int (6 for the default 128-grid configuration)
            ``final_bit_count``   : int
        """
        lut  = rule_dict_to_lut(rule_dict)
        grid = np.zeros((self.grid_size, self.grid_size), dtype=np.uint8)
        for r, c in self._glider_a:
            grid[r % self.grid_size, c % self.grid_size] = 1
        for r, c in self._glider_b:
            grid[r % self.grid_size, c % self.grid_size] = 1

        for _ in range(self.steps):
            grid = step_grid(grid, lut)

        final_bits = int(grid.sum())
        fitness = 1.0 if final_bits == self._initial_bits else 0.0

        return {
            "fitness":           fitness,
            "initial_bit_count": self._initial_bits,
            "final_bit_count":   final_bits,
        }


# Module-level default instance and convenience wrapper
_DEFAULT = CollisionFitness()


def evaluate(rule_dict: dict) -> dict:
    """Convenience wrapper: evaluate *rule_dict* with default CollisionFitness settings.

    Returns the same dict as ``CollisionFitness().evaluate(rule_dict)``.
    """
    return _DEFAULT.evaluate(rule_dict)
