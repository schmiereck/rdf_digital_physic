#!/usr/bin/env python3
"""
fitness_simple_motion.py

SimpleMotionFitness: rewards total displacement while penalising both
velocity instability and structural bloat (large peak bit counts).

The procedure mirrors StableVelocityFitness for the motion measurements
(2000 steps on the L-tromino seed, four 400-step post-settling windows),
but the score formula is:

    fitness = total_displacement
              / ((1 + std_dev_velocity) * (1 + max_bit_count))

where
  * total_displacement  = sum of the four per-window displacements
                          (same windows as StableVelocityFitness)
  * std_dev_velocity    = std dev of those same four per-window displacements
  * max_bit_count       = maximum number of live cells observed at any
                          point during the 2000-step simulation
"""

import math

import numpy as np

from evolution import (
    LTROMINO_CELLS,
    make_ltromino_grid,
    rule_dict_to_lut,
    step_grid,
    center_of_mass,
)

TOTAL_STEPS       = 2000
CHECKPOINT_STEPS  = [400, 800, 1200, 1600, 2000]
INITIAL_BIT_COUNT = len(LTROMINO_CELLS)  # 3

_VELOCITY_WINDOWS = [
    (400,  800),
    (800,  1200),
    (1200, 1600),
    (1600, 2000),
]


class BaseFitness:
    """Minimal base class establishing the fitness-evaluation API.

    Concrete subclasses override ``evaluate(rule_dict)`` to return a
    dict that contains at least the key ``"fitness"``.
    """

    name: str = "BaseFitness"

    def evaluate(self, rule_dict: dict) -> dict:
        raise NotImplementedError

    def __call__(self, rule_dict: dict) -> dict:
        return self.evaluate(rule_dict)


class SimpleMotionFitness(BaseFitness):
    """Fitness that rewards motion and penalises both velocity instability
    and large peak bit counts (complexity bloat)."""

    name = "SimpleMotionFitness"

    def __init__(self, grid_size: int = 128, steps: int = 2000):
        self.grid_size = grid_size
        self.steps = steps
        # Scale checkpoint and window steps proportionally to total steps
        ratio = steps / 2000
        scaled = [max(1, int(s * ratio)) for s in CHECKPOINT_STEPS]
        # Ensure the last checkpoint equals total steps
        scaled[-1] = steps
        self._checkpoint_steps = scaled
        self._velocity_windows = list(zip(scaled[:-1], scaled[1:]))
        # L-tromino centred in grid: mirror LTROMINO_CELLS pattern at grid_size//2
        c = grid_size // 2 - 1
        self._ltromino_cells = [(c, c), (c + 1, c), (c + 1, c + 1)]

    def evaluate(self, rule_dict: dict) -> dict:
        lut  = rule_dict_to_lut(rule_dict)
        grid = make_ltromino_grid(
            grid_size=self.grid_size, cells=self._ltromino_cells
        )

        step       = 0
        max_bits   = int(grid.sum())
        com_at     = {0: center_of_mass(grid)}

        for target in self._checkpoint_steps:
            while step < target:
                grid = step_grid(grid, lut)
                step += 1
                bits = int(grid.sum())
                if bits > max_bits:
                    max_bits = bits
            com_at[target] = center_of_mass(grid)

        velocities = []
        for t_start, t_end in self._velocity_windows:
            r0, c0 = com_at[t_start]
            r1, c1 = com_at[t_end]
            velocities.append(math.sqrt((r1 - r0) ** 2 + (c1 - c0) ** 2))

        total_displacement = float(sum(velocities))
        mean_velocity      = float(np.mean(velocities))
        std_dev_velocity   = float(np.std(velocities))
        final_bit_count    = int(grid.sum())

        fitness = total_displacement / (
            (1.0 + std_dev_velocity) * (1.0 + max_bits)
        )

        return {
            "fitness":            fitness,
            "total_displacement": total_displacement,
            "mean_velocity":      mean_velocity,
            "std_dev_velocity":   std_dev_velocity,
            "max_bit_count":      max_bits,
            "initial_bit_count":  INITIAL_BIT_COUNT,
            "final_bit_count":    final_bit_count,
            "velocities":         velocities,
        }


_DEFAULT = SimpleMotionFitness()


def evaluate(rule_dict: dict) -> dict:
    """Module-level convenience wrapper matching the StableVelocityFitness API."""
    return _DEFAULT.evaluate(rule_dict)
