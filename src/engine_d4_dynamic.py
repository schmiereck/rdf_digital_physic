#!/usr/bin/env python3
"""engine_d4_dynamic.py — 3D+1 Spacetime LGCA with Fully Dynamic Local Latching/Trapping.

In this engine, there is no permanent static mass. Spacetime coordinate latency (latching)
is driven purely by the moving bits themselves, reflecting a dynamic gravity-like spacetime
deformation.
"""

from __future__ import annotations

import os
import sys
import numpy as np
from typing import Dict, Any, List, Tuple

# Adjust sys.path to ensure we can import engine_d4_spacetime
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from src.engine_d4_spacetime import generate_symmetric_lut, collide, stream, SHIFTS
except ModuleNotFoundError:
    from engine_d4_spacetime import generate_symmetric_lut, collide, stream, SHIFTS


class DynamicLatchingEngine:
    """Manages a 3D+1 D4 Spacetime LGCA with dynamic local latching (trapping) driven by moving bits.

    Attributes:
        L (int): Grid size.
        alpha (float): Coupling constant for trapping duration.
        threshold (float): Density threshold (M_threshold) for trapping.
        exponent (float): Exponent for the power law of local mass density.
        lut_seed (int): Seed for standard O_h symmetric collision LUT.
        temporal_grid (np.ndarray): Shape (L, L, L, 6), temporal channels.
        latched_grid (np.ndarray): Shape (L, L, L, 6), latched bits.
        timers (np.ndarray): Shape (L, L, L, 6), countdown for latched bits.
        lut (np.ndarray): Symmetric 64-element lookup table for standard O_h collisions.
    """

    def __init__(
        self,
        L: int,
        alpha: float,
        threshold: float,
        exponent: float = 1.0,
        lut_seed: int = 1,
    ):
        self.L = L
        self.alpha = alpha
        self.threshold = threshold
        self.exponent = exponent
        self.lut_seed = lut_seed

        # Initialize grids (L, L, L, 6)
        self.temporal_grid = np.zeros((L, L, L, 6), dtype=np.uint8)
        self.latched_grid = np.zeros((L, L, L, 6), dtype=np.uint8)
        self.timers = np.zeros((L, L, L, 6), dtype=np.int32)

        # Generate standard O_h symmetric collision LUT
        self.lut = generate_symmetric_lut(seed=self.lut_seed)

    def compute_local_density(self) -> np.ndarray:
        """Compute the smoothed local mass density M for each cell.

        M(x, y, z) is the sum of bits (temporal + latched) in each cell,
        smoothed by summing with its 6 nearest spatial neighbors (using periodic roll).
        """
        # Sum of bits in each cell
        cell_m = (
            self.temporal_grid.sum(axis=-1).astype(np.float64)
            + self.latched_grid.sum(axis=-1).astype(np.float64)
        )

        # Smooth with its 6 nearest spatial neighbors (using periodic roll)
        smoothed = cell_m.copy()
        for dx, dy, dz in [
            (1, 0, 0),
            (-1, 0, 0),
            (0, 1, 0),
            (0, -1, 0),
            (0, 0, 1),
            (0, 0, -1),
        ]:
            smoothed += np.roll(cell_m, shift=(dx, dy, dz), axis=(0, 1, 2))
        return smoothed

    def step(self) -> None:
        """Executes a single step of the fully dynamic latching Spacetime LGCA:
        a. Timer decrement and release: release expired latched bits back to `temporal_grid`
           if the target temporal channel is empty. If blocked, keep the timer at 1.
        b. Compute updated local density field M.
        c. Trapping: for any cell with M >= threshold, trap incoming temporal bits (except
           those just released in this step) into the `latched_grid`, setting their timers to
           `round(alpha * (M ** exponent))` (ensure at least 1 step duration). If the target
           latched channel is occupied, trapping is blocked.
        d. Collision: apply the Oh symmetric LUT on remaining temporal bits.
        e. Stream: stream temporal bits using the 6 Shifts.
        """
        # a. Timer decrement and release
        # Identify bits that want to be released in this step (timer is 1 and currently latched)
        want_to_release = (self.latched_grid == 1) & (self.timers == 1)

        # We can only release if the corresponding temporal channel is currently empty (temporal_grid == 0)
        released_mask = want_to_release & (self.temporal_grid == 0)

        # For those that want to release but the temporal channel is occupied, keep them latched
        blocked_mask = want_to_release & (self.temporal_grid == 1)

        # Decrement active timers where latched_grid is 1, but NOT the blocked ones
        active_mask = (self.latched_grid == 1) & (~blocked_mask)
        self.timers[active_mask] -= 1

        # Move released bits back to the temporal grid, clear latched_grid and timers
        self.temporal_grid[released_mask] = 1
        self.latched_grid[released_mask] = 0
        self.timers[released_mask] = 0

        # b. Compute updated local density field M
        M = self.compute_local_density()

        # c. Trapping
        # Trapping condition: local density >= threshold
        trap_condition = M >= self.threshold

        # Broadcast trap condition to 6 channels.
        # We only trap unlatched temporal bits if:
        # - The temporal channel has a bit (temporal_grid == 1)
        # - The temporal bit was NOT just released in this step (~released_mask)
        # - The destination latched channel is currently empty (latched_grid == 0)
        trap_mask = (
            trap_condition[..., np.newaxis]
            & (self.temporal_grid == 1)
            & (~released_mask)
            & (self.latched_grid == 0)
        )

        # Compute duration for each cell (ensure at least 1 step duration)
        duration = np.round(self.alpha * (M**self.exponent)).astype(np.int32)
        duration = np.maximum(duration, 1)
        duration_4d = np.repeat(duration[..., np.newaxis], 6, axis=-1)

        # Move trapped bits to latched grid and set their timers
        self.temporal_grid[trap_mask] = 0
        self.latched_grid[trap_mask] = 1
        self.timers[trap_mask] = duration_4d[trap_mask]

        # d. Collision: apply the Oh symmetric LUT on remaining temporal bits
        self.temporal_grid = collide(self.temporal_grid, self.lut)

        # e. Stream: stream temporal bits using the 6 Shifts
        self.temporal_grid = stream(self.temporal_grid)


# ---------------------------------------------------------------------------
# Self-Test Suite
# ---------------------------------------------------------------------------


def run_self_tests() -> None:
    print("=" * 72)
    print("engine_d4_dynamic — Self-Test Suite")
    print("=" * 72)

    # 1. Verification of exact conservation of bit count under randomized initial conditions
    print("\n[1] Verifying perfect conservation of bit count over 50 steps...")
    L = 12
    alpha = 2.5
    threshold = 2.0
    exponent = 1.2
    lut_seed = 42

    engine = DynamicLatchingEngine(
        L=L, alpha=alpha, threshold=threshold, exponent=exponent, lut_seed=lut_seed
    )

    # Place some random bits with disjoint temporal/latched configurations
    rng = np.random.default_rng(12345)
    choices = rng.choice([0, 1, 2], size=(L, L, L, 6), p=[0.75, 0.20, 0.05])
    temporal_init = (choices == 1).astype(np.uint8)
    latched_init = (choices == 2).astype(np.uint8)

    engine.temporal_grid = temporal_init.copy()
    engine.latched_grid = latched_init.copy()

    # Assign random timers >= 1 for the latched bits
    engine.timers = latched_init.astype(np.int32) * rng.integers(
        1, 10, size=(L, L, L, 6)
    )

    initial_total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
    print(f"  Initial temporal bits : {int(engine.temporal_grid.sum())}")
    print(f"  Initial latched bits  : {int(engine.latched_grid.sum())}")
    print(f"  Initial total bits    : {initial_total_bits}")

    assert initial_total_bits > 0, "No bits placed in the initial grid!"

    trapping_occurred = False
    releasing_occurred = False

    for step_idx in range(1, 51):
        prev_latched = int(engine.latched_grid.sum())

        engine.step()

        current_temporal = int(engine.temporal_grid.sum())
        current_latched = int(engine.latched_grid.sum())
        current_total_bits = current_temporal + current_latched

        # Monitor dynamic transitions
        if current_latched > prev_latched:
            trapping_occurred = True
        elif current_latched < prev_latched:
            releasing_occurred = True

        print(
            f"  Step {step_idx:02d}: temporal={current_temporal:<5} latched={current_latched:<5} total={current_total_bits:<5}"
        )

        assert (
            current_total_bits == initial_total_bits
        ), f"Bit count changed at step {step_idx}: {current_total_bits} vs {initial_total_bits}"

    print(f"  [SUCCESS] Perfect bit conservation verified over 50 steps!")
    print(f"  [INFO] Trapping occurred during run: {trapping_occurred}")
    print(f"  [INFO] Releasing occurred during run: {releasing_occurred}")

    # 2. Re-test with a different exponent and coupling to verify robustness
    print("\n[2] Verifying robustness with different parameters...")
    engine_robust = DynamicLatchingEngine(
        L=8, alpha=4.0, threshold=1.0, exponent=2.0, lut_seed=13
    )
    choices_rob = rng.choice([0, 1, 2], size=(8, 8, 8, 6), p=[0.60, 0.30, 0.10])
    engine_robust.temporal_grid = (choices_rob == 1).astype(np.uint8)
    engine_robust.latched_grid = (choices_rob == 2).astype(np.uint8)
    engine_robust.timers = engine_robust.latched_grid.astype(
        np.int32
    ) * rng.integers(1, 5, size=(8, 8, 8, 6))

    init_rob_bits = int(
        engine_robust.temporal_grid.sum() + engine_robust.latched_grid.sum()
    )

    for step_idx in range(1, 21):
        engine_robust.step()
        curr_rob_bits = int(
            engine_robust.temporal_grid.sum() + engine_robust.latched_grid.sum()
        )
        assert (
            curr_rob_bits == init_rob_bits
        ), f"Bit count mismatch under robust config at step {step_idx}"

    print(f"  [SUCCESS] Robustness test passed successfully!")
    print("\n" + "=" * 72)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 72)


if __name__ == "__main__":
    run_self_tests()
