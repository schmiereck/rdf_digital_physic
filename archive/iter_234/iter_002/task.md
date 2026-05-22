Create and execute the python script `src/explore_two_body_attraction_v4.py` to run a refined parameter sweep designed to overcome the spatial dilution of Gaussian smoothing ($\sigma = 2.5$) and demonstrate stable, non-transient emergent mutual attraction between two 3D sub-light gliders.

1. The script should use the new `ClosedLoopLatchingEngine` from `src/engine_d4_closed_loop_v2.py`.
2. Load the stable LUT-08 sub-light glider configuration from `archive/iter_224/results/glider_00_lut08_sub03.json`.
3. Configure a 32x32x32 toroidal grid, launching two parallel gliders at Y=13 and Y=19.
4. Run a parameter sweep:
   - `alpha`: [1.0, 2.0, 3.0, 4.0]
   - `threshold`: [0.015, 0.025, 0.035, 0.045, 0.055, 0.065]
   - `gamma` (retention): [0.90, 0.95]
   - `eta`: [1.0, 2.0, 3.0, 4.0, 5.0]
   - `sigma` = 2.5 (fixed)
5. Reject any configuration that violates bit conservation (total active bits must be exactly 8) or causes glider breakup (active cells per glider > 16, or total active cells > 32).
6. Measure the mutual deflection at step 80 (initial separation - final separation, where final separation is computed from unwrapped centroids).
7. Select the stable configuration that produces the highest stable mutual deflection.
8. Perform a long-term validation run (160 steps) with the selected best configuration, and run a corresponding Vacuum Control run with `eta = 0.0` (no latency deposition) to prove that the deflection is driven purely by the dynamic coordinate-latency field.
9. Track and print a beautifully formatted table showing the positions and mutual deflection of the gliders over the 160 steps in both the Vacuum Control and Active Gravity cases, verifying that the deflection grows over time.
10. Save a comprehensive summary JSON to `archive/iter_234/results/dynamic_attraction_v4_summary.json` containing parameters, trajectories, and a clear success statement.