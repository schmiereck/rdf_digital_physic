Design and execute a systematic parameter exploration script `src/explore_two_body_attraction.py` to demonstrate the "Two-Body Cavendish Test" (Mutual Deflection) using the `ClosedLoopLatchingEngine`.

The goals are:
1. Seed two parallel stable 4-bit 3D gliders (LUT-08) at cy=13 and cy=19 (separation of 6.0 in Y, grid size L=32).
2. Measure vacuum control trajectories (they should have constant Y centroid, perfect bit conservation of 8 bits).
3. Search/sweep parameters (alpha, threshold, gamma, kappa, eta, cutoff_radius=4) to find a regime where:
   - Both gliders remain structurally stable and perfectly conserve bit count (exactly 8 bits total, 4 bits in each partition).
   - They exhibit mutual deflection: Glider 1 deflecting upwards (+Y) and Glider 2 deflecting downwards (-Y), reducing their mutual separation.
   - Characterize the best configuration: report the maximum mutual deflection, the parameters used, and how it scales over steps (up to 120 steps).
4. Save the results, trajectories, and a summary to `archive/iter_233/results/closed_loop_attraction.json`. Make sure you print a beautifully formatted summary table.