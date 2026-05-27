Perform Steps 2-5 of the pre-registered experiment for iteration 253 as detailed below:

### Task A: Re-run the GA (src/totalistic_ga.py)
1. Read and modify src/totalistic_ga.py to:
   - Cap at GENERATIONS=30 (instead of 50).
   - Remove/cap the 'while total_unique < 10000:' loop (the GA must stop after exactly GENERATIONS=30).
   - Reduce GA_STEPS from 300 to 200.
   - Modify the evaluate_rule function to run step-by-step with early death termination (bit_count = 0) and early explosion termination (bit_count > 4 * initial_bits). If bit count exceeds 4 * initial_bits, stop simulation immediately and return minimum fitness (0.0).
   - Change 'survival_score = min(survival_time / 300.0, 1.0)' to use GA_STEPS instead of 300.0.
   - Ensure results (ga_results.csv, ga_summary.json) are written to archive/iter_253/results/.
2. Run the modified GA using: `cd src && python totalistic_ga.py`.

### Task B: Post-filter with Three-Test Coherence Protocol
- If any candidate rule (fitness > 0.01) is found, apply the Single-Bit Decomposition Test, Collision Coherence Test, and O_h Covariance Test.
- If no candidates emerge (most likely given sweep results), formally document this as F1 evidence.

### Task C: Positive Control
- Write and execute a validation script at `src/validate_hex_positive_control.py` that:
  1. Loads 'archive/iter_222/results/champion_rule_perfect.json'.
  2. Reconstructs the 2D hex synchronous CA rule lookup table (LUT).
  3. Seeds the L-tromino pattern at SEED_CELLS = [(63, 63), (64, 63), (64, 64)].
  4. Runs 200 steps and measures velocity (v ≈ 0.469c).
  5. Performs single-bit decomposition (confirms each of the 3 bits alone dies / final bit count = 0).
  6. Saves results to `archive/iter_253/results/positive_control.json`.

### Task D: Semi-Totalistic Analysis
- Write and execute a python script `src/run_semi_totalistic_analysis.py` that:
  1. Searches a random sample of 500 semi-totalistic rules (outer-totalistic B and S sets) on the same seed set.
  2. Applies the same fitness function (with the early termination checks).
  3. Saves results to `archive/iter_253/results/semi_totalistic_results.json`.

### Task E: Formal Falsification Evaluation
- Evaluate all falsification criteria F1-F6 and write a formal falsification report to `archive/iter_253/results/falsification_report.json`.

Ensure all code runs successfully and files are correctly saved in the right directories.