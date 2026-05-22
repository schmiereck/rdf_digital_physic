#!/usr/bin/env python3
"""engine_d4_closed_loop_v2.py — 3D+1 Spacetime LGCA with FFT-smoothed Closed-Loop Latching/Trapping.

This engine features a closed-loop coupling where moving bits deposit local "charge" into
a latency field. This field then decays and undergoes periodic 3D Gaussian smoothing using FFT
to prevent discrete gradient shocks:
    decayed_field = gamma * latency_field + eta * active_bits
    latency_field = gaussian_blur_3d_fft(decayed_field, sigma)
Values below 1e-5 are clamped to 0.0.
Trapping of bits is determined by the total potential:
    M = latency_field + permanent_mass
where the latching duration is scaled by alpha.
"""

from __future__ import annotations

import os
import sys
import numpy as np
import json
from typing import Dict, Any, List, Tuple

# Adjust sys.path to ensure we can import engine_d4_spacetime and engine_3d
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class ClosedLoopLatchingEngine:
    """Manages a 3D toroidal LGCA with closed-loop dynamic latching (trapping) driven by an FFT-smoothed latency field."""

    def __init__(
        self,
        L: int,
        gamma: float,
        eta: float,
        threshold: float,
        alpha: float,
        sigma: float,
        exponent: float = 1.0,
        lut_seed: int = 1,
        use_12_channels: bool = True,
        cutoff_radius: int = 4,  # Kept for compatibility
    ):
        """
        Parameters:
            L: Grid size (toroidal LxLxL).
            gamma: Temporal retention rate of the latency field.
            eta: Deposition rate of latency charge per active bit.
            threshold: Potential threshold M for trapping.
            alpha: Scaling factor for trapping duration.
            sigma: Standard deviation for periodic Gaussian smoothing.
            exponent: Exponent for the duration scaling (duration = round(alpha * (M**exponent))).
            lut_seed: Seed to generate symmetric collision lookup table.
            use_12_channels: True to use 12-channel FCC grid (default), False for 6-channel D4 spacetime.
            cutoff_radius: Kept for compatibility.
        """
        self.L = L
        self.gamma = gamma
        self.eta = eta
        self.threshold = threshold
        self.alpha = alpha
        self.sigma = sigma
        self.exponent = exponent
        self.lut_seed = lut_seed
        self.use_12_channels = use_12_channels
        self.cutoff_radius = cutoff_radius
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

    def gaussian_blur_3d_fft(self, field: np.ndarray, sigma: float) -> np.ndarray:
        L = field.shape[0]
        k = np.fft.fftfreq(L)
        KX, KY, KZ = np.meshgrid(k, k, k, indexing="ij")
        K_sq = KX**2 + KY**2 + KZ**2
        H = np.exp(-2.0 * (np.pi * sigma)**2 * K_sq)
        field_fft = np.fft.fftn(field)
        return np.real(np.fft.ifftn(field_fft * H))

    def step(self) -> None:
        """Executes a single step of the closed-loop latching LGCA:
        1. Timer decrement and release: release expired latched bits back to temporal grid
           if the target temporal channel is empty. If blocked, keep the timer at 1.
        2. Compute deposition & decay, then apply 3D periodic Gaussian smoothing with standard deviation self.sigma.
        3. Clamp small values: latency_field < 1e-5 set to 0.0.
        4. Trapping: for any cell with M = latency_field + permanent_mass >= threshold,
           trap incoming temporal bits (except those just released in this step) into
           the latched grid, setting their timers to round(alpha * (M ** exponent)).
        5. Collision: apply standard Oh collision.
        6. Streaming: stream temporal bits.
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

        # 2. Compute decayed field and update latency_field using 3D FFT Gaussian blur
        active_bits = self.temporal_grid.sum(axis=-1).astype(np.float64) + self.latched_grid.sum(axis=-1).astype(np.float64)
        decayed_field = self.gamma * self.latency_field + self.eta * active_bits
        
        if self.sigma > 0.0:
            self.latency_field = self.gaussian_blur_3d_fft(decayed_field, self.sigma)
        else:
            self.latency_field = decayed_field

        # 3. Clamp small values
        self.latency_field[self.latency_field < 1e-5] = 0.0

        # 4. Trapping
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

        # 5. Collision: apply the Oh symmetric LUT on remaining temporal bits
        self.temporal_grid = self._collide(self.temporal_grid, self.lut)

        # 6. Streaming: stream temporal bits
        self.temporal_grid = self._stream(self.temporal_grid)

# Alias for compatibility
ClosedLoopLatchingEngineV2 = ClosedLoopLatchingEngine

def self_test():
    """Runs a robust self-test verifying perfect bit conservation and dynamic latency field evolution."""
    print("="*80)
    print("RUNNING SELF-TEST FOR ClosedLoopLatchingEngineV2")
    print("="*80)
    
    L = 16
    engine = ClosedLoopLatchingEngine(
        L=L,
        gamma=0.95,
        eta=1.0,
        threshold=0.2,
        alpha=2.0,
        sigma=1.5,
        exponent=1.0,
        lut_seed=8,
        use_12_channels=True
    )
    
    # Let's seed some random bits
    np.random.seed(42)
    initial_bits = 12
    seeded_count = 0
    while seeded_count < initial_bits:
        x, y, z, c = np.random.randint(0, L), np.random.randint(0, L), np.random.randint(0, L), np.random.randint(0, 12)
        if engine.temporal_grid[x, y, z, c] == 0:
            engine.temporal_grid[x, y, z, c] = 1
            seeded_count += 1
            
    # Verify bit count
    total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
    assert total_bits == initial_bits, f"Expected {initial_bits} bits, got {total_bits}"
    print(f"Seeded {total_bits} bits successfully.")
    
    # Run 50 steps of simulation
    for step_num in range(1, 51):
        engine.step()
        
        # Verify perfect bit conservation
        current_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
        assert current_bits == initial_bits, f"Bit conservation violated at step {step_num}! Expected {initial_bits}, got {current_bits}"
        
        # Check latency field properties
        assert np.all(engine.latency_field >= 0.0), f"Negative latency field values at step {step_num}!"
        
        if step_num in [1, 10, 50]:
            lat_sum = np.sum(engine.latency_field)
            lat_max = np.max(engine.latency_field)
            latched_count = int(engine.latched_grid.sum())
            print(f"Step {step_num:2d}: Bits (Temporal={current_bits - latched_count}, Latched={latched_count}), Latency (Sum={lat_sum:.4f}, Max={lat_max:.4f})")
            
    print("\nSelf-test PASSED successfully! Perfect bit conservation and dynamic latency evolution verified.")
    print("="*80)

if __name__ == "__main__":
    self_test()
