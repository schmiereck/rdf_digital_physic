#!/usr/bin/env python3
"""
fcc_engine_13ch.py — 13-channel 3D FCC LGCA simulation engine.

Extends engine_3d.py with a rest-mass channel (channel 12) that does NOT shift
during propagation. Provides pack/unpack/stream/collide/invert/verify functions
for 13-bit states (uint16, max 8191).
"""

from __future__ import annotations
import numpy as np

# 12 propagation shifts from engine_3d.py + rest channel (0,0,0)
SHIFTS_13 = [
    (0, 1, 0),    # Channel 0
    (0, -1, 0),   # Channel 1
    (0, 0, 1),    # Channel 2
    (0, 0, -1),   # Channel 3
    (0, 1, -1),   # Channel 4
    (0, -1, 1),   # Channel 5
    (1, 1, 1),    # Channel 6
    (1, 1, 0),    # Channel 7
    (1, 0, 1),    # Channel 8
    (-1, -1, -1), # Channel 9
    (-1, -1, 0),  # Channel 10
    (-1, 0, -1),  # Channel 11
    (0, 0, 0),    # Channel 12: rest mass — does not move
]


def pack_13(grid: np.ndarray) -> np.ndarray:
    """Pack a 3D bit-grid of shape (L, H, W, 13) into an integer grid of shape (L, H, W) of type np.uint16."""
    assert grid.ndim == 4 and grid.shape[-1] == 13, f"Grid must have shape (L, H, W, 13), got {grid.shape}"
    packed = np.zeros(grid.shape[:-1], dtype=np.uint16)
    for i in range(13):
        packed |= (grid[..., i].astype(np.uint16) << i)
    return packed


def unpack_13(packed: np.ndarray) -> np.ndarray:
    """Unpack an integer grid of shape (L, H, W) into a 3D bit-grid of shape (L, H, W, 13) of type np.uint8."""
    out = np.zeros(packed.shape + (13,), dtype=np.uint8)
    for i in range(13):
        out[..., i] = ((packed >> i) & 1).astype(np.uint8)
    return out


def stream_13(grid: np.ndarray, reverse: bool = False) -> np.ndarray:
    """Propagates the bits along their respective directions using np.roll.

    Channel 12 (rest mass) gets shift (0,0,0) — effectively a no-op copy.
    If reverse is True, propagates in the opposite direction (inverse stream).
    """
    assert grid.ndim == 4 and grid.shape[-1] == 13, f"Grid must have shape (L, H, W, 13), got {grid.shape}"
    out = np.empty_like(grid)
    for i, (dl, dr, dc) in enumerate(SHIFTS_13):
        shift_val = (-dl, -dr, -dc) if reverse else (dl, dr, dc)
        out[..., i] = np.roll(grid[..., i], shift=shift_val, axis=(0, 1, 2))
    return out


def collide_13(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Applies a 13-bit lookup table (LUT) of size 8192 to pack the bits, apply the LUT, and unpack them."""
    assert len(lut) == 8192, f"LUT must have size 8192, got {len(lut)}"
    packed = pack_13(grid)
    collided_packed = lut[packed]
    return unpack_13(collided_packed)


def invert_lut_13(lut: np.ndarray) -> np.ndarray:
    """Invert a permutation lookup table (LUT) of size 8192."""
    assert len(lut) == 8192, f"LUT must have size 8192, got {len(lut)}"
    inv_lut = np.empty_like(lut)
    inv_lut[lut] = np.arange(8192, dtype=lut.dtype)
    return inv_lut


def verify_lut_13(lut: np.ndarray, action: np.ndarray) -> dict:
    """Verify the LUT is a bijection, bit-conserving, and O_h-symmetric.

    Parameters
    ----------
    lut : np.ndarray
        LUT of size 8192, dtype uint16.
    action : np.ndarray
        Precomputed O_h action on 13-bit states, shape (48, 8192), dtype uint16.
        Must be computed from the 13-channel O_h permutations.

    Returns
    -------
    dict with keys 'bijection', 'bit_conserving', 'symmetric', and optionally
    'first_violating_perm'.
    """
    results: dict = {}
    results['bijection'] = bool(len(np.unique(lut)) == 8192)

    pop_in = np.array([bin(s).count('1') for s in range(8192)], dtype=np.uint8)
    pop_out = np.array([bin(int(lut[s])).count('1') for s in range(8192)], dtype=np.uint8)
    results['bit_conserving'] = bool(np.array_equal(pop_in, pop_out))

    sym_ok = True
    bad = None
    n_perms = action.shape[0]
    for g in range(n_perms):
        lhs = lut[action[g]]
        rhs = action[g, lut]
        if not np.array_equal(lhs, rhs):
            sym_ok = False
            bad = g
            break
    results['symmetric'] = sym_ok
    if bad is not None:
        results['first_violating_perm'] = int(bad)
    return results
