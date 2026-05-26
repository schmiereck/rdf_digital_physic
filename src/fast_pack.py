#!/usr/bin/env python3
"""
fast_pack.py — Vectorized pack/unpack using lookup tables instead of loops.

Precomputes bit-extraction tables so that pack/unpack are pure numpy advanced-indexing
operations with no Python loops. Also stores LUT in uint16 for fast indexing.
"""
import numpy as np

# ============================================================================
# 12-channel pack/unpack
# ============================================================================

# Precompute extraction: for each possible uint16 value and bit position,
# what is the bit value? This is just ((val >> i) & 1) precomputed.
# Actually, for speed we precompute a table: extract[i, val] = ((val >> i) & 1)
# extract shape: (12, 65536) - 768KB

_EXTRACT_12 = None

def _get_extract_12():
    global _EXTRACT_12
    if _EXTRACT_12 is None:
        vals = np.arange(65536, dtype=np.uint16)
        _EXTRACT_12 = ((vals[:, np.newaxis] >> np.arange(12)) & 1).astype(np.uint8)
        # Transpose so indexing is _EXTRACT[:, packed] -> (12, H, W, L)
        _EXTRACT_12 = _EXTRACT_12.T  # shape (12, 65536)
    return _EXTRACT_12


def fast_pack_12(grid: np.ndarray) -> np.ndarray:
    """Pack (L,H,W,12) uint8 grid -> (L,H,W) uint16. Vectorized."""
    shifts = np.arange(12, dtype=np.uint16)
    # grid sum: each channel contributes channel_value * 2^k
    result = np.zeros(grid.shape[:-1], dtype=np.uint16)
    for i in range(12):
        result |= (grid[..., i] << i)
    return result


def fast_pack_12_v2(grid: np.ndarray) -> np.ndarray:
    """Pack (L,H,W,12) uint8 grid -> (L,H,W) uint16.
    Uses dot product on the last axis."""
    packed = np.zeros(grid.shape[:-1], dtype=np.uint16)
    for i in range(12):
        packed += grid[..., i] << i
    return packed.astype(np.uint16)


def fast_unpack_12(packed: np.ndarray) -> np.ndarray:
    """Unpack (L,H,W) uint16 -> (L,H,W,12) uint8 using lookup table."""
    extract = _get_extract_12()
    # packed is (L,H,W), extract is (12, 65536)
    result = extract[:, packed.ravel()].reshape(12, *packed.shape).transpose(1, 2, 3, 0)
    return result

# ============================================================================
# 13-channel pack/unpack
# ============================================================================

def fast_pack_13(grid: np.ndarray) -> np.ndarray:
    """Pack (L,H,W,13) uint8 grid -> (L,H,W) uint16."""
    result = np.zeros(grid.shape[:-1], dtype=np.uint16)
    for i in range(13):
        result |= (grid[..., i] << i)
    return result


def fast_unpack_13(packed: np.ndarray) -> np.ndarray:
    """Unpack (L,H,W) uint16 -> (L,H,W,13) uint8 using lookup table."""
    extract = _get_extract_12()  # reuse 12-channel table for bits 0-11
    grid = np.zeros(packed.shape + (13,), dtype=np.uint8)
    grid[..., :12] = extract[:, packed.ravel()].reshape(12, *packed.shape).transpose(1, 2, 3, 0)
    grid[..., 12] = ((packed >> 12) & 1).astype(np.uint8)
    return grid
