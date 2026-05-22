Implement and run the Phase 5.4: N-Body Stability systematic experiments on the 3D+1 D4 projected lattice.

Follow the Methodological Discipline and Manager's Note:
1. Write a pre-registration section in your report and script.
2. Maintain parameter-tuning hygiene: keep the physics envelope fixed at the baseline parameters established in Phase 5.3:
   L = 64 (or 32, whichever is best for the study), gamma = 0.90, eta = 2.0 (for active) and 0.0 (for control), threshold = 0.045, alpha = 2.0, sigma = 2.5, using the same LUT-08 glider.
3. Formulate three-body and four-body configurations:
   - A hierarchical 3-body system: a tight binary (similar to iter_235) plus a third glider placed further away.
   - A 4-body system (e.g., a double binary or hierarchical 4-body).
4. Run active vs. vacuum control simulations side-by-side for at least 160 steps.
5. Perform an Oh symmetry and lattice anisotropy check: test the configurations under at least two distinct rotations (Permutation 0 and Permutation 10 or 21).
6. Track the positions of each glider over time. Write a simple, self-contained K-means clustering algorithm in python to partition the active grid bits (which total 12 for N=3 and 16 for N=4) into individual gliders at each step. This avoids external library issues.
7. Compute and log:
   - Individual glider coordinates and distance from the system barycenter.
   - Total bit count (should remain exactly 4 * N if bit-conserving, or document if any latching merger happens).
   - Average and max dispersion over steps.
8. Perform an Escape Velocity probe: vary the initial distance/displacement of the third glider and classify the outcome as Captured, Escaped, or Latching/Collapse.
9. Save the data logs and a comprehensive markdown report (incorporating pre-registration, protocol, observations, and honest null/positive verdicts) under `archive/iter_236/results/nbody_stability_report.md` (and other data files).
10. Ensure the report is written in highly rigorous, objective, non-promotional language.