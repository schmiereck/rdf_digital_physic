Create and execute a python script `src/profile_and_preregister.py` to analyze the single-glider self-potential field (to resolve the sigma-dilution problem) and write the official Pre-Registration document.

The script must:
1. Load the LUT-08 glider from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Configure a `ClosedLoopLatchingEngine` on a 64x64x64 grid with absorbing boundaries (margin=2, where any bit entering the margin is set to 0 to prevent toroidal wrap-around).
3. Sweep over parameters:
   - sigma: [1.0, 1.5, 2.0, 2.5]
   - gamma: [0.80, 0.90, 0.95]
   - eta: [1.0, 2.0, 4.0]
4. For each parameter set, simulate a single glider in vacuum (with trapping threshold set to a very high value like 999.0 to ensure no self-trapping) for 60 steps.
5. Record the peak value of the latency field `latency_field` across steps 30-60 (steady state). This represents the glider's peak self-potential P_max.
6. Verify that if threshold is set to a value slightly above P_max (e.g., 1.1 * P_max), the glider propagates with perfect structural stability and zero self-trapping.
7. Write the results of this profiling to `archive/iter_237/results/self_field_profiling.json`.
8. Write the official Pre-Registration markdown file to `archive/iter_237/pre_registration.md` outlining:
   - Working Hypothesis: Overlapping of latency fields allows two gliders to mutually attract and deflect each other without self-trapping when P_max < threshold < 1.8 * P_max.
   - Matched Vacuum Control: eta = 0.0.
   - Boundary Hygiene: L=64, absorbing boundaries (margin=2) to eliminate torus wrap-around recurrence.
   - Explicit Falsification Criteria:
     - Refuted if the active runs do not show a mutual approach in Y that is at least 2.0 lattice units greater than the vacuum control by step 80.
     - Refuted if the glider breaks up or violates bit conservation (4 bits per glider).
     - Refuted if rotating initial conditions by 90 degrees around Z-axis changes deflection by more than 15%.