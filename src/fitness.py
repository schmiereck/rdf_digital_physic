#!/usr/bin/env python3
"""
fitness.py

Velocity-stability fitness metric for hexagonal CA rules.
A rule with sustained, constant-velocity motion scores near 1.0.
A rule with decaying or erratic motion scores near 0.0.
"""

import math

import numpy as np


HEX_DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]


def _rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,  1, axis=1)
    nw = np.roll(w, -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    return lut[state]


def _center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def calculate_velocity_stability(
    rule_dict: dict,
    initial_state: np.ndarray,
    steps_per_window: int = 400,
    num_windows: int = 3,
) -> tuple:
    """
    Calculates fitness based on the stability of velocity over multiple time windows.

    A stable glider should have a constant velocity, meaning a very low standard deviation.
    Decaying motion will have a high standard deviation because early windows have high
    velocity and later windows approach zero.

    Returns (fitness, velocities, std_dev) where fitness = 1 / (1 + std_dev).
    """
    lut  = _rule_to_lut(rule_dict)
    grid = np.copy(initial_state)

    # Record COM at the start of each window
    com_checkpoints = [_center_of_mass(grid)]

    for _ in range(num_windows):
        for __ in range(steps_per_window):
            grid = _step_grid(grid, lut)
        com_checkpoints.append(_center_of_mass(grid))

    velocities = []
    for i in range(num_windows):
        sq, sr = com_checkpoints[i]
        eq, er = com_checkpoints[i + 1]
        displacement = math.sqrt((eq - sq) ** 2 + (er - sr) ** 2)
        # Total displacement per window — proportional to speed since all windows
        # are the same length. This keeps std_dev on a scale where
        # 1/(1+std_dev) meaningfully separates stable from decaying motion.
        velocities.append(displacement)

    if len(velocities) < 2:
        return 0.0, velocities, 0.0

    std_dev = float(np.std(velocities))
    fitness  = 1.0 / (1.0 + std_dev)

    return fitness, velocities, std_dev
