Write and execute the Two-Body Cavendish Parameter Sweep script at `src/explore_two_body_attraction.py`.

The script must perform the following tasks:
1. Load the stable 4-bit 3D glider (LUT-08) from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Implement a parameter sweep over:
   - alpha in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
   - threshold in [0.4, 0.6, 0.8, 1.0, 1.2]
   - gamma in [0.05, 0.1, 0.15]
   - kappa in [0.02, 0.05, 0.08]
   - eta in [0.5, 1.0, 1.5, 2.0]
   Keep cutoff_radius = 4.
3. For each parameter set:
   - Create a `ClosedLoopLatchingEngine` on a 32x32x32 toroidal grid.
   - Seed Glider 1 at cx=16, cy=13, cz=16 and Glider 2 at cx=16, cy=19, cz=16.
   - Simulate for 80 steps.
   - At each step, verify:
     a) Total active bits (temporal + latched) on the grid is exactly 8 (perfect bit conservation).
     b) Split partition count: Glider 1 partition (closest toroidal distance of Y to 13) has exactly 4 bits, and Glider 2 partition (closest toroidal distance of Y to 19) has exactly 4 bits. If any of these are violated, mark the configuration as UNSTABLE, break immediately, and discard.
   - If stable, calculate:
     - Final unwrapped Y-centroids of both gliders.
     - Deflections: defl_Y1 = Y1_final - 13.0, defl_Y2 = Y2_final - 19.0.
     - Mutual attraction: defl_Y1 - defl_Y2 (should be positive for attraction).
4. Identify the best configuration (maximizing mutual attraction while maintaining perfect structural stability).
5. Run a longer simulation (120 steps) for this best configuration to verify that stability is sustained and deflection continues to grow.
6. Write a beautifully formatted summary table of the top 10 stable configurations.
7. Save the results, trajectories, and summary JSON to `archive/iter_233/results/closed_loop_attraction.json` (ensure `archive/iter_233/results/` exists).
8. Print the full output so it is captured in stdout.