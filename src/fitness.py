#!/usr/bin/env python3
"""
fitness.py

Fitness metrics for hexagonal CA rules.
  - calculate_velocity_stability: rewards sustained, constant-velocity motion.
  - CheckpointFitness: rewards stable bit-count throughout the simulation.
"""

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from simulator import Particle, Simulator


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


class CheckpointFitness:
    """Fitness metric that requires bit-count stability at regular checkpoints.

    A rule scores > 0 only if the particle's bit count equals the initial
    seed bit count at every checkpoint step.  The score itself is the
    Euclidean distance travelled by the centre of mass.  Any bit-count
    change at a checkpoint immediately returns 0.0 (early exit).
    """

    def __init__(self, checkpoints: list, simulation_steps: int):
        self.checkpoints = set(checkpoints)
        self.simulation_steps = simulation_steps

    def evaluate(self, rule, seed_bits: list) -> float:
        """Evaluate *rule* starting from *seed_bits* coordinates.

        Parameters
        ----------
        rule:
            A Rule instance (has .rule_dict).
        seed_bits:
            List of [row, col] pairs defining the initial live cells.

        Returns
        -------
        float
            Euclidean displacement of centre of mass, or 0.0 if any
            checkpoint reveals a bit-count mismatch.
        """
        grid = np.zeros((128, 128), dtype=np.uint8)
        for r, c in seed_bits:
            grid[r][c] = 1

        particle = Particle(grid)
        simulator = Simulator(rule)

        initial_bits = particle.bit_count
        initial_com = particle.center_of_mass()

        for step in range(1, self.simulation_steps + 1):
            simulator.step(particle)
            if step in self.checkpoints:
                if particle.bit_count != initial_bits:
                    return 0.0

        final_com = particle.center_of_mass()
        dx = final_com[0] - initial_com[0]
        dy = final_com[1] - initial_com[1]
        return math.sqrt(dx * dx + dy * dy)
