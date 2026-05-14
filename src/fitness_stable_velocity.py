#!/usr/bin/env python3
"""
fitness_stable_velocity.py

StableVelocityFitness: rewards sustained, coherent motion and penalises
instability and growth.

Procedure:
  1. Run 2000 steps on the L-tromino seed (3 bits on a 128x128 toroidal grid).
  2. Record the centre-of-mass (COM) at steps 400, 800, 1200, 1600, 2000.
     Steps 0-400 are a settling period and are not used for velocity.
  3. Compute displacements for the four 400-step windows after settling:
     400->800, 800->1200, 1200->1600, 1600->2000.
  4. mean_velocity    = mean of those four displacements.
     std_dev_velocity = std dev of those four displacements.
  5. fitness = (mean_velocity / (1 + std_dev_velocity))
               * (initial_bit_count / final_bit_count)
     If final_bit_count == 0, fitness = 0.
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


def evaluate(rule_dict: dict) -> dict:
    """Evaluate *rule_dict* using the StableVelocityFitness metric.

    Returns a dict containing fitness and all supporting metrics.
    """
    lut  = rule_dict_to_lut(rule_dict)
    grid = make_ltromino_grid()

    step   = 0
    com_at = {}  # step_number -> (row, col) COM

    for target in CHECKPOINT_STEPS:
        while step < target:
            grid = step_grid(grid, lut)
            step += 1
        com_at[target] = center_of_mass(grid)

    velocities = []
    for t_start, t_end in _VELOCITY_WINDOWS:
        r0, c0 = com_at[t_start]
        r1, c1 = com_at[t_end]
        velocities.append(math.sqrt((r1 - r0) ** 2 + (c1 - c0) ** 2))

    mean_velocity    = float(np.mean(velocities))
    std_dev_velocity = float(np.std(velocities))
    final_bit_count  = int(grid.sum())

    if final_bit_count == 0:
        fitness = 0.0
    else:
        fitness = (mean_velocity / (1.0 + std_dev_velocity)) * (
            INITIAL_BIT_COUNT / final_bit_count
        )

    return {
        "fitness":           fitness,
        "mean_velocity":     mean_velocity,
        "std_dev_velocity":  std_dev_velocity,
        "initial_bit_count": INITIAL_BIT_COUNT,
        "final_bit_count":   final_bit_count,
        "velocities":        velocities,
        "com_checkpoints":   {t: list(com_at[t]) for t in CHECKPOINT_STEPS},
    }
