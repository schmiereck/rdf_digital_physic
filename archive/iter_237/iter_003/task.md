Create and execute a python script `src/analyze_sweep_and_check_symmetry.py` to analyze the sweep results, run symmetry checks on the best configuration, and evaluate the falsification criteria.

The script must:
1. Load `archive/iter_237/results/two_body_sweep_results.json`.
2. Check if the sweep completed (how many configurations are in the file). If the file is incomplete or was truncated due to timeout, the script should run any missing configurations from the 192-config sweep on the fly using the precomputed engine and append them to ensure a 100% complete and valid dataset.
3. Identify all stable configurations with positive net deflection (D_net > 0.0).
4. For the best stable configuration (or the top configurations if they exist):
   - Run an 80-step simulation of the active run and matched vacuum control run.
   - Print the Y-centroids of both gliders and their separation every 10 steps.
   - Apply the Falsification Protocol symmetry check: rotate the initial conditions (glider states and velocities) by 90 degrees around the Z-axis using the O_h symmetry group. Run the rotated simulation (active and vacuum) and check if the net mutual deflection in the rotated coordinate direction matches the unrotated net deflection within 15%.
5. If no stable configuration with positive deflection survives the falsification check, or if no stable configs exist, document a first-class null result explaining why the current closed-loop coordinate latency model is dispersive or cannot sustain mutual attraction at this scale without causing structural breakup.
6. Write a comprehensive summary report `archive/iter_237/results/mutual_attraction_report.md` with all findings, tables, and the final scientific verdict.