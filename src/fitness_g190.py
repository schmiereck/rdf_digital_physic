#!/usr/bin/env python3
"""
fitness_g190.py  —  GradedCollisionFitness for iter_190

Design rationale: MarginalDynamicCollisionFitness is binary (0.0 or 1.0),
producing a flat fitness landscape where partial progress earns nothing.
GradedCollisionFitness rewards partial progress by:

  1. conservation_score: smooth multiplier (1.0 = perfect, degrades gracefully).
  2. interaction_score: rewards the 'V-shaped' distance profile of a real collision
     (approach in first half + recession in second half) continuously.
  3. total_displacement: ensures rules that move particles at all score > 0.

Final formula:
    fitness = conservation_score * (interaction_score + total_displacement)

The two largest connected components in the grid are used as the particles.
This makes the function robust when objects briefly fragment during interaction.
"""

from __future__ import annotations

import math

import numpy as np
from scipy.ndimage import label, center_of_mass as ndimage_com

from evolution import rule_dict_to_lut, step_grid


# ── Grid configuration ───────────────────────────────────────────────────────

GRID_SIZE = 128

# Two 3-bit L-trominos placed on a collision course on the 128x128 torus.
_OBJECT_A = [(60, 40), (61, 40), (60, 41)]
_OBJECT_B = [(67, 87), (68, 87), (67, 88)]

# 8-connectivity so diagonally-adjacent tromino cells count as one object.
_LABEL_STRUCTURE = np.ones((3, 3), dtype=np.uint8)


def _make_grid(grid_size: int = GRID_SIZE) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in _OBJECT_A:
        grid[r % grid_size, c % grid_size] = 1
    for r, c in _OBJECT_B:
        grid[r % grid_size, c % grid_size] = 1
    return grid


# ── Helper: two-largest-object COMs ─────────────────────────────────────────

def _two_largest_coms(
    grid: np.ndarray,
) -> tuple[tuple[float, float], tuple[float, float]] | None:
    """Return COMs of the two largest connected components, or None if < 2 exist."""
    labels, n = label(grid, structure=_LABEL_STRUCTURE)
    if n < 2:
        return None
    # Sort components by size descending and pick the top two.
    sizes = sorted(
        ((lbl, int(np.sum(labels == lbl))) for lbl in range(1, n + 1)),
        key=lambda x: x[1],
        reverse=True,
    )
    top2_lbls = [sizes[0][0], sizes[1][0]]
    coms = ndimage_com(grid, labels, top2_lbls)
    return (tuple(coms[0]), tuple(coms[1]))  # type: ignore[return-value]


def _dist(
    com_a: tuple[float, float],
    com_b: tuple[float, float],
) -> float:
    return math.sqrt((com_a[0] - com_b[0]) ** 2 + (com_a[1] - com_b[1]) ** 2)


# ── Core fitness computation ─────────────────────────────────────────────────

def graded_collision_fitness(
    grid_initial: np.ndarray,
    grid_mid: np.ndarray,
    grid_final: np.ndarray,
) -> dict:
    """Compute GradedCollisionFitness from three grid snapshots.

    Parameters
    ----------
    grid_initial : grid at step 0
    grid_mid     : grid at the simulation midpoint (e.g. step 200)
    grid_final   : grid at the final step (e.g. step 400)

    Returns a dict containing 'fitness' and all diagnostic sub-scores.
    """
    initial_bits = int(grid_initial.sum())
    final_bits   = int(grid_final.sum())

    # conservation_score: 1.0 for perfect bit conservation, degrades gracefully.
    if initial_bits > 0:
        conservation_score = min(initial_bits, final_bits) / max(initial_bits, final_bits)
    else:
        conservation_score = 0.0

    # COMs of the two largest objects at each snapshot.
    coms_init  = _two_largest_coms(grid_initial)
    coms_mid   = _two_largest_coms(grid_mid)
    coms_final = _two_largest_coms(grid_final)

    initial_dist = _dist(*coms_init)  if coms_init  is not None else 0.0
    mid_dist     = _dist(*coms_mid)   if coms_mid   is not None else 0.0
    final_dist   = _dist(*coms_final) if coms_final is not None else 0.0

    # approach_score: rewards particles getting closer in the first half.
    approach_score = max(0.0, initial_dist - mid_dist)
    # recede_score: rewards particles moving apart in the second half.
    recede_score   = max(0.0, final_dist - mid_dist)
    # interaction_score: full reward for the V-shaped collision profile.
    interaction_score = approach_score + recede_score

    # total_displacement: sum of per-particle travel from start to finish.
    # Greedy assignment minimises total displacement (avoids label-swap artefacts).
    if coms_init is not None and coms_final is not None:
        a0, b0 = coms_init
        af, bf = coms_final
        disp_straight = _dist(a0, af) + _dist(b0, bf)
        disp_crossed  = _dist(a0, bf) + _dist(b0, af)
        total_displacement = min(disp_straight, disp_crossed)
    else:
        total_displacement = 0.0

    # Final formula: conservation multiplies the sum of interaction and movement.
    # A rule with poor conservation is penalised proportionally; a rule with no
    # movement at all scores 0 regardless of conservation.
    fitness = conservation_score * (interaction_score + total_displacement)

    return {
        "fitness":            float(fitness),
        "conservation_score": float(conservation_score),
        "approach_score":     float(approach_score),
        "recede_score":       float(recede_score),
        "interaction_score":  float(interaction_score),
        "total_displacement": float(total_displacement),
        "initial_dist":       float(initial_dist),
        "mid_dist":           float(mid_dist),
        "final_dist":         float(final_dist),
        "initial_bits":       initial_bits,
        "final_bits":         final_bits,
    }


# ── Class wrapper for evolutionary search ───────────────────────────────────

class GradedCollisionFitness:
    """Runs the simulation internally and scores it with graded_collision_fitness.

    Captures grid snapshots at step 0, the midpoint, and the final step, then
    delegates to graded_collision_fitness for the actual computation.
    """

    name = "GradedCollisionFitness"

    def __init__(
        self,
        horizon: int = 400,
        midpoint: int | None = None,
        grid_size: int = GRID_SIZE,
        rule: dict | None = None,
    ) -> None:
        self.horizon   = int(horizon)
        self.midpoint  = int(midpoint) if midpoint is not None else self.horizon // 2
        self.grid_size = int(grid_size)
        self.rule      = rule

    def evaluate(self, rule_dict: dict | None = None) -> dict:
        rule_dict = rule_dict if rule_dict is not None else self.rule
        if rule_dict is None:
            raise ValueError("GradedCollisionFitness: no rule supplied")

        lut          = rule_dict_to_lut(rule_dict)
        grid         = _make_grid(self.grid_size)
        grid_initial = grid.copy()
        grid_mid     = None

        for step in range(1, self.horizon + 1):
            grid = step_grid(grid, lut)
            if step == self.midpoint:
                grid_mid = grid.copy()

        if grid_mid is None:
            grid_mid = grid_initial.copy()

        return graded_collision_fitness(grid_initial, grid_mid, grid)

    def __call__(self, rule_dict: dict | None = None) -> dict:
        return self.evaluate(rule_dict)
