We have discovered that with wide Gaussian smoothing ($\sigma = 2.5$), the self-generated latency field is too flat at an initial separation of 6 cells to produce a sufficient gradient for asymmetric Zitterbewegung deflection. 

To overcome this, we will write and run `src/explore_two_body_attraction_v5.py` to test whether reducing the initial separation (to 4 or 5 cells) and tuning the parameters can successfully generate non-zero, stable mutual deflection that continues to grow over a longer horizon.

1. Implement a script `src/explore_two_body_attraction_v5.py` using `ClosedLoopLatchingEngine` from `src/engine_d4_closed_loop_v2.py`.
2. Load the LUT-08 sub-light glider configuration.
3. Test three initial Y-separations:
   - 4 cells (CY1=14, CY2=18, initial separation = 4.0)
   - 5 cells (CY1=13, CY2=18, initial separation = 5.0)
   - 6 cells (CY1=13, CY2=19, initial separation = 6.0)
4. For each separation, run a parameter sweep over:
   - `alpha`: [2.0, 3.0, 4.0]
   - `threshold`: [0.015, 0.025, 0.035, 0.045]
   - `gamma` (retention): [0.90, 0.95]
   - `eta`: [2.0, 4.0, 6.0, 8.0]
   - `sigma` = 2.5 (fixed)
5. Reject any configuration that violates bit conservation (total active bits must be exactly 8) or causes glider breakup (active cells per glider > 16, or total active cells > 32).
6. Measure mutual deflection at step 80 (initial separation - final separation, computed from unwrapped centroids).
7. Print a summary table of the best stable configurations (with deflection > 0) for each separation.
8. For the overall best configuration, run a long-term validation run (160 steps) and a corresponding Vacuum Control run (`eta = 0.0`), printing a table of the centroids and mutual deflection every 10 steps, and check if the deflection grows over time.
9. Save the summary to `archive/iter_234/results/dynamic_attraction_v5_summary.json`.