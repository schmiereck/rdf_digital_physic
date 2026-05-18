#!/usr/bin/env python3
"""
new_fitness.py

Fitness functions robust to the "puffer" exploit identified in iter_203.1.

DisplacementOverBoundingBoxFitness (formula class)
---------------------------------------------------
Takes pre-computed grids and metrics dict. Implements the core formula:

    fitness = cumulative_displacement / (1 + max_bounding_box_diagonal)

Bit conservation is enforced: if the initial and final bit counts differ,
the fitness is 0.0.

DisplacementOverBoundingBoxEvaluator (evolutionary loop evaluator)
------------------------------------------------------------------
Full-simulation wrapper around the formula. Compatible with run_evosg.py.
Runs the CA for `simulation_steps` steps, accumulating cumulative_displacement
and tracking max_bounding_box_diagonal at each step, then delegates to the
formula class. Registered as "DisplacementOverBoundingBoxFitness" in REGISTRY.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from evolution import center_of_mass, rule_dict_to_lut, step_grid
from fitness_simple_motion import BaseFitness


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Default seed: 3-bit L-tromino (offsets from grid centre)
L_TROMINO: list[tuple[int, int]] = [(-1, -1), (0, -1), (0, 0)]


def _make_particle_grid(
    particle: list[tuple[int, int]],
    grid_size: int = 128,
) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for dr, dc in particle:
        r = (centre + dr) % grid_size
        c = (centre + dc) % grid_size
        grid[r, c] = 1
    return grid


def _bounding_box_diagonal(grid: np.ndarray) -> float:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return 0.0
    h = int(rows.max()) - int(rows.min()) + 1
    w = int(cols.max()) - int(cols.min()) + 1
    return math.sqrt(h * h + w * w)


# ---------------------------------------------------------------------------
# Formula class (takes pre-computed grids + metrics dict)
# ---------------------------------------------------------------------------

class DisplacementOverBoundingBoxFitness(BaseFitness):
    """Fitness that rewards displacement while penalising structural bloat.

    The score is the ratio of cumulative displacement to the maximum
    bounding-box diagonal observed across all simulation steps.  The
    ``+1`` in the denominator prevents division by zero.

    Bit conservation is mandatory — a mismatch in live-cell count between
    initial and final grids immediately yields a fitness of ``0.0``.

    Parameters / contract
    ---------------------
    ``__call__(initial_grid, final_grid, metrics) -> float``
        *initial_grid* – 2-D ``np.ndarray`` of the seed configuration.
        *final_grid*   – 2-D ``np.ndarray`` after simulation completes.
        *metrics*      – dict with at least the keys
                         ``'cumulative_displacement'`` and
                         ``'max_bounding_box_diagonal'``.

    Returns
    -------
    float
        The fitness value (higher is better).
    """

    name = "DisplacementOverBoundingBoxFitness"

    def __call__(
        self,
        initial_grid: np.ndarray,
        final_grid: np.ndarray,
        metrics: dict,
    ) -> float:
        """Compute the fitness value from grid snapshots and pre-computed metrics."""

        initial_bits = int(initial_grid.sum())
        final_bits = int(final_grid.sum())

        if initial_bits != final_bits:
            return 0.0

        cumulative_displacement = metrics["cumulative_displacement"]
        max_bounding_box_diagonal = metrics["max_bounding_box_diagonal"]

        fitness = cumulative_displacement / (1 + max_bounding_box_diagonal)

        return float(fitness)


# ---------------------------------------------------------------------------
# Evolutionary loop evaluator (takes rule_dict, runs full simulation)
# ---------------------------------------------------------------------------

class DisplacementOverBoundingBoxEvaluator:
    """Full-simulation evaluator compatible with run_evosg.py.

    Runs the CA for ``simulation_steps`` steps, accumulating
    ``cumulative_displacement`` (sum of per-step CoM movements) and tracking
    ``max_bounding_box_diagonal`` at every step.  Delegates to
    ``DisplacementOverBoundingBoxFitness`` for the final score.

    Registered as ``"DisplacementOverBoundingBoxFitness"`` in the REGISTRY
    so it can be selected via ``--fitness DisplacementOverBoundingBoxFitness``.

    Calling convention (matches fitness_v2.py classes):
        fitness, metrics = evaluator(rule_dict)   # 2-tuple
        metrics_dict = evaluator.evaluate(rule_dict)  # dict
    """

    name = "DisplacementOverBoundingBoxFitness"

    def __init__(
        self,
        grid_size: int = 128,
        simulation_steps: int = 200,
        particle: list | None = None,
    ) -> None:
        self.grid_size = int(grid_size)
        self.simulation_steps = int(simulation_steps)
        self.particle = particle if particle is not None else L_TROMINO
        self._formula = DisplacementOverBoundingBoxFitness()

    def evaluate(self, rule_dict: dict) -> dict:
        lut = rule_dict_to_lut(rule_dict)
        grid = _make_particle_grid(self.particle, self.grid_size)
        initial_grid = grid.copy()
        initial_bits = int(grid.sum())

        prev_com = center_of_mass(grid)
        cumulative_displacement = 0.0
        max_bbox_diagonal = _bounding_box_diagonal(grid)

        for _step in range(self.simulation_steps):
            grid = step_grid(grid, lut)

            current_com = center_of_mass(grid)
            dx = current_com[0] - prev_com[0]
            dy = current_com[1] - prev_com[1]
            cumulative_displacement += math.sqrt(dx * dx + dy * dy)
            prev_com = current_com

            diag = _bounding_box_diagonal(grid)
            if diag > max_bbox_diagonal:
                max_bbox_diagonal = diag

        final_bits = int(grid.sum())

        metrics = {
            "cumulative_displacement": cumulative_displacement,
            "max_bounding_box_diagonal": max_bbox_diagonal,
        }
        fitness = self._formula(initial_grid, grid, metrics)

        return {
            "fitness": fitness,
            "reason": "ok" if initial_bits == final_bits else "bit_conservation_failed",
            "cumulative_displacement": float(cumulative_displacement),
            "max_bounding_box_diagonal": float(max_bbox_diagonal),
            "initial_bits": initial_bits,
            "final_bits": final_bits,
        }

    def __call__(self, rule_dict: dict) -> tuple[float, dict]:
        m = self.evaluate(rule_dict)
        return (float(m["fitness"]), m)
