#!/usr/bin/env python3
"""
fitness_v_lessthan_c.py

Fitness functions specifically for the v < c search regime.

LateWindowDisplacementFitness
-----------------------------
A variant of ``NetDisplacementFitness`` that measures the Euclidean distance
between the centre of mass at simulation step 500 and step 1000 only.

This defeats the 'transient drift' exploit identified in **iter_213**, where
an initial settling phase (steps 0-500) registers a false positive for motion.
By ignoring the first 500 steps, we only reward *sustained* movement that
persists well into the simulation, filtering out rules that drift briefly
during an initial transient before stalling.

    fitness = late_window_displacement / (1 + final_bb_area)

See ``fitness_functions.NetDisplacementFitness`` for the full parameter and
return-value documentation (identical, except the displacement is computed
over the late window instead of the full run).

Parameters
----------
grid_size : int
    Side length of the square toroidal grid (default 128).
simulation_steps : int
    Total simulation steps (default 1001; window is [500, 1000]).
window_start : int
    Start of the displacement window (default 500).
window_end : int
    End of the displacement window (default 1000).
particle : list of (int, int)
    Seed particle as (dr, dc) offsets from grid centre.
    Defaults to the 3-bit L-tromino.
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

class LateWindowDisplacementFitness:
    """Fitness based on centre-of-mass displacement in a late simulation window.

    Evaluates a CA rule by simulating the seed particle for the full duration,
    but measures net displacement only between *window_start* and *window_end*
    (default: steps 500 → 1000).

        1. **Late-window net displacement** — Euclidean distance between the
           centre-of-mass at t=window_start and t=window_end.  This ignores
           any initial settling phase, defeating the transient drift exploit
           from iter_213.
        2. **Bounding-box penalty** — divides by ``1 + final_bb_area`` so that
           rules producing large, diffuse patterns (puffers) are suppressed.
        3. **Bit conservation** — if the initial or final bit count does not
           match the seed's bit count (3 for the L-tromino), fitness is
           forced to 0.0.  This rejects annihilating/explosive rules.

    Score formula::

        fitness = late_window_displacement / (1 + final_bb_area)

    If the initial or final bit count does not equal ``expected_bits``
    (3 for the L-tromino seed), fitness is returned as ``0.0``.

    Parameters
    ----------
    grid_size : int
        Side length of the square toroidal grid (default 128).
    simulation_steps : int
        Total simulation steps (default 1001).
    window_start : int
        Simulation step at which the displacement window begins (default 500).
    window_end : int
        Simulation step at which the displacement window ends (default 1000).
    particle : list of (int, int)
        Seed particle as (dr, dc) offsets from grid centre.
        Defaults to the 3-bit L-tromino.
    expected_bits : int
        Number of bits the seed must have for conservation to pass.
        Defaults to 3 (L-tromino).
    """

    name = "LateWindowDisplacementFitness"

    def __init__(
        self,
        grid_size:        int              = 128,
        simulation_steps: int              = 1001,
        window_start:     int              = 500,
        window_end:       int              = 1000,
        particle:         list | None      = None,
        expected_bits:    int              = 3,
    ) -> None:
        self.grid_size         = int(grid_size)
        self.simulation_steps  = int(simulation_steps)
        self.window_start      = int(window_start)
        self.window_end        = int(window_end)
        self.particle          = particle if particle is not None else LTROMINO
        self.expected_bits     = int(expected_bits)

        # Sanity-check: window must be a proper sub-window of the simulation.
        if self.window_start < 0 or self.window_end > self.simulation_steps:
            raise ValueError(
                f"LateWindowDisplacementFitness: window [{self.window_start}, "
                f"{self.window_end}] must be within [0, {self.simulation_steps}]."
            )

    # ------------------------------------------------------------------

    def evaluate(self, rule_dict: dict) -> dict[str, Any]:
        """Evaluate *rule_dict* and return a metrics dict.

        Returns
        -------
        dict
            Always contains ``"fitness"`` (float ≥ 0).
            Additional keys vary by outcome:
            - ``"reason"``                  : "ok" | "bit_conservation_failed"
            - ``"initial_bits"``            : seed bit count
            - ``"final_bits"``              : bit count at t=max_steps
            - ``"window_start_com"``        : [row, col] of CoM at t=window_start
            - ``"window_end_com"``          : [row, col] of CoM at t=window_end
            - ``"late_window_displacement"``: Euclidean distance in the late window
            - ``"final_bb_area"``           : bounding-box area at t=max_steps
        """
        lut    = rule_dict_to_lut(rule_dict)
        grid   = _make_particle_grid(self.particle, self.grid_size)

        initial_bits = int(grid.sum())

        # Single-pass simulation capturing COM at the two window boundaries
        # and at the final step.
        window_start_com = None
        window_end_com   = None

        for step in range(self.simulation_steps):
            if step == self.window_start:
                window_start_com = center_of_mass(grid)
            if step == self.window_end:
                window_end_com = center_of_mass(grid)
            grid = step_grid(grid, lut)

        # After the loop, grid is at t=max_steps (one step beyond the last
        # iteration).
        final_com      = center_of_mass(grid)
        final_bits     = int(grid.sum())

        # ── Bit-conservation gate ────────────────────────────────────────
        if initial_bits != self.expected_bits or final_bits != self.expected_bits:
            return {
                "fitness":          0.0,
                "reason":           "bit_conservation_failed",
                "initial_bits":     initial_bits,
                "final_bits":       final_bits,
                "expected_bits":    self.expected_bits,
            }

        # ── Late-window displacement ─────────────────────────────────────
        dx = window_end_com[0] - window_start_com[0]
        dy = window_end_com[1] - window_start_com[1]
        late_window_displacement = math.sqrt(dx * dx + dy * dy)

        # ── Bounding-box area ────────────────────────────────────────────
        final_bb_area = _bounding_box_area(grid)

        # ── Fitness score ────────────────────────────────────────────────
        fitness = late_window_displacement / (1.0 + float(final_bb_area))

        return {
            "fitness":                    float(fitness),
            "reason":                     "ok",
            "window_start_com":           list(window_start_com),
            "window_end_com":             list(window_end_com),
            "late_window_displacement":   float(late_window_displacement),
            "final_bb_area":              final_bb_area,
            "initial_bits":               initial_bits,
            "final_bits":                 final_bits,
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
            "LateWindowDisplacementFitness.__call__ must return a 2-tuple "
            "(fitness: float, metrics: dict)."
        )
        return result


# ---------------------------------------------------------------------------
# Module-level convenience wrapper
# ---------------------------------------------------------------------------

def evaluate(rule_dict: dict) -> dict[str, Any]:
    """Evaluate *rule_dict* with the default LateWindowDisplacementFitness settings."""
    return LateWindowDisplacementFitness().evaluate(rule_dict)
