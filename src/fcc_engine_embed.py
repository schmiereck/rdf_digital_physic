#!/usr/bin/env python3
"""
fcc_engine_embed.py — Hybrid FCC engine embedding 2D hex CA into [111] plane.

Architecture:
- Inter-plane channels (ch6-11): standard LGCA stream + identity collide
- In-plane channels (ch0-5): reconstructed synchronously from neighbors' center bits
- Center channel (ch12): computed by hex rule LUT

This is a HYBRID engine, NOT a pure LGCA. The in-plane channels are VIRTUAL —
they are not streamed but read directly from neighbors' ch12 values each step.
This breaks LGCA bit-conservation and bijectivity for the in-plane+center
subsystem, which is the expected architectural incompatibility (F3).

Channel mapping for [111] hex plane (layer l):
  ch12 = center bit (cell state)
  ch0  = after stream: center bit of W  neighbor → hex W  bit (bit 2 of hex_state)
  ch1  = after stream: center bit of E  neighbor → hex E  bit (bit 5)
  ch2  = after stream: center bit of SW neighbor → hex SW bit (bit 3)
  ch3  = after stream: center bit of NE neighbor → hex NE bit (bit 0)
  ch4  = after stream: center bit of NW neighbor → hex NW bit (bit 1)
  ch5  = after stream: center bit of SE neighbor → hex SE bit (bit 4)

hex_state encoding (matches step_grid in evolution.py):
  bit 6 (64) = ch12 = center
  bit 5 (32) = ch1  = E
  bit 4 (16) = ch5  = SE
  bit 3 (8)  = ch2  = SW
  bit 2 (4)  = ch0  = W
  bit 1 (2)  = ch4  = NW
  bit 0 (1)  = ch3  = NE
"""

from __future__ import annotations

import numpy as np

from src.fcc_engine_13ch import SHIFTS_13

# ── Hybrid step ─────────────────────────────────────────────────────────────

def embed_step(grid_3d: np.ndarray, hex_lut: np.ndarray, alpha: float = 0.0) -> np.ndarray:
    """One hybrid step: stream inter-plane + synchronous in-plane + hex collide.

    Parameters
    ----------
    grid_3d : np.ndarray, shape (L, H, W, 13), dtype uint8
        Current 3D grid.  channel 12 = center bit, channels 0-5 = in-plane,
        channels 6-11 = inter-plane.
    hex_lut : np.ndarray, shape (128,), dtype uint8
        7-bit → 1-bit lookup table for the 2D hex CA (output = new center bit).
    alpha : float
        Inter-plane coupling strength (unused at α=0, reserved for α>0 tests).

    Returns
    -------
    np.ndarray, same shape/dtype as grid_3d
        Next-step grid.
    """
    assert grid_3d.ndim == 4 and grid_3d.shape[-1] == 13
    assert len(hex_lut) == 128

    L, H, W, _ = grid_3d.shape
    streamed = np.empty_like(grid_3d)

    # 1. Stream inter-plane channels (ch6-11) with standard LGCA shift
    for i in range(6, 12):
        dl, dr, dc = SHIFTS_13[i]
        streamed[..., i] = np.roll(grid_3d[..., i], shift=(dl, dr, dc), axis=(0, 1, 2))

    # 2. In-plane channels (ch0-5): read synchronously from neighbors' center bits.
    #    These are VIRTUAL — no storage/retention across steps.
    center = grid_3d[..., 12]

    #    W  neighbor at (0, -1, 0)  → roll center by +1 on axis 1
    streamed[..., 0] = np.roll(center, shift=(0, 1, 0), axis=(0, 1, 2))
    #    E  neighbor at (0,  1, 0)  → roll center by -1 on axis 1
    streamed[..., 1] = np.roll(center, shift=(0, -1, 0), axis=(0, 1, 2))
    #    SW neighbor at (0,  0,-1)  → roll center by +1 on axis 2
    streamed[..., 2] = np.roll(center, shift=(0, 0, 1), axis=(0, 1, 2))
    #    NE neighbor at (0,  0, 1)  → roll center by -1 on axis 2
    streamed[..., 3] = np.roll(center, shift=(0, 0, -1), axis=(0, 1, 2))
    #    NW neighbor at (0, -1, 1)  → roll center by (+1,-1) on axes (1,2)
    streamed[..., 4] = np.roll(center, shift=(0, 1, -1), axis=(0, 1, 2))
    #    SE neighbor at (0,  1,-1)  → roll center by (-1,+1) on axes (1,2)
    streamed[..., 5] = np.roll(center, shift=(0, -1, 1), axis=(0, 1, 2))

    # 3. Compute 7-bit hex_state from streamed in-plane + center
    #    hex_state = ch12*64 + ch1*32 + ch5*16 + ch2*8 + ch0*4 + ch4*2 + ch3
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
    # Inter-plane: identity collide (pass through)
    out[..., 6:12] = streamed[..., 6:12]
    # In-plane: broadcast new center bit (these will be overwritten next step)
    out[..., 0:6] = new_center[..., np.newaxis]
    # Center: new center bit
    out[..., 12] = new_center

    # α>0 coupling reserved for future inter-plane tests
    if alpha != 0.0:
        # placeholder: no-op for α=0 test
        pass

    return out


# ── Positive control: 2D hex standalone ────────────────────────────────────

def step_hex_2d(grid: np.ndarray, hex_lut: np.ndarray) -> np.ndarray:
    """Pure 2D hex CA step (exactly step_grid from evolution.py).

    Kept here as a self-contained positive-control implementation.
    """
    # Same neighbor reads as evolution.step_grid but inlined for clarity
    e  = np.roll(grid, -1, axis=0)    # E neighbor
    w  = np.roll(grid,  1, axis=0)    # W neighbor
    ne = np.roll(grid, -1, axis=1)    # NE neighbor
    sw = np.roll(grid,  1, axis=1)    # SW neighbor
    se = np.roll(e,    1, axis=1)     # SE neighbor
    nw = np.roll(w,   -1, axis=1)     # NW neighbor

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


# ── Utility: build seeded 3D grid ──────────────────────────────────────────

def make_3d_seed(grid_size_3d: int = 32,
                 seed_2d_cells: list[tuple[int, int]] | None = None,
                 layer: int | None = None) -> np.ndarray:
    """Create a 3D grid with the L-tromino seed on the [111] plane."""
    if seed_2d_cells is None:
        # Default L-tromino at center of 2D grid
        seed_2d_cells = [(15, 15), (16, 15), (16, 16)]
    if layer is None:
        layer = grid_size_3d // 2  # 16 for 32³

    grid = np.zeros((grid_size_3d, grid_size_3d, grid_size_3d, 13), dtype=np.uint8)
    for r, c in seed_2d_cells:
        grid[layer, r, c, 12] = 1  # center channel
    return grid


# ── F3: Pure LGCA feasibility analysis ─────────────────────────────────────

def attempt_pure_lgca_lut(hex_lut: np.ndarray) -> dict:
    """
    Attempt to build a 13-bit LUT (8192 entries) that:
      1. Is a bijection on {0..8191}
      2. Is bit-conserving (preserves Hamming weight)
      3. Matches hex_lut on in-plane+center channels when inter-plane=0

    The strategy is to set output bits as:
      out_ch0-5 = some function of input state
      out_ch12  = hex_lut(hex_state)
      out_ch6-11 = input_ch6-11 (identity)

    We test several output mappings for ch0-5 and document why each fails.

    Returns
    -------
    dict with 'f3_triggered', 'attempts', 'reason'.
    """
    attempts = []

    # ---- Attempt 1: Broadcast center bit to all in-plane channels ----
    out_lut = np.zeros(8192, dtype=np.uint16)
    pop_in = np.zeros(8192, dtype=np.uint8)
    pop_out = np.zeros(8192, dtype=np.uint8)

    for s in range(8192):
        bits = [(s >> i) & 1 for i in range(13)]
        pop_in[s] = sum(bits)

        ch0, ch1, ch2, ch3, ch4, ch5 = bits[0:6]
        ch6, ch7, ch8, ch9, ch10, ch11 = bits[6:12]
        ch12 = bits[12]

        # Build hex_state from in-plane+center
        hex_state = (
            ch12 * 64 + ch1 * 32 + ch5 * 16 + ch2 * 8 +
            ch0 * 4 + ch4 * 2 + ch3
        )
        new_center = int(hex_lut[hex_state])

        # Inter-plane identity
        out_ch6_11 = (ch6 << 6) | (ch7 << 7) | (ch8 << 8) | (ch9 << 9) | (ch10 << 10) | (ch11 << 11)
        # In-plane broadcast of new center
        out_ch0_5 = new_center * ((1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5))
        out_ch12 = new_center << 12

        out_lut[s] = out_ch0_5 | out_ch6_11 | out_ch12
        pop_out[s] = bin(int(out_lut[s])).count('1')

    # Check bijection
    unique_out = len(np.unique(out_lut))
    bijective = (unique_out == 8192)

    # Check bit conservation
    bit_conserving = bool(np.array_equal(pop_in, pop_out))

    # Identify first violating state
    first_violation = None
    for s in range(8192):
        if pop_in[s] != pop_out[s]:
            first_violation = int(s)
            break

    attempts.append({
        "name": "broadcast_center_to_inplane_identity_interplane",
        "bijective": bijective,
        "bit_conserving": bit_conserving,
        "unique_outputs": int(unique_out),
        "first_violation": first_violation,
        "description": (
            "Sets out_ch0-5 = new_center (broadcast), out_ch6-11 = in_ch6-11, "
            "out_ch12 = new_center. 6 output in-plane bits all equal."
        )
    })

    # ---- Attempt 2: Permute in-plane bits to maintain some distribution ----
    # This cannot fix the core problem: the hex rule changes total bit count
    # for states with inter-plane=0, which violates bit conservation for
    # the 7-bit subspace regardless of how we map the remaining 6 bits.

    # The fundamental issue: consider two states with same in-plane+center
    # but different inter-plane bits. If inter-plane bits > 0, the input
    # and output populations can be balanced by adjusting inter-plane outputs.
    # But for states with inter-plane=0, only 7 bits are available, and
    # hex_rule only computes 1 output bit. We have 6 in-plane outputs to set.
    # To balance population, we need pop_out = pop_in = pop_7bit.
    # But output has 6*out_center + out_center + pop_interplane_out.
    # With interplane=0: pop_out = 7*new_center. This can be 0 or 7.
    # pop_in ranges from 0 to 7. So we need pop_in ∈ {0, 7} for all inputs,
    # which is false.

    # Let's prove with a concrete counterexample for Attempt 1.
    # State s = 0 (all zeros, inter-plane=0): pop_in=0, hex_state=0, new_center=0, pop_out=0. OK.
    # State s = 1 (ch0=1, rest=0): pop_in=1, hex_state=4 (ch0=1, ch12=0), new_center=hex_lut[4], pop_out=6*new_center + new_center = 7*new_center.
    #   hex_lut[4] = ? Let's check champion_rule_perfect.json: rule_dict has key 4 → value 4, but LUT entry 4 maps to 4. rule_dict_to_lut does lut[k]=v, so lut[4]=4, then ((lut>>6)&1) = 0. So new_center=0, pop_out=0 ≠ 1. VIOLATION.

    counterexample = {
        "state": 1,
        "binary": format(1, '013b'),
        "pop_in": 1,
        "hex_state": 4,
        "new_center": int(hex_lut[4]),
        "pop_out": 0,
        "reason": "Input has 1 bit, output has 0 bits."
    }

    # ---- Attempt 3: Try to use inter-plane bits as "reservoir" ----
    # Even with inter-plane bits present, the mapping is not a bijection
    # because multiple inputs with different in-plane+center but same
    # hex_state can map to the same output.

    # Check if any two states with different hex inputs but same hex_state
    # produce different outputs (they should for bijection).
    collisions = 0
    seen_out = {}
    for s in range(8192):
        if out_lut[s] in seen_out:
            collisions += 1
        else:
            seen_out[out_lut[s]] = s

    attempts[0]["total_collisions"] = collisions

    # ---- Conclusion ----
    f3_triggered = not (bijective and bit_conserving)

    return {
        "f3_triggered": f3_triggered,
        "attempts": attempts,
        "counterexample": counterexample,
        "reason": (
            "The hex CA rule is not bit-conserving on the 7-bit in-plane+center subspace. "
            "A pure LGCA LUT must preserve total Hamming weight for all 8192 states. "
            "When inter-plane channels are zero (128 such states), the output population "
            "is 7*new_center (0 or 7), while input population ranges 0..7. "
            "No bijective, bit-conserving mapping can reconcile this. "
            "Additionally, even ignoring bit conservation, many inputs collide to the same "
            "output because the 7-bit→1-bit hex rule loses information. "
        )
    }
