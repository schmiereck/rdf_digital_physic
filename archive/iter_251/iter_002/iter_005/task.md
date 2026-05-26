Task: Perform 12-channel control search, Candidate Analysis (T1, T3, F5), and write the final reports.

Specifically, write and execute a Python script `src/complete_experiment.py` that:
1. Runs the 12-channel control search using multiprocessing (e.g., multiprocessing.Pool) over the 100 control LUTs to make it complete in seconds/minutes, and successfully saves the results to `archive/iter_251/results/control_results.json`.
2. Reads `archive/iter_251/results/search_results.json` and filters the top 10 candidate (LUT, seed) pairs that:
   - Survive 300 steps with `bit_stability == 1`
   - Have net motion (`displacement_norm > 1.0`)
3. For these top candidates, executes:
   - T1 (Single-bit decomposition test): Runs the simulation with each constituent bit removed individually. Compares the trajectory of the remaining bits. If the behavior/trajectory of the remaining bits is independent of the removed bit, then they are non-interacting composites (verdict: F2 triggered).
   - T3 (O_h covariance test): Rotates the seed under all 48 O_h symmetries, runs the simulation, and checks if the trajectory rotates covariantly.
   - F5 (Active channel mixing): Checks if the rest channel occupancy (ch12) is dynamically active (i.e. oscillates and transitions between 0 and other values, and rest bits change position).
4. Analyzes if ANY genuine glider with binding energy > 0 (T1 passed, T3 passed, F5 passed) is found.
5. Writes the final `archive/iter_251/results/experiment_report.json` with all fields:
   - total_runs: total tested (LUT, seed) pairs
   - candidates_surviving_200steps: count
   - candidates_passing_T1: count  
   - candidates_passing_T3: count
   - candidates_passing_F5: count
   - f1_triggered: bool (no multi-bit configuration survives >= 200 steps)
   - f2_triggered: bool (all survivors fail single-bit decomposition)
   - f3_triggered: bool (any discovered glider fails O_h covariance)
   - f4_triggered: bool (12-channel control produces gliders at same rate)
   - f5_triggered: bool (rest channel not dynamically active)
   - verdict: string summarizing findings
   - positive_control_passed: bool
   - 12ch_control_glider_count: int
   - best_candidate: dict or null

Run the script and output its print statements and final results. Let's see the scientific truth!