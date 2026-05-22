Write and execute a python script `src/sweep_two_body_attraction.py` to run a comprehensive parameter sweep for the two-body mutual attraction.

The script must:
1. Load the LUT-08 glider from `archive/iter_224/results/glider_00_lut08_sub03.json` and the self-field profiling results from `archive/iter_237/results/self_field_profiling.json`.
2. Implement the `AbsorbingClosedLoopLatchingEngine` with L=64, where active bits entering the margin (margin=2) are cleanly set to 0 to prevent any toroidal wrap-around.
3. Set up the parameter sweep:
   - Initial separations: S_Y in [4, 5, 6] (launch parallel gliders at X1=X2=12, Z1=Z2=4, and Y1=32 - S_Y/2, Y2=32 + S_Y/2)
   - sigma: [1.0, 1.5, 2.0, 2.5]
   - gamma: [0.90, 0.95]
   - eta: [2.0, 4.0]
   - threshold ratio R: [1.1, 1.3, 1.5, 1.7] (where threshold = R * P_max)
4. For each configuration, run the active simulation for T=50 steps.
5. Filter for STABILITY:
   - Perfect bit conservation (total active + latched bits = 8) across all 50 steps.
   - Both gliders must retain exactly 4 bits (use partition_split to separate cells into Glider 1 or Glider 2 and check that both partitions have exactly 4 bits at every step).
6. For stable configurations, compute:
   - The initial Y-separation: S_Y
   - The final Y-separation at step 50: S_Y_final
   - The deflection: D = S_Y - S_Y_final
7. For stable configurations with deflection D != 0, run a matched Vacuum Control run with eta = 0.0 (vacuum control) and verify its deflection D_vac is approximately 0.0 (and record D_net = D - D_vac).
8. Save a complete list of all tested configurations (both stable and unstable, with stability flags, deflection values, and fail reasons if any) to `archive/iter_237/results/two_body_sweep_results.json`.
9. Print a beautifully formatted summary table of the top 10 stable configurations with the largest positive D_net (genuine mutual attraction) and write a short summary of the findings to stdout.