We want to perform a systematic parameter sweep of gravitational lensing on our 3D+1 D4 discrete spacetime.

Please do the following:
1. Create a script named `src/d4_lensing_sweep.py` that implements the parameter sweep, Markdown and JSON reporting, and 2D matplotlib plotting as planned.
2. The script must:
   - Import functions from `src/d4_lensing.py`.
   - Run Dijkstra lensing simulations on D4 for impact parameters b in [2.0, 4.0, 6.0] and potentials A_grav in [1.0, 3.0, 5.0].
   - Calculate coordinate times, Shapiro delays, and deflection angles.
   - Plot the trajectories in the X-Y plane using matplotlib. Add the background potential U_grid centered at (0,0) as a colored reference shade. Save the plot to `archive/iter_227/results/d4_lensing_paths.png`.
   - Save a JSON report to `archive/iter_227/results/lensing_sweep_report.json`.
   - Save a Markdown report to `archive/iter_227/results/lensing_sweep_report.md`.
3. Execute `python src/d4_lensing_sweep.py`.
4. Verify that all output files are successfully created and non-empty.
5. Return `src/d4_lensing_sweep.py`, `archive/iter_227/results/d4_lensing_paths.png`, `archive/iter_227/results/lensing_sweep_report.json`, and `archive/iter_227/results/lensing_sweep_report.md` in your final artifacts list. Do not use mock data. Ensure proper execution in this Windows environment.