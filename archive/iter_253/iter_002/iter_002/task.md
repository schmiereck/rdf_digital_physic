Please execute the pre-registered experiment steps 2-5 using the ultra-fast-path optimization for totalistic_ga.py and semi-totalistic analysis:

### Task A: Re-run the GA (src/totalistic_ga.py)
1. Modify `src/totalistic_ga.py`:
   - Set `POP_SIZE = 100` (matches pre-registration)
   - Set `GA_STEPS = 200` (matches pre-registration)
   - Set `GENERATIONS = 30`
   - Modify `evaluate_rule(B, S, seeds)` with the fast-path pre-simulation:
     - Run a fast-path loop first: `g = grid.copy()`, and step it up to `GA_STEPS` steps. If `bc == 0` or `bc > 4 * initial_bits`, record the step.
     - If `exploded` or `survival_time <= 100`, append `0.0` to fitnesses and continue immediately without any COM or extent calculations.
     - Otherwise (if it survives > 100 steps and is not exploded), re-run the full simulation using `simulate(grid, B, S, steps=GA_STEPS)` to compute accurate COMs, extents, and the final fitness score.
     - Use `float(GA_STEPS)` instead of `300.0` when calculating survival_score.
   - Remove the `while total_unique < 10000:` loop.
   - Set results output path to `archive/iter_253/results/ga_results.csv` and `archive/iter_253/results/ga_summary.json`.
2. Run the GA: `python totalistic_ga.py` from the `src/` directory. It should complete in under 30 seconds now!

### Task B: Post-filter with Three-Test Coherence Protocol
- If any candidates are found, apply post-filtering. Otherwise, document that 0 candidates were found (F1 evidence).

### Task C: Positive Control
- Write and run `src/validate_hex_positive_control.py` to:
  1. Load `archive/iter_222/results/champion_rule_perfect.json`.
  2. Create the LUT using `rule_dict_to_lut`.
  3. Seed the L-tromino pattern at `[(63, 63), (64, 63), (64, 64)]`.
  4. Run 200 steps and confirm it propagates at v ≈ 0.469c.
  5. Confirm single-bit decomposition (all 3 isolated bits die).
  6. Save results to `archive/iter_253/results/positive_control.json`.

### Task D: Semi-Totalistic Analysis
- Write and run `src/run_semi_totalistic_analysis.py` to:
  1. Generate 500 random semi-totalistic rules (outer-totalistic B and S sets where B is subset of {1,...,11} and S is subset of {1,...,12}).
  2. Evaluate them using the same `evaluate_rule` (with fast-path optimization) on the 5 seeds.
  3. Save results to `archive/iter_253/results/semi_totalistic_results.json`.

### Task E: Formal Falsification Evaluation
- Evaluate F1-F6 and write `archive/iter_253/results/falsification_report.json`.

Please run the scripts and make sure all results are correctly generated and saved.