#!/usr/bin/env python3
"""engine_d4_latching.py — 3D+1 Spacetime LGCA with Local Latching/Trapping.

This module implements a local trapping/latching mechanism on top of the 3D+1 D4 Spacetime LGCA,
simulating coordinate time dilation (Shapiro delay) and Fermat's principle of least time (light bending)
directly on the cellular automaton lattice.
"""

from __future__ import annotations

import os
import sys
import heapq
import numpy as np
from typing import List, Tuple, Dict, Any

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


class LatchingEngine:
    """Manages a 3D+1 D4 Spacetime LGCA with local latching (trapping) mechanism.

    Attributes:
        L (int): Grid size.
        temporal_grid (np.ndarray): Shape (L, L, L, 6), temporal channels.
        latched_grid (np.ndarray): Shape (L, L, L, 6), latched bits.
        timers (np.ndarray): Shape (L, L, L, 6), countdown for latched bits.
        permanent_mass (np.ndarray): Shape (L, L, L), static mass well.
        latch_duration (int): Duration (N) of the latching trap.
        threshold (float): Density threshold (M_threshold) for trapping.
        lut (np.ndarray): Symmetric 64-element lookup table for standard O_h collisions.
    """

    def __init__(self, L: int, latch_duration: int, threshold: float):
        self.L = L
        self.latch_duration = latch_duration
        self.threshold = threshold

        # Initialize grids
        self.temporal_grid = np.zeros((L, L, L, 6), dtype=np.uint8)
        self.latched_grid = np.zeros((L, L, L, 6), dtype=np.uint8)
        self.timers = np.zeros((L, L, L, 6), dtype=np.int32)
        self.permanent_mass = np.zeros((L, L, L), dtype=np.float64)

        # Generate standard O_h symmetric collision LUT using seed=1.
        # This LUT is bit-conserving, bijective, O_h-equivariant, and identity for weight 1.
        self.lut = generate_symmetric_lut(seed=1)

    def compute_local_density(self) -> np.ndarray:
        """Compute the smoothed local mass density M for each cell.

        M(x, y, z) is the sum of bits (temporal + latched) plus permanent mass
        at the cell itself, smoothed by summing with its 6 nearest spatial neighbors.
        """
        # Sum of bits in each cell + permanent mass
        cell_m = (self.temporal_grid.sum(axis=-1).astype(np.float64) + 
                  self.latched_grid.sum(axis=-1).astype(np.float64) + 
                  self.permanent_mass)
        
        # Smooth with its 6 nearest spatial neighbors (using periodic roll)
        smoothed = cell_m.copy()
        for dx, dy, dz in [
            (1, 0, 0), (-1, 0, 0),
            (0, 1, 0), (0, -1, 0),
            (0, 0, 1), (0, 0, -1)
        ]:
            smoothed += np.roll(cell_m, shift=(dx, dy, dz), axis=(0, 1, 2))
        return smoothed

    def step(self) -> None:
        """Executes a single step of the latching Spacetime LGCA:
        1. Decrements active timers; releases expired latched bits back to the temporal grid.
           If a temporal channel is already occupied, the release is blocked (timer held at 1).
        2. Computes the updated local density field.
        3. Traps temporal bits in cells exceeding the threshold, moving them to latched_grid
           and setting their timers (exempting just-released bits from trapping in this step).
           If a latched channel is already occupied, trapping is blocked.
        4. Applies the standard O_h symmetric collision on remaining temporal bits.
        5. Streams temporal bits.
        """
        # 1. Timer Decrement and Release
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

        # 2. Compute local density
        M = self.compute_local_density()

        # 3. Trapping
        # Trapping condition: local density >= threshold
        trap_condition = (M >= self.threshold)
        
        # Broadcast trap condition to 6 channels.
        # We only trap unlatched temporal bits if:
        # - The temporal channel has a bit (temporal_grid == 1)
        # - The temporal bit was NOT just released in this step (~released_mask)
        # - The destination latched channel is currently empty (latched_grid == 0)
        trap_mask = (trap_condition[..., np.newaxis] & 
                     (self.temporal_grid == 1) & 
                     (~released_mask) & 
                     (self.latched_grid == 0))

        # Move trapped bits to latched grid and set their timers
        self.temporal_grid[trap_mask] = 0
        self.latched_grid[trap_mask] = 1
        self.timers[trap_mask] = self.latch_duration

        # 4. Apply standard O_h symmetric collision on remaining temporal bits
        self.temporal_grid = collide(self.temporal_grid, self.lut)

        # 5. Stream temporal bits
        self.temporal_grid = stream(self.temporal_grid)


# ---------------------------------------------------------------------------
# Dijkstra Fermat Pathfinding
# ---------------------------------------------------------------------------

def run_dijkstra_pathfinding(
    engine: LatchingEngine, 
    start_node: Tuple[int, int, int], 
    tie_breaker_weight: float = 1e-6
) -> List[Tuple[int, int, int]]:
    """Runs Dijkstra Fermat pathfinding on the emergent latency field.

    Link weight = 1 + latching_delay.
    
    Args:
        engine (LatchingEngine): The engine containing the static mass & state.
        start_node (tuple): 3D coordinates (0, y_start, z_start).
        tie_breaker_weight (float): Small penalty to prefer straight-line trajectories.

    Returns:
        list of tuple: The list of 3D coordinates representing the shortest path
                       from start_node to any node with X = L - 1.
    """
    L = engine.L
    # Compute current smoothed density field
    M = engine.compute_local_density()
    
    # Priority queue stores (cost, current_node)
    pq = []
    heapq.heappush(pq, (0.0, start_node))
    
    best_cost = {start_node: 0.0}
    parent = {start_node: None}
    
    target_node = None
    x_start, y_start, z_start = start_node
    
    while pq:
        curr_cost, u = heapq.heappop(pq)
        
        if curr_cost > best_cost.get(u, float('inf')):
            continue
            
        x, y, z = u
        
        # Target: reached the far side X = L - 1
        if x == L - 1:
            target_node = u
            break
            
        # Explore 6 nearest neighbors
        # Restrict x to stay within [0, L-1] to prevent wrapping in the direction of propagation.
        # Allow periodic wrapping in y and z.
        neighbors = []
        if x + 1 < L:
            neighbors.append((x + 1, y, z))
        if x - 1 >= 0:
            neighbors.append((x - 1, y, z))
        neighbors.append((x, (y + 1) % L, z))
        neighbors.append((x, (y - 1) % L, z))
        neighbors.append((x, y, (z + 1) % L))
        neighbors.append((x, y, (z - 1) % L))
        
        for v in neighbors:
            v_density = M[v]
            latching_delay = engine.latch_duration if v_density >= engine.threshold else 0
            cost_uv = 1.0 + latching_delay
            
            # Periodic tie-breaker to favor straight-line path near y_start, z_start
            dy_val = (v[1] - y_start) % L
            if dy_val > L // 2:
                dy_val -= L
            dz_val = (v[2] - z_start) % L
            if dz_val > L // 2:
                dz_val -= L
            tb_cost = tie_breaker_weight * (dy_val**2 + dz_val**2)
            
            new_cost = curr_cost + cost_uv + tb_cost
            
            if new_cost < best_cost.get(v, float('inf')):
                best_cost[v] = new_cost
                parent[v] = u
                heapq.heappush(pq, (new_cost, v))
                
    if target_node is None:
        raise ValueError("No path found to the target boundary X = L - 1")
        
    # Reconstruct path
    path = []
    curr = target_node
    while curr is not None:
        path.append(curr)
        curr = parent[curr]
    path.reverse()
    
    return path


def get_path_deflection(path: List[Tuple[int, int, int]], start_node: Tuple[int, int, int], L: int) -> int:
    """Computes the maximum spatial deflection (absolute deviation in Y/Z)
    along the path from the starting straight-line trajectory.
    """
    _, y_start, z_start = start_node
    max_deflection = 0
    for x, y, z in path:
        dy = (y - y_start) % L
        if dy > L // 2:
            dy -= L
        dz = (z - z_start) % L
        if dz > L // 2:
            dz -= L
        dev = max(abs(dy), abs(dz))
        if dev > max_deflection:
            max_deflection = dev
    return max_deflection


# ---------------------------------------------------------------------------
# Shapiro Delay Measurement Function
# ---------------------------------------------------------------------------

def measure_shapiro_delay(
    latch_duration: int = 10, 
    threshold: float = 5.0, 
    mass_value: float = 10.0
) -> Dict[int, int]:
    """Measures the coordinate travel time of a light pulse (single temporal bit)
    from X = 0 to X = 31 in a 32x32x32 grid with a central permanent mass.

    Returns:
        dict: Maps the Y impact parameter (distance from the mass at Y=16)
              to the exact coordinate time (number of steps) taken to reach X = 31.
    """
    L = 32
    results = {}
    
    # We test impact parameters corresponding to Y starting from 16 (direct hit) down to 12 (far away)
    for y_start in [16, 15, 14, 13, 12]:
        b = abs(y_start - 16)
        
        # Create engine
        engine = LatchingEngine(L=L, latch_duration=latch_duration, threshold=threshold)
        
        # Setup central mass
        engine.permanent_mass[16, 16, 16] = mass_value
        
        # Launch a single temporal bit in channel 4 (shift is (1, 0, 0)) at X = 0, Y = y_start, Z = 16
        engine.temporal_grid[0, y_start, 16, 4] = 1
        
        steps = 0
        max_steps = 1000
        reached = False
        while steps < max_steps:
            # Check if the bit has reached X = 31 (either in temporal_grid or latched_grid)
            if engine.temporal_grid[31, y_start, 16, 4] == 1 or engine.latched_grid[31, y_start, 16, 4] == 1:
                reached = True
                break
            engine.step()
            steps += 1
            
        if reached:
            results[b] = steps
        else:
            results[b] = None
            
    return results


# ---------------------------------------------------------------------------
# Self-test execution
# ---------------------------------------------------------------------------

def run_self_tests() -> None:
    print("=" * 72)
    print("engine_d4_latching — Self-Test Suite")
    print("=" * 72)

    # 1. Conservation of Bit Count
    print("\n[1] Verifying exact conservation of bit count...")
    L = 16
    engine = LatchingEngine(L=L, latch_duration=5, threshold=3.0)
    # Set up some random static mass and random bits in both temporal and latched grids
    rng = np.random.default_rng(1234)
    engine.permanent_mass = rng.uniform(0, 10, size=(L, L, L))
    
    # Place some initial bits
    engine.temporal_grid = rng.integers(0, 2, size=(L, L, L, 6), dtype=np.uint8)
    engine.latched_grid = rng.integers(0, 2, size=(L, L, L, 6), dtype=np.uint8)
    # Ensure they are disjoint initially to avoid exclusion principle violations
    engine.latched_grid[engine.temporal_grid == 1] = 0
    
    # Initialize some timers for latched bits
    engine.timers[engine.latched_grid == 1] = rng.integers(1, 6, size=np.sum(engine.latched_grid == 1))

    initial_total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
    print(f"  Initial temporal bits : {int(engine.temporal_grid.sum())}")
    print(f"  Initial latched bits  : {int(engine.latched_grid.sum())}")
    print(f"  Initial total bits    : {initial_total_bits}")

    conserved = True
    for step_idx in range(1, 51):
        engine.step()
        current_total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
        if current_total_bits != initial_total_bits:
            print(f"  [ERROR] Bit count changed at step {step_idx}: {current_total_bits} vs {initial_total_bits}")
            conserved = False
            break

    if conserved:
        print(f"  [SUCCESS] Bit count is perfectly conserved across 50 steps!")
    else:
        raise AssertionError("Bit conservation check failed!")

    # 2. Shapiro Delay
    print("\n[2] Running Shapiro Delay tests on a 32x32x32 grid...")
    latch_dur = 10
    thresh = 5.0
    mass_val = 10.0
    shapiro_results = measure_shapiro_delay(latch_duration=latch_dur, threshold=thresh, mass_value=mass_val)
    
    print("  Impact Parameter (b) | Coordinate Time (Steps) | Shapiro Delay (Steps)")
    print("  " + "-" * 55)
    vacuum_time = 31  # Theoretical vacuum propagation time
    for b, steps in sorted(shapiro_results.items()):
        delay = steps - vacuum_time
        print(f"  {b:^20} | {steps:^23} | {delay:^21}")

    # Verifications
    assert shapiro_results[0] > shapiro_results[1], "Shapiro Delay is not larger at b=0 than b=1!"
    assert shapiro_results[1] > shapiro_results[2], "Shapiro Delay is not larger at b=1 than b=2!"
    assert shapiro_results[2] == vacuum_time, f"Expected no delay at b=2, but got {shapiro_results[2]} steps"
    print("  [SUCCESS] Shapiro Delay confirms coordinate time dilation correctly!")

    # 3. Dijkstra Fermat Pathfinding and Light Bending
    print("\n[3] Running Dijkstra Fermat Pathfinding & Deflection demonstration...")
    # Vacuum run
    engine_vac = LatchingEngine(L=32, latch_duration=10, threshold=5.0)
    # Start at (0, 16, 16)
    start_node = (0, 16, 16)
    path_vac = run_dijkstra_pathfinding(engine_vac, start_node)
    defl_vac = get_path_deflection(path_vac, start_node, 32)
    print(f"  Vacuum shortest path length : {len(path_vac) - 1}")
    print(f"  Vacuum path deflection      : {defl_vac}")
    assert defl_vac == 0, f"Vacuum path should be straight, but has deflection {defl_vac}"

    # Gravity run
    engine_grav = LatchingEngine(L=32, latch_duration=10, threshold=5.0)
    engine_grav.permanent_mass[16, 16, 16] = 10.0
    path_grav = run_dijkstra_pathfinding(engine_grav, start_node)
    defl_grav = get_path_deflection(path_grav, start_node, 32)
    print(f"  Gravity shortest path length: {len(path_grav) - 1}")
    print(f"  Gravity path deflection     : {defl_grav}")
    print(f"  Gravity path sample (middle): {path_grav[L//2 - 2 : L//2 + 3]}")
    
    assert defl_grav > 0, "Gravity path did not show any spatial deflection (light bending)!"
    print("  [SUCCESS] Dijkstra Fermat pathfinding demonstrates coordinate light bending!")
    print("\n" + "=" * 72)
    print("ALL TESTS PASSED SUCCESSFULLY!")
    print("=" * 72)


if __name__ == "__main__":
    run_self_tests()
