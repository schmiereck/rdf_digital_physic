Create a new Python module `src/engine_d4_latching.py` that implements a 3D+1 D4 Spacetime LGCA with the local latching/trapping mechanism as described in the Strategic Director's Notes.

Key requirements:
1. Class `LatchingEngine` that manages:
   - `L`: grid size (e.g. 32 or 64).
   - `temporal_grid`: np.ndarray of shape (L, L, L, 6) for 6 temporal channels.
   - `latched_grid`: np.ndarray of shape (L, L, L, 6) for latched/trapped bits.
   - `timers`: np.ndarray of shape (L, L, L, 6) for latch delay countdown.
   - `permanent_mass`: np.ndarray of shape (L, L, L) representing a static mass well.
   - `latch_duration` (N) and `threshold` (M_threshold) as parameters.
2. Implement local mass density computation:
   - For each cell (x, y, z), local density M is the sum of bits in the cell itself (temporal + latched) plus its permanent mass, smoothed by summing with its 6 nearest spatial neighbors.
3. Implement `step()`:
   - Decrement active timers for latched bits; when they reach 0, release them back to the temporal grid in the same channel.
   - Compute local density.
   - Trapping: if density >= threshold, any unlatched temporal bit is moved to the latched grid, and its timer is set to `latch_duration` (released bits are exempted in the current step to avoid infinite traps).
   - Apply standard O_h symmetric collision on remaining temporal bits (identity for weight 1).
   - Stream temporal bits.
4. Add a test function to measure Shapiro Delay:
   - Setup a permanent mass at the center of a 32x32x32 grid.
   - Launch a single temporal bit (light pulse) from X = 0 to X = 31 at different Y impact parameters.
   - Measure the exact coordinate time (number of steps) to reach the target.
   - Verify that coordinate time is larger (positive Shapiro delay) for paths passing closer to the mass.
5. Add a function that runs Dijkstra Fermat pathfinding on the emergent latency field (link weight = 1 + latching_delay) to show coordinate light bending (deflection).
6. Run a self-test when the file is executed to verify conservation of bit count and output Shapiro delay numbers.