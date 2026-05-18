#!/usr/bin/env python3
"""
fitness_functions.py

A library of fitness functions for evaluating cellular-automaton rules on the
128x128 toroidal hexagonal grid used throughout this project.

NetDisplacementFitness
-----------------------
Designed to defeat the 'compact oscillator' and 'puffer' exploits identified
in iter_203.  Two complementary mechanisms:

  1. **Net displacement** — measures the Euclidean distance between the
     centre-of-mass at t=0 and t=max_steps.  Stationary oscillators that
     merely wiggle in place have a net displacement ≈ 0 regardless of how
     many intermediate steps they travelled.

  2. **Bounding-box penalty** — divides by ``1 + final_bb_area`` so that
     rules producing large, diffuse patterns (puffers) are suppressed even
     if they manage non-zero net displacement.

  3. **Bit conservation** — if the initial or final bit count does not
     match the seed's bit count (3 for the L-tromino), fitness is forced
     to 0.0.  This rejects annihilating/explosive rules that change particle
     mass.

    fitness = net_displacement / (1 + final_bb_area)

Parameters
----------
grid_size : int
    Side length of the square toroidal grid (default 128).
simulation_steps : int
    Total simulation steps (default 250).
particle : list of (int, int)
    Seed particle as (dr, dc) offsets from grid centre.
    Defaults to the 3-bit L-tromino [(0,0), (0,1), (1,1)].
expected_bits : int
    Number of bits the seed must have for conservation to pass.
    Defaults to 3 (L-tromino).
"""

from __future__ import annotations

import math
from typing import Any

import numpy as np

from evolution import center_of_mass, rule_dict_to_lut, step_grid

# ---------------------------------------------------------------------------
# Default seed — 3-bit L-tromino
# ---------------------------------------------------------------------------

LTROMINO: list[tuple[int, int]] = [(0, 0), (0, 1), (1, 1)]

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
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    centre = grid_size // 2
    for dr, dc in particle:
        r = (centre + dr) % grid_size
        c = (centre + dc) % grid_size
        grid[r, c] = 1
    return grid


# ---------------------------------------------------------------------------
# Fitness classes
# ---------------------------------------------------------------------------

class NetDisplacementFitness:
    """Fitness based on net displacement of the particle's centre of mass.

    Evaluates a CA rule by simulating the seed particle for the full
    duration and then measuring:

        1. Net displacement = Euclidean distance between CoM at t=0 and CoM
           at t=max_steps.
        2. Final bounding-box area (defence against 'puffer' exploit).
        3. Bit conservation (defence against annihilating/explosive rules).

    Score formula::

        fitness = net_displacement / (1 + final_bb_area)

    If the initial or final bit count does not equal ``expected_bits``
    (3 for the L-tromino seed), fitness is returned as ``0.0``.

    Parameters
    ----------
    grid_size : int
        Side length of the square toroidal grid (default 128).
    simulation_steps : int
        Total simulation steps (default 250).
    particle : list of (int, int)
        Seed particle as (dr, dc) offsets from grid centre.
        Defaults to the 3-bit L-tromino.
    expected_bits : int
        Number of bits the seed must have for conservation to pass.
        Defaults to 3 (L-tromino).
    """

    name = "NetDisplacementFitness"

    def __init__(
        self,
        grid_size:        int              = 128,
        simulation_steps: int              = 250,
        particle:         list | None      = None,
        expected_bits:    int              = 3,
    ) -> None:
        self.grid_size      = int(grid_size)
        self.simulation_steps = int(simulation_steps)
        self.particle       = particle if particle is not None else LTROMINO
        self.expected_bits  = int(expected_bits)

    # ------------------------------------------------------------------

    def evaluate(self, rule_dict: dict) -> dict[str, Any]:
        """Evaluate *rule_dict* and return a metrics dict.

        Returns
        -------
        dict
            Always contains ``"fitness"`` (float ≥ 0).
            Additional keys vary by outcome:
            - ``"reason"``          : "ok" | "bit_conservation_failed"
            - ``"initial_bits"``    : seed bit count
            - ``"final_bits"``      : bit count at t=max_steps
            - ``"initial_com"``     : [row, col] of CoM at t=0
            - ``"final_com"``       : [row, col] of CoM at t=max_steps
            - ``"net_displacement"``: Euclidean distance (initial→final CoM)
            - ``"final_bb_area"``   : bounding-box area at t=max_steps
        """
        lut  = rule_dict_to_lut(rule_dict)
        grid = _make_particle_grid(self.particle, self.grid_size)

        initial_com  = center_of_mass(grid)
        initial_bits = int(grid.sum())

        # Simulate for the full duration
        for _ in range(self.simulation_steps):
            grid = step_grid(grid, lut)

        final_com    = center_of_mass(grid)
        final_bits   = int(grid.sum())

        # ── Bit-conservation gate ────────────────────────────────────────
        if initial_bits != self.expected_bits or final_bits != self.expected_bits:
            return {
                "fitness":          0.0,
                "reason":           "bit_conservation_failed",
                "initial_bits":     initial_bits,
                "final_bits":       final_bits,
                "expected_bits":    self.expected_bits,
            }

        # ── Net displacement ─────────────────────────────────────────────
        dx = final_com[0] - initial_com[0]
        dy = final_com[1] - initial_com[1]
        net_displacement = math.sqrt(dx * dx + dy * dy)

        # ── Bounding-box area ────────────────────────────────────────────
        final_bb_area = _bounding_box_area(grid)

        # ── Fitness score ────────────────────────────────────────────────
        fitness = net_displacement / (1.0 + float(final_bb_area))

        return {
            "fitness":            float(fitness),
            "reason":             "ok",
            "initial_com":        list(initial_com),
            "final_com":          list(final_com),
            "net_displacement":   float(net_displacement),
            "final_bb_area":      final_bb_area,
            "initial_bits":       initial_bits,
            "final_bits":         final_bits,
        }

    def __call__(self, rule_dict: dict) -> tuple[float, dict[str, Any]]:
        """Convenience callable returning ``(fitness, metrics_dict)``.

        Returning a 2-tuple here prevents the
        ``ValueError: too many values to unpack`` that occurs when an
        evolutionary loop tries to unpack the canonical dict directly
        (iterating a dict yields its keys, of which there are more than 2).
        """
        m = self.evaluate(rule_dict)
        result: tuple[float, dict[str, Any]] = (float(m["fitness"]), m)
        assert isinstance(result, tuple) and len(result) == 2, (
            "NetDisplacementFitness.__call__ must return a 2-tuple "
            "(fitness: float, metrics: dict)."
        )
        return result


# ---------------------------------------------------------------------------
# Module-level convenience wrapper
# ---------------------------------------------------------------------------

def evaluate(rule_dict: dict) -> dict[str, Any]:
    """Evaluate *rule_dict* with the default NetDisplacementFitness settings."""
    return NetDisplacementFitness().evaluate(rule_dict)
