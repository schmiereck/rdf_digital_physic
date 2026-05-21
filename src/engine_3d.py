#!/usr/bin/env python3
"""
engine_3d.py — 3D Cuboctahedron (FCC lattice) Lattice Gas Cellular Automaton (LGCA) simulation engine.

This engine implements:
1. A 3D toroidal grid of shape (L, H, W, 12) representing the 12 velocity channels of the FCC lattice.
2. The 12 directions defined in the standard projection of FCC onto a stack of hexagonal layers.
3. A `stream` function that propagates the bits along their respective directions using `np.roll`.
4. A `collide` function that applies a 12-bit lookup table (LUT) of size 4096 to pack the bits, apply the LUT, and unpack them.
5. Verification functions for Reversibility and Bit conservation.
"""

from __future__ import annotations
import numpy as np

# Precise coordinate shifts (dl, dr, dc) derived in our coordinate projection:
# Axis 0: Layer (l), Axis 1: Row (r), Axis 2: Column (c)
SHIFTS = [
    (0, 1, 0),    # Channel 0: dl=0, dr=1, dc=0
    (0, -1, 0),   # Channel 1: dl=0, dr=-1, dc=0
    (0, 0, 1),    # Channel 2: dl=0, dr=0, dc=1
    (0, 0, -1),   # Channel 3: dl=0, dr=0, dc=-1
    (0, 1, -1),   # Channel 4: dl=0, dr=1, dc=-1
    (0, -1, 1),   # Channel 5: dl=0, dr=-1, dc=1
    (1, 1, 1),    # Channel 6: dl=1, dr=1, dc=1
    (1, 1, 0),    # Channel 7: dl=1, dr=1, dc=0
    (1, 0, 1),    # Channel 8: dl=1, dr=0, dc=1
    (-1, -1, -1), # Channel 9: dl=-1, dr=-1, dc=-1
    (-1, -1, 0),  # Channel 10: dl=-1, dr=-1, dc=0
    (-1, 0, -1),  # Channel 11: dl=-1, dr=0, dc=-1
]

def pack(grid: np.ndarray) -> np.ndarray:
    """Pack a 3D bit-grid of shape (L, H, W, 12) into an integer grid of shape (L, H, W) of type np.uint16."""
    assert grid.ndim == 4 and grid.shape[-1] == 12, f"Grid must have shape (L, H, W, 12), got {grid.shape}"
    packed = np.zeros(grid.shape[:-1], dtype=np.uint16)
    for i in range(12):
        packed |= (grid[..., i].astype(np.uint16) << i)
    return packed

def unpack(packed: np.ndarray) -> np.ndarray:
    """Unpack an integer grid of shape (L, H, W) into a 3D bit-grid of shape (L, H, W, 12) of type np.uint8."""
    out = np.zeros(packed.shape + (12,), dtype=np.uint8)
    for i in range(12):
        out[..., i] = ((packed >> i) & 1).astype(np.uint8)
    return out

def stream(grid: np.ndarray, reverse: bool = False) -> np.ndarray:
    """Propagates the bits along their respective directions using np.roll.
    
    If reverse is True, propagates in the opposite direction (inverse stream).
    """
    assert grid.ndim == 4 and grid.shape[-1] == 12, f"Grid must have shape (L, H, W, 12), got {grid.shape}"
    out = np.empty_like(grid)
    for i, (dl, dr, dc) in enumerate(SHIFTS):
        shift_val = (-dl, -dr, -dc) if reverse else (dl, dr, dc)
        out[..., i] = np.roll(grid[..., i], shift=shift_val, axis=(0, 1, 2))
    return out

def collide(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    """Applies a 12-bit lookup table (LUT) of size 4096 to pack the bits, apply the LUT, and unpack them."""
    assert len(lut) == 4096, f"LUT must have size 4096, got {len(lut)}"
    packed = pack(grid)
    collided_packed = lut[packed]
    return unpack(collided_packed)

def invert_lut(lut: np.ndarray) -> np.ndarray:
    """Invert a permutation lookup table (LUT) of size 4096."""
    assert len(lut) == 4096, f"LUT must have size 4096, got {len(lut)}"
    inv_lut = np.empty_like(lut)
    inv_lut[lut] = np.arange(4096, dtype=lut.dtype)
    return inv_lut

def generate_bit_conserving_lut(seed: int | None = None) -> np.ndarray:
    """Generate a random, invertible (reversible), and bit-conserving 12-bit LUT of size 4096."""
    if seed is not None:
        np.random.seed(seed)
    
    lut = np.zeros(4096, dtype=np.uint16)
    
    # Group all indices by Hamming weight
    for w in range(13):
        indices = [x for x in range(4096) if bin(x).count('1') == w]
        indices = np.array(indices, dtype=np.uint16)
        shuffled = indices.copy()
        np.random.shuffle(shuffled)
        lut[indices] = shuffled
        
    return lut

def verify_reversibility(grid: np.ndarray, lut: np.ndarray) -> bool:
    """Verify that both the stream and collide steps can be reversed.
    
    Returns True if both steps are successfully reversed, False otherwise.
    """
    # 1. Test stream reversibility
    streamed = stream(grid, reverse=False)
    unstreamed = stream(streamed, reverse=True)
    stream_ok = np.array_equal(grid, unstreamed)
    
    # 2. Test collide reversibility
    inv_lut = invert_lut(lut)
    collided = collide(grid, lut)
    uncollided = collide(collided, inv_lut)
    collide_ok = np.array_equal(grid, uncollided)
    
    return bool(stream_ok and collide_ok)

def verify_bit_conservation(grid: np.ndarray, lut: np.ndarray) -> bool:
    """Verify that both the stream and collide steps preserve the exact total number of set bits.
    
    Assumes that the LUT itself is bit-conserving.
    Returns True if both steps conserve bits, False otherwise.
    """
    initial_bits = int(grid.sum())
    
    # Test stream bit conservation
    streamed = stream(grid)
    stream_bits = int(streamed.sum())
    stream_ok = (initial_bits == stream_bits)
    
    # Test collide bit conservation
    collided = collide(grid, lut)
    collide_bits = int(collided.sum())
    collide_ok = (initial_bits == collide_bits)
    
    return bool(stream_ok and collide_ok)
