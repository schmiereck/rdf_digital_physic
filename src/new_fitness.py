#!/usr/bin/env python3
"""
new_fitness.py

A fitness function robust to the "puffer" exploit identified in iter_203.1.

DisplacementOverBoundingBoxFitness
-----------------------------------
Instead of rewarding raw displacement (which puffers can inflate by
expanding their bounding box without achieving coherent motion), this
fitness normalises total displacement by the *size* of the object as
measured by its maximum bounding-box diagonal.  A puffer that grows
enormously will incur a large denominator, keeping its score low.

    fitness = cumulative_displacement / (1 + max_bounding_box_diagonal)

Bit conservation is enforced: if the initial and final bit counts differ,
the fitness is 0.0.
"""

from __future__ import annotations

import numpy as np

from fitness_simple_motion import BaseFitness


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

    # ── core evaluation ──────────────────────────────────────────────────

    def __call__(
        self,
        initial_grid: np.ndarray,
        final_grid: np.ndarray,
        metrics: dict,
    ) -> float:
        """Compute the fitness value from grid snapshots and pre-computed metrics."""

        # 1. Bit conservation check
        initial_bits = int(initial_grid.sum())
        final_bits = int(final_grid.sum())

        if initial_bits != final_bits:
            return 0.0

        # 2. Normalised displacement score
        cumulative_displacement = metrics["cumulative_displacement"]
        max_bounding_box_diagonal = metrics["max_bounding_box_diagonal"]

        fitness = cumulative_displacement / (1 + max_bounding_box_diagonal)

        return float(fitness)
