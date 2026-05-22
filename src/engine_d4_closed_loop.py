#!/usr/bin/env python3
"""engine_d4_closed_loop.py — 3D+1 Spacetime LGCA with Closed-Loop Latching/Trapping.

This engine features a closed-loop coupling where moving bits deposit local "charge" into
a latency field. This field then diffuses and decays according to a discrete heat-like equation:
    new_latency = (1.0 - gamma) * latency_field + kappa * Laplacian + deposition.

To prevent infinite numerical dispersion/underflow, an optimized update mask limits calculations
to cells within a cutoff radius of active bits or non-trivial latency (> 1e-4).
Trapping of bits is determined by the total potential:
    M = latency_field + permanent_mass
where the latching duration is scaled by alpha.
"""

from __future__ import annotations

import os
import sys
import numpy as np
from typing import Dict, Any, List, Tuple

# Adjust sys.path to ensure we can import engine_d4_spacetime and engine_3d
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class ClosedLoopLatchingEngine:
    """Manages a 3D toroidal LGCA with closed-loop dynamic latching (trapping) driven by a diffusing latency field."""

    def __init__(
        self,
        L: int,
        gamma: float,
        kappa: float,
        eta: float,
        threshold: float,
        alpha: float,
        cutoff_radius: int,
        exponent: float = 1.0,
        lut_seed: int = 1,
        use_12_channels: bool = True,
    ):
        """
        Parameters:
            L: Grid size (toroidal LxLxL).
            gamma: Decay rate of the latency field.
            kappa: Diffusion rate (Laplacian coefficient) of the latency field.
            eta: Deposition rate of latency charge per active bit.
            threshold: Potential threshold M for trapping.
            alpha: Scaling factor for trapping duration.
            cutoff_radius: Radius around active bits / non-trivial latency for update mask.
            exponent: Exponent for the duration scaling (duration = round(alpha * (M**exponent))).
            lut_seed: Seed to generate symmetric collision lookup table.
            use_12_channels: True to use 12-channel FCC grid (default), False for 6-channel D4 spacetime.
        """
        self.L = L
        self.gamma = gamma
        self.kappa = kappa
        self.eta = eta
        self.threshold = threshold
        self.alpha = alpha
        self.cutoff_radius = cutoff_radius
        self.exponent = exponent
        self.lut_seed = lut_seed
        self.use_12_channels = use_12_channels
        self.C = 12 if use_12_channels else 6

        # Initialize grids (L, L, L, C)
        self.temporal_grid = np.zeros((L, L, L, self.C), dtype=np.uint8)
        self.latched_grid = np.zeros((L, L, L, self.C), dtype=np.uint8)
        self.timers = np.zeros((L, L, L, self.C), dtype=np.int32)
        
        # Continuous fields (L, L, L)
        self.latency_field = np.zeros((L, L, L), dtype=np.float64)
        self.permanent_mass = np.zeros((L, L, L), dtype=np.float64)

        # Import and generate LUT dynamically
        if self.use_12_channels:
            try:
                from src.search_3d_gliders import generate_symmetric_lut as generate_lut_12
                from src.engine_3d import collide as collide_12, stream as stream_12
            except ModuleNotFoundError:
                from search_3d_gliders import generate_symmetric_lut as generate_lut_12
                from engine_3d import collide as collide_12, stream as stream_12
            self.lut = generate_lut_12(seed=self.lut_seed)
            self._collide = collide_12
            self._stream = stream_12
        else:
            try:
                from src.engine_d4_spacetime import generate_symmetric_lut as generate_lut_6, collide as collide_6, stream as stream_6
            except ModuleNotFoundError:
                from engine_d4_spacetime import generate_symmetric_lut as generate_lut_6, collide as collide_6, stream as stream_6
            self.lut = generate_lut_6(seed=self.lut_seed)
            self._collide = collide_6
            self._stream = stream_6

    def step(self) -> None:
        """Executes a single step of the closed-loop latching LGCA:
        1. Timer decrement and release: release expired latched bits back to temporal grid
           if the target temporal channel is empty. If blocked, keep the timer at 1.
        2. Compute deposition: deposition = eta * active_bits.
        3. Construct optimized update mask using periodic roll.
        4. Compute discrete diffusion and decay of latency field inside the mask, and
           clear potential float noise outside the mask to exactly 0.0.
        5. Trapping: for any cell with M = latency_field + permanent_mass >= threshold,
           trap incoming temporal bits (except those just released in this step) into
           the latched grid, setting their timers to round(alpha * (M ** exponent)).
        6. Collision: apply standard Oh collision.
        7. Streaming: stream temporal bits.
        """
        # 1. Timer decrement and release
        want_to_release = (self.latched_grid == 1) & (self.timers == 1)
        released_mask = want_to_release & (self.temporal_grid == 0)
        blocked_mask = want_to_release & (self.temporal_grid == 1)

        # Decrement active timers where latched_grid is 1, but NOT the blocked ones
        active_mask = (self.latched_grid == 1) & (~blocked_mask)
        self.timers[active_mask] -= 1

        # Move released bits back to temporal grid, clear latched_grid and timers
        self.temporal_grid[released_mask] = 1
        self.latched_grid[released_mask] = 0
        self.timers[released_mask] = 0

        # 2. Compute deposition
        active_bits = self.temporal_grid.sum(axis=-1).astype(np.float64) + self.latched_grid.sum(axis=-1).astype(np.float64)
        deposition = self.eta * active_bits

        # 3. Construct optimized update mask
        # Sources are cells with active bits or non-trivial latency
        sources = (active_bits > 0) | (self.latency_field > 1e-4)
        
        # Dilate mask up to cutoff_radius using periodic roll
        mask = sources.copy()
        for _ in range(self.cutoff_radius):
            next_mask = mask.copy()
            for dx, dy, dz in [
                (1, 0, 0), (-1, 0, 0),
                (0, 1, 0), (0, -1, 0),
                (0, 0, 1), (0, 0, -1)
            ]:
                next_mask |= np.roll(mask, shift=(dx, dy, dz), axis=(0, 1, 2))
            mask = next_mask

        # 4. Discrete diffusion and decay of the latency_field inside the mask
        # Compute the 3D discrete Laplacian with periodic boundaries
        laplacian = np.zeros_like(self.latency_field)
        for dx, dy, dz in [
            (1, 0, 0), (-1, 0, 0),
            (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1)
        ]:
            laplacian += np.roll(self.latency_field, shift=(dx, dy, dz), axis=(0, 1, 2))
        laplacian -= 6.0 * self.latency_field

        # Update latency field using: new_latency = (1.0 - gamma) * latency_field + kappa * Laplacian + deposition
        new_latency = (1.0 - self.gamma) * self.latency_field + self.kappa * laplacian + deposition
        
        # Set the updated latency field inside the mask, and clear potential float noise outside to exactly 0.0
        self.latency_field[mask] = new_latency[mask]
        self.latency_field[~mask] = 0.0

        # 5. Trapping
        # Total potential M = latency_field + permanent_mass
        M = self.latency_field + self.permanent_mass
        
        trap_condition = (M >= self.threshold)
        trap_mask = (
            trap_condition[..., np.newaxis]
            & (self.temporal_grid == 1)
            & (~released_mask)
            & (self.latched_grid == 0)
        )

        # Compute trapping duration for each cell (ensure at least 1 step duration)
        duration = np.round(self.alpha * (M**self.exponent)).astype(np.int32)
        duration = np.maximum(duration, 1)
        duration_4d = np.repeat(duration[..., np.newaxis], self.C, axis=-1)

        # Move trapped bits
        self.temporal_grid[trap_mask] = 0
        self.latched_grid[trap_mask] = 1
        self.timers[trap_mask] = duration_4d[trap_mask]

        # 6. Collision: apply the Oh symmetric LUT on remaining temporal bits
        self.temporal_grid = self._collide(self.temporal_grid, self.lut)

        # 7. Streaming: stream temporal bits
        self.temporal_grid = self._stream(self.temporal_grid)
