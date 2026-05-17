#!/usr/bin/env python3
"""
simulator.py — Particle and Simulator classes for the hexagonal CA.

The legacy 1-bit pipeline (128-entry LUT, 2D grids) is preserved as the
default fast path so existing callers keep working unchanged.  Passing
``bits_per_cell > 1`` enables the multi-bit engine in ``engine.py``, where
grids carry shape ``(H, W, bits_per_cell)``.
"""

from __future__ import annotations

import numpy as np

from engine import (
    BITS_PER_CELL,
    HexagonalGrid,
    build_lut,
    occupancy_mask,
    step_grid as engine_step_grid,
)

GRID_SIZE = 128


# ── Legacy 1-bit helpers (kept verbatim for backward compat) ────────────────

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
    if grid.ndim == 3:
        mask = grid.sum(axis=-1) > 0
    else:
        mask = grid > 0
    xs, ys = np.where(mask)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


# ── OO wrappers ─────────────────────────────────────────────────────────────

class Particle:
    """Holds the grid state of a simulated CA particle.

    For ``bits_per_cell == 1`` (default), ``self.grid`` is the legacy 2D array
    (``shape == (H, W)``).  For ``bits_per_cell > 1`` it is a 3D array of shape
    ``(H, W, bits_per_cell)`` as produced by ``engine.step_grid``.
    """

    def __init__(self, grid: np.ndarray, bits_per_cell: int | None = None):
        if bits_per_cell is None:
            bits_per_cell = BITS_PER_CELL
        self.bits_per_cell = int(bits_per_cell)
        if self.bits_per_cell == 1:
            # Accept either a 2D legacy grid or a (H, W, 1) 3D bit-grid.
            if grid.ndim == 3:
                assert grid.shape[-1] == 1
                self.grid = grid[:, :, 0].astype(np.uint8)
            else:
                self.grid = grid.astype(np.uint8)
        else:
            # Multi-bit mode requires the 3D bit-grid.
            if grid.ndim == 2:
                # Treat 2D as occupancy mask: cell value = 1 (LSB).
                hg = HexagonalGrid.from_2d(grid, bits_per_cell=self.bits_per_cell)
                self.grid = hg.data
            else:
                assert grid.shape[-1] == self.bits_per_cell, (
                    f"grid bit dim {grid.shape[-1]} != bits_per_cell {self.bits_per_cell}"
                )
                self.grid = grid.astype(np.uint8)

    @property
    def bit_count(self) -> int:
        return int(self.grid.sum())

    def center_of_mass(self) -> tuple:
        return _center_of_mass(self.grid)


class Simulator:
    """Advances a Particle forward one step at a time using a Rule's LUT."""

    def __init__(
        self,
        rule,
        grid_size: int = GRID_SIZE,
        bits_per_cell: int | None = None,
    ):
        if bits_per_cell is None:
            # Inherit from the rule when available, else module default.
            bits_per_cell = getattr(rule, "bits_per_cell", BITS_PER_CELL)
        self.bits_per_cell = int(bits_per_cell)
        self.grid_size = grid_size
        # Prefer a Rule-supplied LUT when present (multi-bit-aware).
        rule_lut = getattr(rule, "lut", None)
        if rule_lut is not None:
            self.lut = rule_lut
        elif self.bits_per_cell == 1:
            self.lut = _rule_to_lut(rule.rule_dict)
        else:
            self.lut = build_lut(rule.rule_dict, self.bits_per_cell)

    def step(self, particle: Particle) -> None:
        if self.bits_per_cell == 1 and particle.grid.ndim == 2:
            # Legacy fast path
            particle.grid = _step_grid(particle.grid, self.lut)
        else:
            particle.grid = engine_step_grid(
                particle.grid, self.lut, self.bits_per_cell
            )
