Write and execute a systematic parameter exploration script `src/explore_two_body_attraction.py` to demonstrate the "Two-Body Cavendish Test" (Mutual Deflection) using the `ClosedLoopLatchingEngine`.

### Requirements:
1. **Load Glider**: Load the stable 4-bit 3D glider from `archive/iter_224/results/glider_00_lut08_sub03.json`. Note its `lut_seed` (which is 8) and `particle` list.
2. **Seeding**: Seed two parallel gliders in a grid of size L=32.
   - Glider 1: Centered at `cx=16, cy=13, cz=16`.
   - Glider 2: Centered at `cx=16, cy=19, cz=16`.
   - This gives an initial separation of exactly 6.0 in Y.
3. **Centroid & Stability Calculation**:
   - At each step, identify all active cells (where `temporal_grid == 1` or `latched_grid == 1`).
   - The engine must have exactly 8 active cells total.
   - Unwrap their Y coordinates relative to 16.0: `unwrapped_y = 16.0 + np.mod(y_vals - 16 + L//2, L) - L//2`.
   - Partition the active cells into:
     - Glider 1: cells with `unwrapped_y < 16.0`
     - Glider 2: cells with `unwrapped_y >= 16.0`
   - Stability check: If the total bits are not 8, or if Glider 1 doesn't have exactly 4 bits, or if Glider 2 doesn't have exactly 4 bits, the configuration is **unstable**. Stop simulating immediately and discard this parameter set.
   - For a stable step, compute each glider's centroid. To handle toroidal boundary crossings of X, Y, Z, unwrap the coordinates of the 4 cells of each glider relative to cell 0 of that glider (the anchor):
     ```python
     def compute_single_centroid(cells):
         anchor = cells[0]
         unwrapped = np.zeros_like(cells, dtype=np.float64)
         for d in range(3):
             unwrapped[:, d] = anchor[d] + np.mod(cells[:, d] - anchor[d] + L//2, L) - L//2
         return np.mean(unwrapped, axis=0)[:3]
     ```
   - To get smooth, continuous trajectories across the entire 120 steps, unwrap the centroids over time:
     ```python
     # At each step t > 0
     step_change_1 = np.mod(c1_toroidal - c1_prev_toroidal + L//2, L) - L//2
     step_change_2 = np.mod(c2_toroidal - c2_prev_toroidal + L//2, L) - L//2
     c1_continuous += step_change_1
     c2_continuous += step_change_2
     ```
   - Compute the separation as `c2_continuous[1] - c1_continuous[1]` and mutual deflection as `6.0 - separation`.
4. **Vacuum Reference Run**:
   - Run the simulation with `eta = 0.0` (all other parameters set to standard values, e.g. `gamma=0.1, kappa=0.05, threshold=1.5, alpha=2.0`) for 120 steps.
   - Verify that both gliders remain perfectly stable and conserve bit count, and that deflection remains exactly 0.0.
5. **Systematic Sweep**:
   - Sweep a grid of parameters:
     - `alpha`: `[1.0, 1.5, 2.0, 3.0]`
     - `threshold`: `[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5]`
     - `gamma`: `[0.05, 0.1, 0.15, 0.2]`
     - `kappa`: `[0.02, 0.05, 0.08, 0.12]`
     - `eta`: `[0.1, 0.2, 0.5, 1.0, 1.5]`
     - `cutoff_radius` is fixed at `4`.
   - Run each simulation up to 120 steps, but abort early if it becomes unstable.
   - Find the parameter set that remains perfectly stable for all 120 steps and achieves the **maximum mutual deflection** (highest value of `deflection` over the 120 steps).
6. **Detailed Evaluation**:
   - Re-run the best parameter set for 120 steps to collect detailed step-by-step continuous centroids, separation, and deflection.
7. **Report & Output**:
   - Print a beautifully formatted summary table comparing the Vacuum Run and the Best Attraction Run at intervals of 10 steps (0, 10, 20, ..., 120).
   - Create directory `archive/iter_233/results/` if it doesn't exist.
   - Save the full results, trajectories, and a summary to `archive/iter_233/results/closed_loop_attraction.json`.
   - The JSON should contain fields: `vacuum_trajectory` (with centroids, deflection, etc.), `best_params`, `attraction_trajectory`, and a summary block.

Write `src/explore_two_body_attraction.py` and run it. Verify it prints the table and saves the json. Do not mock or hallucinate. Use the real python environment.