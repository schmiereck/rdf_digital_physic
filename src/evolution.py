#!/usr/bin/env python3
"""
evolution.py  —  C2-symmetric rule evolution for the L-tromino nursery

Fitness = displacement * (final_bit_count / (initial_bit_count + EPS))

This penalises annihilation: a rule that destroys the seed gets a ratio near
zero even if the centre-of-mass technically moves before the grid goes dark.
Rules that move the particle while preserving its bit count score highest.
"""

import math
import random

import numpy as np

# Small constant to guard against the (very unlikely) zero-initial-bits edge case
EPS = 1e-6

# L-tromino seed used in iter_170 and iter_171
LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]
INITIAL_BITS   = len(LTROMINO_CELLS)   # 3

GRID_SIZE = 128
STEPS     = 200


# ── C2-symmetric rule generation ──────────────────────────────────────────────

def _rotate60(state: int) -> int:
    """Rotate hex neighbourhood 60° CW. MSB encoding: bit6=center, bit5=E … bit0=NE."""
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c * 64 + b6 * 32 + b1 * 16 + b2 * 8 + b3 * 4 + b4 * 2 + b5


def _rotate_c2(state: int) -> int:
    return _rotate60(_rotate60(_rotate60(state)))


def _try_build_c2_rule(pairs: list) -> dict | None:
    rule: dict = {}
    for a, b in pairs:
        rot_a, rot_b = _rotate_c2(a), _rotate_c2(b)
        for src, dst in [(a, b), (b, a), (rot_a, rot_b), (rot_b, rot_a)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule


def generate_random_c2_rule(rng: random.Random, max_attempts: int = 10_000) -> dict:
    for _ in range(max_attempts):
        k     = rng.randint(2, 4)
        pairs = []
        for _ in range(k):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            while b == a:
                b = rng.randint(1, 127)
            pairs.append((a, b))
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError("Failed to generate a valid C2 rule after many attempts")


# ── Simulation ─────────────────────────────────────────────────────────────────

def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)
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


def center_of_mass(grid: np.ndarray) -> tuple[float, float]:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def make_ltromino_grid(grid_size: int = GRID_SIZE, cells: list = LTROMINO_CELLS) -> np.ndarray:
    grid = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for r, c in cells:
        grid[r, c] = 1
    return grid


# ── Fitness ────────────────────────────────────────────────────────────────────

def evaluate_rule(rule_dict: dict, steps: int = STEPS) -> dict:
    """
    Simulate ``rule_dict`` for ``steps`` steps on the L-tromino seed and
    return a metrics dict including the new fitness score.

    fitness = displacement * (final_bit_count / (initial_bit_count + EPS))
    """
    lut          = rule_dict_to_lut(rule_dict)
    grid         = make_ltromino_grid()
    initial_com  = center_of_mass(grid)
    initial_bits = int(grid.sum())

    for _ in range(steps):
        grid = step_grid(grid, lut)

    final_com       = center_of_mass(grid)
    final_bit_count = int(grid.sum())
    dx              = final_com[0] - initial_com[0]
    dy              = final_com[1] - initial_com[1]
    displacement    = math.sqrt(dx * dx + dy * dy)
    fitness         = displacement * (final_bit_count / (initial_bits + EPS))

    return {
        "fitness":         fitness,
        "displacement":    displacement,
        "final_bit_count": final_bit_count,
        "initial_bit_count": initial_bits,
        "initial_com":     list(initial_com),
        "final_com":       list(final_com),
    }
