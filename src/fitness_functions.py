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

SubLightFitness
---------------
Designed (iter_216.4) to defeat the ``v=1c`` glider exploit identified in
iter_215/216:  ``LateWindowDisplacementFitness`` rewards displacement
proportionally to speed and so converges to the lattice speed of light.
``SubLightFitness`` introduces a hard velocity gate, an internal-period gate,
and a period-bonus factor so that sub-light periodic gliders out-score the
trivial period-1 v=1c glider.

    fitness = displacement * (1 - 1 / period)

See the ``SubLightFitness`` class docstring for the full design rationale.

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


def _toroidal_center_of_mass(grid: np.ndarray, grid_size: int) -> tuple[float, float]:
    """Wrap-aware centre of mass via the circular-mean formula.

    The naive arithmetic mean (used by ``evolution.center_of_mass``) is
    discontinuous when a multi-cell particle crosses a toroidal boundary —
    a single wrapped cell can jolt the CoM by ~grid_size/n_cells.  The
    circular mean maps each integer coordinate to an angle on the unit
    circle, averages the unit vectors, and converts back, giving a
    continuous CoM for any cluster smaller than half the grid.
    """
    rs, cs = np.where(grid > 0)
    if len(rs) == 0:
        return (0.0, 0.0)
    two_pi_over_n = 2.0 * math.pi / grid_size
    theta_r = rs * two_pi_over_n
    theta_c = cs * two_pi_over_n
    mean_r = math.atan2(
        float(np.mean(np.sin(theta_r))), float(np.mean(np.cos(theta_r)))
    )
    mean_c = math.atan2(
        float(np.mean(np.sin(theta_c))), float(np.mean(np.cos(theta_c)))
    )
    if mean_r < 0.0:
        mean_r += 2.0 * math.pi
    if mean_c < 0.0:
        mean_c += 2.0 * math.pi
    return (mean_r / two_pi_over_n, mean_c / two_pi_over_n)


def _normalize_config(grid: np.ndarray, grid_size: int) -> frozenset:
    """Translation-invariant fingerprint of the live-cell pattern.

    Cell offsets are computed relative to the rounded toroidal CoM and
    wrapped to the minimum periodic image.  Two grids whose live-cell
    pattern differs only by a (toroidal) translation produce the same
    frozenset — which is exactly what period detection needs.
    """
    rs, cs = np.where(grid > 0)
    if len(rs) == 0:
        return frozenset()
    com_r, com_c = _toroidal_center_of_mass(grid, grid_size)
    cr = int(round(com_r)) % grid_size
    cc = int(round(com_c)) % grid_size
    half = grid_size / 2.0
    offsets: list[tuple[int, int]] = []
    for r, c in zip(rs, cs):
        dr = int(r) - cr
        dc = int(c) - cc
        if dr > half:
            dr -= grid_size
        elif dr < -half:
            dr += grid_size
        if dc > half:
            dc -= grid_size
        elif dc < -half:
            dc += grid_size
        offsets.append((dr, dc))
    return frozenset(offsets)


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


class SubLightFitness:
    """Fitness function that selects for *sub-light-speed* (v<c) periodic gliders.

    Background
    ----------
    ``LateWindowDisplacementFitness`` rewards late-window displacement
    proportionally to the particle's speed::

        fitness = displacement / (1 + bb_area)   ≈   (speed × window) / (1 + bb_area)

    Because there is no upper ceiling on speed, the fittest particle is the
    fastest one — the lattice-speed-of-light glider (one cell per step,
    internal period 1).  No sub-light glider can compete on displacement
    alone, so evolution converges to v=1c (see ``archive/iter_216/results/
    fitness_analysis.md``).

    ``SubLightFitness`` defeats that exploit with three additions:

      1. **Unwrapped centre-of-mass tracking** — the per-step CoM is
         computed with a wrap-aware circular mean and then integrated
         cumulatively with a minimum-image delta correction, so the
         displacement measurement is correct even when the particle
         traverses the toroidal boundary multiple times.

      2. **Hard velocity gate** — any particle whose mean speed reaches
         ``v_threshold`` cells/step (default 0.9) is rejected with
         ``fitness = 0``.  A v=1c glider has speed exactly 1.0 and is
         therefore unwinnable.

      3. **Internal-period gate and bonus** — the smallest period ``T`` at
         which the translation-normalised cell configuration repeats is
         detected; ``T <= 1`` is rejected outright (a v=1c glider trivially
         has T=1), and the surviving fitness is multiplied by the period
         factor ``(1 - 1/T)`` so that slower, more structurally complex
         gliders are rewarded for their internal oscillation.

    Formula
    -------
    ::

        if not bit_conserved:           fitness = 0
        if displacement == 0:           fitness = 0
        if avg_velocity >= v_threshold: fitness = 0   # hard reject v≈1c
        if period <= 1:                 fitness = 0   # hard reject trivial period
        else:
            fitness = displacement * (1 - 1 / period)

    Examples of the period factor:

    ===========  ======  ============  ==================
    Particle     period  ``1 - 1/T``   fitness scale
    ===========  ======  ============  ==================
    v=1c glider   1       0.0           **0** (rejected)
    v=0.5c        2       0.5           0.5 × displacement
    v=0.25c       4       0.75          0.75 × displacement
    v=1/8 c       8       0.875         0.875 × displacement
    ===========  ======  ============  ==================

    Why it avoids v=1c gliders
    --------------------------
    A v=1c glider has period 1 by construction: it merely translates by one
    cell per step with no change in shape, so the period gate alone is
    sufficient to drive its fitness to zero.  As a defence-in-depth, the
    velocity gate (default 0.9) also rejects it: its measured speed is
    exactly 1.0 cells/step, comfortably above the threshold.  Sub-light
    gliders, conversely, must cycle through more than one internal
    configuration per cell of net displacement and therefore have period
    > 1, so they survive both gates and earn fitness proportional to their
    displacement times the period bonus.

    Parameters
    ----------
    grid_size : int
        Side length of the square toroidal grid (default 128).
    simulation_steps : int
        Total simulation steps (default 1200) — long enough to settle and
        still leave room for displacement and period windows.
    window_start, window_end : int
        Step indices delimiting the late displacement window
        (default 600 → 1000).  Unwrapped-CoM displacement is measured
        between these two snapshots.
    period_window_start, period_window_end : int
        Step indices delimiting the period-detection window
        (default 600 → 800).
    max_period : int
        Largest period the detector will check (default 64).  Periods
        beyond this are treated as 'no period found' (chaotic) and fitness
        becomes 0.
    v_threshold : float
        Hard upper bound on mean velocity (cells/step, default 0.9).
        Particles meeting or exceeding this are rejected.
    particle : list of (int, int)
        Seed particle as (dr, dc) offsets from grid centre
        (default: 3-bit L-tromino).
    expected_bits : int
        Bit count required for both the initial and final grid for the
        bit-conservation gate (default 3 for the L-tromino).
    """

    name = "SubLightFitness"

    def __init__(
        self,
        grid_size:           int          = 128,
        simulation_steps:    int          = 1200,
        window_start:        int          = 600,
        window_end:          int          = 1000,
        period_window_start: int          = 600,
        period_window_end:   int          = 800,
        max_period:          int          = 64,
        v_threshold:         float        = 0.9,
        particle:            list | None  = None,
        expected_bits:       int          = 3,
    ) -> None:
        self.grid_size           = int(grid_size)
        self.simulation_steps    = int(simulation_steps)
        self.window_start        = int(window_start)
        self.window_end          = int(window_end)
        self.period_window_start = int(period_window_start)
        self.period_window_end   = int(period_window_end)
        self.max_period          = int(max_period)
        self.v_threshold         = float(v_threshold)
        self.particle            = particle if particle is not None else LTROMINO
        self.expected_bits       = int(expected_bits)

        if self.window_start < 0 or self.window_end > self.simulation_steps:
            raise ValueError(
                f"SubLightFitness: displacement window [{self.window_start}, "
                f"{self.window_end}] must lie within [0, {self.simulation_steps}]."
            )
        if self.window_end <= self.window_start:
            raise ValueError(
                f"SubLightFitness: window_end ({self.window_end}) must be > "
                f"window_start ({self.window_start})."
            )
        if self.period_window_start < 0 or self.period_window_end > self.simulation_steps:
            raise ValueError(
                f"SubLightFitness: period window [{self.period_window_start}, "
                f"{self.period_window_end}] must lie within [0, {self.simulation_steps}]."
            )
        if self.period_window_end - self.period_window_start <= self.max_period:
            raise ValueError(
                f"SubLightFitness: period window length "
                f"({self.period_window_end - self.period_window_start}) must "
                f"exceed max_period ({self.max_period})."
            )

    # ------------------------------------------------------------------

    @staticmethod
    def _detect_period(
        configs: list[frozenset],
        max_period: int,
    ) -> int:
        """Smallest ``k`` in [1, max_period] with ``configs[i] == configs[i+k]``
        for every valid ``i``.  Returns 0 if no such period exists within the
        cap (treated as 'chaotic' by the caller).
        """
        n = len(configs)
        if n < 2:
            return 0
        upper = min(max_period, n - 1)
        for k in range(1, upper + 1):
            if all(configs[i] == configs[i + k] for i in range(n - k)):
                return k
        return 0

    # ------------------------------------------------------------------

    def evaluate(self, rule_dict: dict) -> dict[str, Any]:
        """Evaluate *rule_dict* and return a metrics dict.

        Returns
        -------
        dict
            Always contains ``"fitness"`` (float ≥ 0) and ``"reason"`` —
            one of ``"ok"``, ``"bit_conservation_failed"``,
            ``"no_displacement"``, ``"velocity_at_or_above_threshold"``,
            or ``"period_too_short"``.
            On ``"ok"`` the dict additionally contains ``"displacement"``,
            ``"avg_velocity"``, ``"period"``, ``"period_bonus"``, and
            ``"final_bb_area"``.
        """
        lut  = rule_dict_to_lut(rule_dict)
        grid = _make_particle_grid(self.particle, self.grid_size)

        initial_bits = int(grid.sum())

        # ── Unwrapped CoM tracking ───────────────────────────────────────
        prev_raw      = np.array(_toroidal_center_of_mass(grid, self.grid_size))
        unwrapped_com = prev_raw.copy()
        com_history: list[np.ndarray] = [unwrapped_com.copy()]

        # Period-detection snapshots (configs, not grids — saves memory)
        period_configs: list[frozenset] = []
        if self.period_window_start <= 0 < self.period_window_end:
            period_configs.append(_normalize_config(grid, self.grid_size))

        for step in range(1, self.simulation_steps + 1):
            grid = step_grid(grid, lut)
            raw = np.array(_toroidal_center_of_mass(grid, self.grid_size))
            delta = raw - prev_raw
            # Minimum-image wrap correction: any single-step shift larger
            # than half the grid is a wrap, not real motion.
            delta -= np.round(delta / self.grid_size) * self.grid_size
            unwrapped_com = unwrapped_com + delta
            com_history.append(unwrapped_com.copy())
            prev_raw = raw

            if self.period_window_start <= step < self.period_window_end:
                period_configs.append(_normalize_config(grid, self.grid_size))

        final_bits = int(grid.sum())

        # ── Bit-conservation gate ────────────────────────────────────────
        if initial_bits != self.expected_bits or final_bits != self.expected_bits:
            return {
                "fitness":       0.0,
                "reason":        "bit_conservation_failed",
                "initial_bits":  initial_bits,
                "final_bits":    final_bits,
                "expected_bits": self.expected_bits,
            }

        # ── Late-window displacement ─────────────────────────────────────
        com_a = com_history[self.window_start]
        com_b = com_history[self.window_end]
        dx = float(com_b[0] - com_a[0])
        dy = float(com_b[1] - com_a[1])
        displacement = math.sqrt(dx * dx + dy * dy)
        window_steps = self.window_end - self.window_start
        avg_velocity = displacement / window_steps

        if displacement == 0.0:
            return {
                "fitness":       0.0,
                "reason":        "no_displacement",
                "displacement":  0.0,
                "avg_velocity":  0.0,
                "initial_bits":  initial_bits,
                "final_bits":    final_bits,
            }

        if avg_velocity >= self.v_threshold:
            return {
                "fitness":       0.0,
                "reason":        "velocity_at_or_above_threshold",
                "displacement":  float(displacement),
                "avg_velocity":  float(avg_velocity),
                "v_threshold":   self.v_threshold,
                "initial_bits":  initial_bits,
                "final_bits":    final_bits,
            }

        # ── Period detection ─────────────────────────────────────────────
        period = self._detect_period(period_configs, self.max_period)
        if period <= 1:
            return {
                "fitness":       0.0,
                "reason":        "period_too_short",
                "displacement":  float(displacement),
                "avg_velocity":  float(avg_velocity),
                "period":        int(period),
                "initial_bits":  initial_bits,
                "final_bits":    final_bits,
            }

        # ── Fitness ──────────────────────────────────────────────────────
        period_bonus  = 1.0 - 1.0 / period
        fitness       = displacement * period_bonus
        final_bb_area = _bounding_box_area(grid)

        return {
            "fitness":       float(fitness),
            "reason":        "ok",
            "displacement":  float(displacement),
            "avg_velocity":  float(avg_velocity),
            "period":        int(period),
            "period_bonus":  float(period_bonus),
            "final_bb_area": int(final_bb_area),
            "initial_bits":  initial_bits,
            "final_bits":    final_bits,
        }

    def __call__(self, rule_dict: dict) -> tuple[float, dict[str, Any]]:
        """Convenience callable returning ``(fitness, metrics_dict)``.

        Mirrors ``NetDisplacementFitness.__call__`` so this class is a
        drop-in replacement for evolutionary loops that unpack
        ``fitness, metrics = fitness_fn(rule)``.
        """
        m = self.evaluate(rule_dict)
        result: tuple[float, dict[str, Any]] = (float(m["fitness"]), m)
        assert isinstance(result, tuple) and len(result) == 2, (
            "SubLightFitness.__call__ must return a 2-tuple "
            "(fitness: float, metrics: dict)."
        )
        return result


# ---------------------------------------------------------------------------
# Module-level convenience wrapper
# ---------------------------------------------------------------------------

def evaluate(rule_dict: dict) -> dict[str, Any]:
    """Evaluate *rule_dict* with the default NetDisplacementFitness settings."""
    return NetDisplacementFitness().evaluate(rule_dict)
