Continue Step 3-5 of Iteration 253.

First, let's fix the variable shadowing bug in `src/totalistic_ga.py`.
Locate where `f` is assigned to `evaluate_rule(B, S, seeds)` inside `with open(GA_CSV, "w", newline="") as f:` (e.g., around lines 265, 296, 344), and rename `f` to `fit_val` (or similar).
This is critical so that `f.flush()` is called on the file object and does not crash with `AttributeError: 'float' object has no attribute 'flush'`.

Once the bug is fixed:
1. RUN EVOLUTIONARY GA:
Run `PYTHONPATH=. python3 src/totalistic_ga.py` to search for candidate rules.
The GA should run for generations/evaluations and track unique rules evaluated. We want the total number of unique rules evaluated across the sweep (which was 200) plus the GA to be at least 10,000 rules.
Make sure `ga_results.csv` and `ga_summary.json` are written correctly under `archive/iter_253/results/`.

2. WRITE AND EXECUTE COHERENCE TESTING:
Create `src/glider_coherence_test.py` to verify if any of the candidate rules discovered in Step 2 (Sweep) or Step 3 (GA) pass all the F1-F6 falsification criteria.
Since Step 2 found 0 candidate rules, check if Step 3 (GA) finds any candidate rules (i.e. rules with fitness > 0 on the GA seed suite).
If GA finds any candidate rules:
For each candidate rule:
  Test it on all 46 sweep seeds to find any combinations that pass the sweep filters:
    - Survival: survives >= 300 steps.
    - Displacement: net displacement >= 5.0.
    - Bounding box: bounding extent <= 10 after step 100.
    - Bloom check: bit count <= 4x initial seed weight after step 100.
    - Cooperative survival: single-bit seed at (20,20,20) dies within <= 50 steps.
  For any rule+seed combination passing those filters, run Coherence Testing:
    - Single-Bit Decomposition Test (F2): Verify that a single-bit seed under this rule dies in <= 50 steps.
    - O_h Covariance Test (F3): Load the 48 O_h transforms using `build_oh_transforms()` from `src/rigorous_glider_audit.py`. Rotate the seed coordinates relative to (20,20,20) using each transform's `M_g` matrix. Verify that all 48 rotations of the seed survive, propagate (displacement >= 5), and do not bloom (<= 4x initial bits after step 100) or shed debris (bounding box <= 10 after step 100).
    - Bloom and Debris recheck (F5, F6): Verify bit count <= 4x initial and bounding extent <= 10 after step 100.
    - Full 300-step run: Verify survival >= 300 steps with net displacement >= 5.0.
  Save results to `archive/iter_253/results/coherence_results.csv`: columns = `rule_str, seed_id, decomposition_pass, oh_covariance_pass, bloom_pass, debris_pass, full_pass`.

If NO candidates pass all tests (from either sweep or GA), then coherence_results.csv can be empty or list evaluated rules that failed, and we report a FIRST-CLASS NULL RESULT.

3. DOCUMENTATION:
Create `archive/iter_253/results/summary.json` containing:
- `verdict`: "supported" (if at least one glider passed all tests) or "refuted" (if all failed).
- `total_rules_tested`: total number of unique rules evaluated across sweep and GA (should be >= 10,000).
- `candidates_found`: number of candidates passing sweep/GA filters.
- `candidates_passing_coherence`: number of candidates passing all coherence tests.

If this is a null result, write a beautifully detailed scientific write-up in the final summary of what you did and analyze the totalistic phase space on the FCC lattice (how lambda values relate to rapid death, localization, explosion, stationary still-lives, etc.), using the generated data in `phase_diagram.csv` and `ga_results.csv`.

Let's execute this cleanly.