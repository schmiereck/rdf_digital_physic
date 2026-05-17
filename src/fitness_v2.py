#!/usr/bin/env python3
"""
fitness_v2.py

SparseGliderFitness: an exploit-resistant fitness function for v<c glider
discovery on a hexagonal toroidal grid.

Design
------
Builds on CheckpointFitness principles (fitness.py):
  - Bit conservation is checked at every checkpoint; any violation → 0.0.
  - Centre-of-mass displacement is accumulated across checkpoints.

Adds a sparsity term:
  - At each checkpoint:  sparsity = bit_count / bounding_box_area
  - High for compact particles (few bits, tight bounding box).
  - Low for diffuse patterns (bits scattered across a large bounding box).
  - Grid-filling exploits: the initial seed typically has very few bits
    (e.g., 4-cell T-tromino); an explosive rule changes the bit count
    at the first checkpoint, returning 0.0 immediately via the bit-
    conservation gate.

Final fitness = total_displacement × mean_sparsity_score
"""

import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from evolution import center_of_mass, rule_dict_to_lut, step_grid

# ---------------------------------------------------------------------------
# Default seed
# ---------------------------------------------------------------------------

# T-tromino (4 cells): row/col offsets from grid centre.
#
#   . X .     (dr=-1, dc=0)
#   X X X     (dr=0, dc=-1/0/+1)
#
T_TROMINO: list[tuple[int, int]] = [
    (-1,  0),
    ( 0, -1),
    ( 0,  0),
    ( 0,  1),
]

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _bounding_box_area(grid: np.ndarray) -> int:
    """Return the area (h × w) of the axis-aligned bounding box of live cells.

    Returns 1 when the grid is empty to avoid division by zero.
    """
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return 1
    h = int(rows.max()) - int(rows.min()) + 1
    w = int(cols.max()) - int(cols.min()) + 1
    return h * w


def _make_particle_grid(
    particle: list[tuple[int, int]],
    grid_size: int = 128,
) -> np.ndarray:
    """Return a zero grid with *particle* centred at (grid_size//2, grid_size//2)."""
    grid   = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for dr, dc in particle:
        r = (centre + dr) % grid_size
        c = (centre + dc) % grid_size
        grid[r, c] = 1
    return grid


# ---------------------------------------------------------------------------
# Fitness class
# ---------------------------------------------------------------------------

class SparseGliderFitness:
    """Exploit-resistant fitness for v<c glider discovery.

    At each checkpoint step the evaluator:
      1. Checks bit conservation (current bits == initial bits).
         Any violation immediately returns fitness 0.0.
      2. Records the inter-checkpoint centre-of-mass displacement.
      3. Computes  sparsity = bit_count / bounding_box_area.

    Final fitness = total_displacement * mean_sparsity_score.

    The bit-conservation gate is the primary defence against grid-filling
    exploits: an explosive rule changes the bit count within the first few
    steps, so it is rejected at the earliest checkpoint.  The sparsity term
    provides a secondary defence against diffuse, large-bounding-box patterns
    that somehow conserve bits: their low density ratio suppresses fitness.

    Parameters
    ----------
    grid_size : int
        Side length of the square toroidal grid (default 128).
    simulation_steps : int
        Total simulation steps (default 200).
    checkpoint_every : int
        Steps between consecutive checkpoints (default 50).
    particle : list of (int, int)
        Seed particle as (dr, dc) offsets from grid centre.
        Defaults to the 4-cell T-tromino used in iter_197+.
    """

    name = "SparseGliderFitness"

    def __init__(
        self,
        grid_size:        int              = 128,
        simulation_steps: int              = 200,
        checkpoint_every: int              = 50,
        particle:         list | None      = None,
    ) -> None:
        self.grid_size        = int(grid_size)
        self.simulation_steps = int(simulation_steps)
        self.checkpoint_every = int(checkpoint_every)
        self.particle         = particle if particle is not None else T_TROMINO
        self.checkpoints      = set(range(
            self.checkpoint_every,
            self.simulation_steps + 1,
            self.checkpoint_every,
        ))

    # ------------------------------------------------------------------

    def evaluate(self, rule_dict: dict) -> dict:
        """Evaluate *rule_dict* and return a metrics dict.

        Returns
        -------
        dict
            Always contains ``"fitness"`` (float ≥ 0).
            Additional keys vary by outcome:
            - ``"reason"`` : "ok" | "bit_conservation_failed"
            - ``"step_failed"``    : first step where conservation failed
            - ``"initial_bits"``   : seed bit count
            - ``"current_bits"``   : bit count at failure step
            - ``"total_displacement"`` : sum of inter-checkpoint displacements
            - ``"mean_sparsity"``  : average of per-checkpoint sparsity scores
            - ``"sparsity_scores"``: list of per-checkpoint sparsity values
            - ``"displacements"``  : list of inter-checkpoint displacements
        """
        lut  = rule_dict_to_lut(rule_dict)
        grid = _make_particle_grid(self.particle, self.grid_size)

        initial_bits = int(grid.sum())
        prev_com     = center_of_mass(grid)

        sparsity_scores: list[float] = []
        displacements:   list[float] = []

        for step in range(1, self.simulation_steps + 1):
            grid = step_grid(grid, lut)

            if step in self.checkpoints:
                current_bits = int(grid.sum())

                # ── Hard gate: bit conservation ──────────────────────────
                if current_bits != initial_bits:
                    return {
                        "fitness":       0.0,
                        "reason":        "bit_conservation_failed",
                        "step_failed":   step,
                        "initial_bits":  initial_bits,
                        "current_bits":  current_bits,
                        "sparsity_scores": sparsity_scores,
                        "displacements":   displacements,
                    }

                # ── Sparsity: compact particles score high ────────────────
                bbox_area     = _bounding_box_area(grid)
                sparsity      = current_bits / bbox_area
                sparsity_scores.append(float(sparsity))

                # ── Displacement since last checkpoint ────────────────────
                current_com = center_of_mass(grid)
                d = math.sqrt(
                    (current_com[0] - prev_com[0]) ** 2
                    + (current_com[1] - prev_com[1]) ** 2
                )
                displacements.append(float(d))
                prev_com = current_com

        total_displacement = sum(displacements)
        mean_sparsity = (
            sum(sparsity_scores) / len(sparsity_scores)
            if sparsity_scores else 0.0
        )
        fitness = total_displacement * mean_sparsity

        return {
            "fitness":            float(fitness),
            "reason":             "ok",
            "total_displacement": float(total_displacement),
            "mean_sparsity":      float(mean_sparsity),
            "sparsity_scores":    sparsity_scores,
            "displacements":      displacements,
            "initial_bits":       initial_bits,
            "final_bits":         int(grid.sum()),
        }

    def __call__(self, rule_dict: dict) -> tuple[float, dict]:
        """Convenience callable form.

        Returns ``(fitness, metrics_dict)`` so callers can write either::

            metrics = fit.evaluate(rule)        # dict (canonical form)
            fitness, metrics = fit(rule)        # 2-tuple (loop-friendly form)

        Returning a 2-tuple here prevents the ``ValueError: too many values to
        unpack (expected 2)`` that occurs when an evolutionary loop tries to
        unpack the canonical dict directly (iterating a dict yields its keys,
        of which there are more than 2).
        """
        m = self.evaluate(rule_dict)
        return float(m["fitness"]), m
