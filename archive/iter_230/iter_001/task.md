Create a new engine file `src/engine_d4_dynamic.py` that implements a fully dynamic 3D+1 D4 Spacetime LGCA.
In this engine, there is no permanent static mass. Spacetime coordinate latency (latching) is driven purely by the moving bits themselves.
The class `DynamicLatchingEngine` should:
1. Accept grid size `L`, coupling constant `alpha`, threshold `threshold`, and optionally `exponent` (default 1.0) and `lut_seed` (default 1).
2. Maintain `temporal_grid`, `latched_grid`, and `timers` of shape (L, L, L, 6).
3. Implement `compute_local_density()` which calculates the local active bit density (sum of temporal + latched bits) in each cell, smoothed with its 6 nearest spatial neighbors using periodic boundaries (periodic roll).
4. Implement `step()`:
   a. Timer decrement and release: release expired latched bits back to `temporal_grid` if the target temporal channel is empty. If blocked, keep the timer at 1.
   b. Compute updated local density field M.
   c. Trapping: for any cell with M >= threshold, trap incoming temporal bits (except those just released in this step) into the `latched_grid`, setting their timers to `round(alpha * (M ** exponent))` (ensure at least 1 step duration). If the target latched channel is occupied, trapping is blocked.
   d. Collision: apply the Oh symmetric LUT on remaining temporal bits.
   e. Stream: stream temporal bits using the 6 Shifts.
5. Perfect bit conservation: total bit count (temporal + latched) must remain perfectly invariant across steps.
Include a self-test suite within `src/engine_d4_dynamic.py` that asserts perfect bit conservation over 50 steps on a randomized initial grid.