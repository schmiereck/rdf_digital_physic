Write and execute a Python script `src/non_periodic_attraction.py` to run the non-periodic mutual attraction experiment on an L=64 grid, strictly following our pre-registered hypothesis and falsification criteria in `src/pre_registration.md`.

The script must:
1. Define `NonPeriodicClosedLoopLatchingEngine` as a subclass of `ClosedLoopLatchingEngine` from `src/engine_d4_closed_loop_v2.py`.
   - Implement the zero-padded 3D FFT Gaussian potential solver by padding the L x L x L density/charge grid to 2L x 2L x 2L with zeros before performing FFT, multiplying by the Gaussian blur kernel, performing inverse FFT, and cropping back to L x L x L.
   - Implement absorbing boundary conditions with a margin of 2, zeroing out active bits in the boundaries at the start of each step.
   - Track and log whether any active bits or the latency field (with a threshold of 1e-5) touched the boundaries of the grid during the run.

2. Load the LUT-08 sub-light glider configuration from `archive/iter_224/results/glider_00_lut08_sub03.json`.
3. Set up two parallel gliders near the center of the L=64 grid:
   - Initial positions: (12, 30, 8) and (12, 35, 8). This is a separation of 5.0 along the Y-axis.
   - This ensures the gliders (propagating in the X-Z plane with velocity v_z = 1.0, v_x = 0.5) remain completely inside the [2, 62] range for T = 50 steps, avoiding boundary collisions.
   - Define a function to partition active bits into two gliders and compute their Y-centroids and mutual Y-separation.

4. Run the following simulation groups for T = 50 steps:
   Group A: Pre-registered configuration (sigma = 1.5, gamma = 0.90, eta = 2.0)
     - Active run (with threshold = 1.1 * P_max = 1.1 * 0.1670116 = 0.1837128)
     - Vacuum control (eta = 0.0)
     - Rotated Active & Vacuum runs: Apply O_h rotations g=0 and g=10 (90-degree layer stacking rotation) using get_oh_permutations and project onto the rotated separation axis.
   Group B: Best sweep configuration (sigma = 2.0, gamma = 0.95, eta = 2.0)
     - Active run (with threshold = 1.1 * P_max = 1.1 * 0.0901136 = 0.0991249)
     - Vacuum control (eta = 0.0)
     - Rotated Active & Vacuum runs under g=0 and g=10.

5. Measure and save the separation distance d(t) at every step.
6. Evaluate all 4 pre-registered falsification criteria:
   - Criterion 1: d_vacuum_min - d_active_min >= 2.0 lattice units.
   - Criterion 2: Rotational covariance (isotropy) - difference in separation trajectory between g=0 and g=10 is <= 1.75 lattice units, and final deflection difference is <= 15%.
   - Criterion 3: Boundary leak - confirm that no active bits or latency field > 1e-5 touched the boundaries.
   - Criterion 4: Bit conservation - confirm that total active + latched bits is exactly 8 at every single step.

7. Write a beautifully structured markdown report `archive/iter_238/results/non_periodic_attraction_report.md` summarizing the findings, and save a summary JSON to `archive/iter_238/results/non_periodic_summary.json`.

Execute this script and print out its stdout and key metrics.