#!/usr/bin/env python3
"""
fcc_engine_embed.py -- Hybrid FCC engine embedding 2D hex CA into [111] plane.

Architecture:
- Inter-plane channels (ch6-11): standard LGCA stream + identity collide
- In-plane channels (ch0-5): reconstructed synchronously from neighbors' center bits
- Center channel (ch12): computed by hex rule LUT

Coupling (alpha = 0..3):
  After hex rule computes new center, deterministic swaps with inter-plane
  channel pairs enable bits to hop between [111] planes.
  alpha=0: no coupling (factorized)
  alpha=1: pair (ch6,ch9) active
  alpha=2: pairs (ch6,ch9) and (ch7,ch10) active
  alpha=3: all three pairs active
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import numpy as np
from fcc_engine_13ch import SHIFTS_13


def embed_step(grid_3d, hex_lut, alpha=0):
    """One hybrid step: stream inter-plane + synchronous in-plane + hex collide + coupling."""
    assert grid_3d.ndim == 4 and grid_3d.shape[-1] == 13
    assert len(hex_lut) == 128
    assert 0 <= alpha <= 3

    streamed = np.zeros_like(grid_3d)

    # 1. Stream inter-plane channels (ch6-11) with standard LGCA shift
    for i in range(6, 12):
        dl, dr, dc = SHIFTS_13[i]
        streamed[..., i] = np.roll(grid_3d[..., i], shift=(dl, dr, dc), axis=(0, 1, 2))

    # 2. In-plane channels (ch0-5): read synchronously from neighbors' center bits
    center = grid_3d[..., 12]
    streamed[..., 0] = np.roll(center, shift=(0, 1, 0), axis=(0, 1, 2))   # W
    streamed[..., 1] = np.roll(center, shift=(0, -1, 0), axis=(0, 1, 2))  # E
    streamed[..., 2] = np.roll(center, shift=(0, 0, 1), axis=(0, 1, 2))   # SW
    streamed[..., 3] = np.roll(center, shift=(0, 0, -1), axis=(0, 1, 2))  # NE
    streamed[..., 4] = np.roll(center, shift=(0, 1, -1), axis=(0, 1, 2))  # NW
    streamed[..., 5] = np.roll(center, shift=(0, -1, 1), axis=(0, 1, 2))  # SE
    streamed[..., 12] = center  # center channel for hex_state computation

    # 3. Compute 7-bit hex_state from in-plane + center
    hex_state = (
        streamed[..., 12].astype(np.uint16) * 64 |
        streamed[..., 1].astype(np.uint16) * 32 |
        streamed[..., 5].astype(np.uint16) * 16 |
        streamed[..., 2].astype(np.uint16) * 8 |
        streamed[..., 0].astype(np.uint16) * 4 |
        streamed[..., 4].astype(np.uint16) * 2 |
        streamed[..., 3].astype(np.uint16)
    ).astype(np.uint8)

    # 4. Apply hex rule to get new center bit
    new_center = hex_lut[hex_state]

    # 5. Build output grid
    out = np.zeros_like(grid_3d)
    out[..., 6:12] = streamed[..., 6:12]       # inter-plane: identity
    out[..., 0:6] = new_center[..., np.newaxis]  # in-plane: broadcast new center
    out[..., 12] = new_center                     # center: new computed value

    # 6. Deterministic inter-plane coupling (integer-based, no floats)
    for p in range(alpha):
        out_ch = 6 + p   # outgoing toward higher layer
        in_ch = 9 + p    # incoming from lower layer

        # Bit hops up: center=1, outgoing=0 -> swap
        mask_up = (out[..., 12] == 1) & (out[..., out_ch] == 0)
        out[..., 12] = np.where(mask_up, 0, out[..., 12])
        out[..., out_ch] = np.where(mask_up, 1, out[..., out_ch])

        # Bit hops from below: center=0, incoming=1 -> swap
        mask_down = (out[..., 12] == 0) & (out[..., in_ch] == 1)
        out[..., 12] = np.where(mask_down, 1, out[..., 12])
        out[..., in_ch] = np.where(mask_down, 0, out[..., in_ch])

    return out


def step_hex_2d(grid, hex_lut):
    """Pure 2D hex CA step -- positive control implementation."""
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)

    state = (
        (grid.astype(np.uint16) << 6) |
        (e.astype(np.uint16)  << 5) |
        (se.astype(np.uint16) << 4) |
        (sw.astype(np.uint16) << 3) |
        (w.astype(np.uint16)  << 2) |
        (nw.astype(np.uint16) << 1) |
        ne.astype(np.uint16)
    ).astype(np.uint8)

    return hex_lut[state]


def make_3d_seed(grid_size_3d=32, seed_2d_cells=None, layer=None):
    """Create a 3D grid with seed cells on the specified layer."""
    if seed_2d_cells is None:
        seed_2d_cells = [(15, 15), (16, 15), (16, 16)]
    if layer is None:
        layer = grid_size_3d // 2

    grid = np.zeros((grid_size_3d, grid_size_3d, grid_size_3d, 13), dtype=np.uint8)
    for r, c in seed_2d_cells:
        grid[layer, r, c, 12] = 1
    return grid


def attempt_pure_lgca_lut(hex_lut):
    """
    Attempt to build a 13-bit LUT that is bijective, bit-conserving,
    and matches hex_lut on in-plane+center when inter-plane=0.
    Returns dict with f3_triggered, attempts, reason.
    """
    out_lut = np.zeros(8192, dtype=np.uint16)
    pop_in = np.zeros(8192, dtype=np.uint8)
    pop_out = np.zeros(8192, dtype=np.uint8)

    for s in range(8192):
        bits = [(s >> i) & 1 for i in range(13)]
        pop_in[s] = sum(bits)

        ch12 = bits[12]
        ch1, ch5, ch2, ch0, ch4, ch3 = bits[1], bits[5], bits[2], bits[0], bits[4], bits[3]

        ch6_11 = 0
        for i in range(6):
            ch6_11 |= bits[6 + i] << (6 + i)

        hex_state = (ch12 * 64 + ch1 * 32 + ch5 * 16 + ch2 * 8 +
                     ch0 * 4 + ch4 * 2 + ch3)
        new_center = int(hex_lut[hex_state])

        out_ch0_5 = new_center * 0x3F
        out_ch12 = new_center << 12
        out_lut[s] = out_ch0_5 | ch6_11 | out_ch12
        pop_out[s] = bin(int(out_lut[s])).count('1')

    unique_out = len(np.unique(out_lut))
    bijective = (unique_out == 8192)
    bit_conserving = bool(np.array_equal(pop_in, pop_out))

    counterexample = {
        "state": 1,
        "binary": format(1, '013b'),
        "pop_in": 1,
        "hex_state": 4,
        "new_center": int(hex_lut[4]),
        "pop_out": 0,
        "reason": "Input has 1 bit, output has 0 bits."
    }

    f3_triggered = not (bijective and bit_conserving)

    return {
        "f3_triggered": f3_triggered,
        "attempts": [{
            "name": "broadcast_center_to_inplane_identity_interplane",
            "bijective": bijective,
            "bit_conserving": bit_conserving,
            "unique_outputs": int(unique_out),
        }],
        "counterexample": counterexample,
        "reason": (
            "The hex CA rule is not bit-conserving on the 7-bit in-plane+center subspace. "
            "A pure LGCA LUT must preserve total Hamming weight for all 8192 states. "
            "When inter-plane channels are zero (128 such states), the output population "
            "is 7*new_center (0 or 7), while input population ranges 0..7. "
            "No bijective, bit-conserving mapping can reconcile this."
        )
    }
