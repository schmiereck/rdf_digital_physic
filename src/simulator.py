#!/usr/bin/env python3
"""
simulator.py — Particle and Simulator classes for the hexagonal CA.

Uses the same toroidal 128×128 hex-neighbour step_grid logic as evolution.py
but exposes it through OO wrappers suitable for fitness evaluation.
"""

import numpy as np

GRID_SIZE = 128


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


class Particle:
    """Holds the grid state of a simulated CA particle."""

    def __init__(self, grid: np.ndarray):
        self.grid = grid

    @property
    def bit_count(self) -> int:
        return int(self.grid.sum())

    def center_of_mass(self) -> tuple:
        return _center_of_mass(self.grid)


class Simulator:
    """Advances a Particle forward one step at a time using a Rule's LUT."""

    def __init__(self, rule, grid_size: int = GRID_SIZE):
        self.lut = _rule_to_lut(rule.rule_dict)
        self.grid_size = grid_size

    def step(self, particle: Particle) -> None:
        particle.grid = _step_grid(particle.grid, self.lut)
