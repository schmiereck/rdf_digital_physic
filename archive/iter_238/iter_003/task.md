Write and execute a Python script `src/evaluate_attraction.py` to evaluate our pre-registered falsification criteria against the 192-configuration sweep results from iter_237.

The script must:
1. Load the completed sweep results from `archive/iter_237/results/two_body_sweep_results.json`.
2. Locate the pre-registered configuration in the sweep data:
   - S_Y = 5, sigma = 1.5, gamma = 0.9, eta = 2.0, R = 1.1.
   - Read its stability, final separation, and net deflection.
3. Locate the best sweep configuration:
   - S_Y = 5, sigma = 2.0, gamma = 0.95, eta = 2.0, R = 1.1.
   - Read its stability, final separation, and net deflection.
4. Run short verification simulations (using `AbsorbingClosedLoopLatchingEngine` from `src/sweep_two_body_attraction.py` on an L=64 grid) for:
   - The pre-registered configuration (both active eta=2.0 and vacuum eta=0.0).
   - The best sweep configuration (both active eta=2.0 and vacuum eta=0.0).
   - Verify that bit conservation is perfectly preserved (exactly 8 bits) across all 50 steps.
   - Verify that neither active bits nor the latency field at the boundaries (index < 2 or index >= 62) exceeds 1e-5.
   - Run matched rotated runs (using the O_h symmetry group transformation for permutation g=10, 90-degree stack rotation) to check rotational covariance.
5. Evaluate all 4 pre-registered falsification criteria:
   - Criterion 1 (Deflection Failure): Is d_vacuum_min - d_active_min >= 2.0 lattice units?
   - Criterion 2 (Anisotropy / Lack of Symmetry Covariance): Does the final deflection differ by more than 15% between g=0 and g=10?
   - Criterion 3 (Boundary Leak): Did any glider or latency field > 1e-5 touch the boundaries?
   - Criterion 4 (Bit Conservation): Was bit conservation violated?
6. Write a comprehensive summary JSON to `archive/iter_238/results/non_periodic_summary.json`.
7. Write the official Scientific Report to `archive/iter_238/results/non_periodic_attraction_report.md` with sections:
   - Pre-Declared Hypothesis & Falsification
   - Experimental Protocol
   - Trajectory Observations (Active vs Vacuum, Rotated)
   - Falsification Audit & Verdict
   - Construction-vs-Empirical Notes & Scientific Limitations.

Verify that the script runs successfully, print its output, and list all generated files in your response. Do NOT attempt to spawn any sub-agents or use any recursive planners.