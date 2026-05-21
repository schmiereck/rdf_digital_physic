#!/usr/bin/env python3
"""
test_engine_3d.py — Verification and test suite for the 3D Cuboctahedron LGCA engine.
"""

import sys
import os
import numpy as np

# Add src to the path if needed
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from engine_3d import (
    SHIFTS,
    pack,
    unpack,
    stream,
    collide,
    invert_lut,
    generate_bit_conserving_lut,
    verify_reversibility,
    verify_bit_conservation,
)

def test_coordinate_shifts():
    print("=== Testing Coordinate Shifts and Streaming Directions ===")
    # Create an empty grid with shape (5, 5, 5, 12)
    grid = np.zeros((5, 5, 5, 12), dtype=np.uint8)
    
    # Place a particle in each channel at the center cell (2, 2, 2)
    for i, (dl, dr, dc) in enumerate(SHIFTS):
        grid[2, 2, 2, i] = 1
        
    # Stream one step forward
    streamed = stream(grid, reverse=False)
    
    # Verify that each particle moved to the correct destination
    for i, (dl, dr, dc) in enumerate(SHIFTS):
        expected_l = (2 + dl) % 5
        expected_r = (2 + dr) % 5
        expected_c = (2 + dc) % 5
        
        # Check that the particle is at the expected destination
        assert streamed[expected_l, expected_r, expected_c, i] == 1, \
            f"Channel {i} failed to stream to ({expected_l}, {expected_r}, {expected_c})"
        # Verify that it is nowhere else in this channel
        streamed_channel_sum = streamed[..., i].sum()
        assert streamed_channel_sum == 1, \
            f"Channel {i} has unexpected extra or missing bits (sum: {streamed_channel_sum})"
            
    print("Coordinate shifts and streaming directions: PASS")


def test_pack_unpack_cycle():
    print("=== Testing Pack and Unpack Cycle ===")
    # Generate random grids of different sizes
    sizes = [(4, 4, 4), (8, 6, 10), (16, 16, 16)]
    for size in sizes:
        shape = size + (12,)
        grid = np.random.randint(0, 2, size=shape, dtype=np.uint8)
        
        packed = pack(grid)
        assert packed.shape == size, f"Packed shape mismatch: {packed.shape} vs {size}"
        assert packed.dtype == np.uint16, f"Packed dtype mismatch: {packed.dtype} vs np.uint16"
        
        unpacked = unpack(packed)
        assert unpacked.shape == shape, f"Unpacked shape mismatch: {unpacked.shape} vs {shape}"
        assert unpacked.dtype == np.uint8, f"Unpacked dtype mismatch: {unpacked.dtype} vs np.uint8"
        
        assert np.array_equal(grid, unpacked), f"Pack/unpack cycle failed for shape {shape}"
        
    print("Pack/unpack cycle: PASS")


def test_reversibility_and_conservation():
    print("=== Testing Reversibility and Bit Conservation ===")
    np.random.seed(42)
    
    # Generate 5 random grids and 5 random bit-conserving LUTs
    for test_idx in range(5):
        grid = np.random.randint(0, 2, size=(6, 6, 6, 12), dtype=np.uint8)
        lut = generate_bit_conserving_lut(seed=test_idx)
        
        # Verify reversibility
        rev_ok = verify_reversibility(grid, lut)
        assert rev_ok, f"Reversibility verification failed on trial {test_idx}"
        
        # Verify bit conservation
        cons_ok = verify_bit_conservation(grid, lut)
        assert cons_ok, f"Bit conservation verification failed on trial {test_idx}"
        
    print("Reversibility and Bit Conservation: PASS")


def test_multi_step_simulation():
    print("=== Testing Multi-Step Simulation Consistency ===")
    # Initialize a random grid
    grid = np.random.randint(0, 2, size=(8, 8, 8, 12), dtype=np.uint8)
    lut = generate_bit_conserving_lut(seed=999)
    inv_lut = invert_lut(lut)
    
    initial_bits = int(grid.sum())
    current_grid = grid.copy()
    
    # Record history to verify reversibility backwards
    history = [current_grid.copy()]
    
    # Run 10 steps of stream and collide
    for step in range(1, 11):
        # 1. Stream
        current_grid = stream(current_grid)
        # 2. Collide
        current_grid = collide(current_grid, lut)
        
        # Save history
        history.append(current_grid.copy())
        
        # Check bit conservation at each step
        current_bits = int(current_grid.sum())
        assert current_bits == initial_bits, \
            f"Bit count changed at step {step}: expected {initial_bits}, got {current_bits}"
            
    print("Bit conservation over 10 steps: PASS")
    
    # Reverse the simulation from the final step back to the start
    for step in range(10, 0, -1):
        state = history[step]
        # To reverse: first invert collide, then invert stream
        uncollided = collide(state, inv_lut)
        unstreamed = stream(uncollided, reverse=True)
        
        expected_prev_state = history[step - 1]
        assert np.array_equal(unstreamed, expected_prev_state), \
            f"Reversal failed when going from step {step} back to {step - 1}"
            
    print("Reversibility over 10 steps (backward propagation): PASS")


def main():
    try:
        test_coordinate_shifts()
        test_pack_unpack_cycle()
        test_reversibility_and_conservation()
        test_multi_step_simulation()
        print("\nALL TESTS PASSED SUCCESSFULLY! The 3D Cuboctahedron LGCA engine is fully correct and verified.")
    except AssertionError as e:
        print(f"\nTEST FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
