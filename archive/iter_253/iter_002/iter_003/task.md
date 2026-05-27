Complete steps 3, 4, and 5 of the search pipeline for iteration 253.

We have already completed Step 2 (sweep) which found 0 candidate rules out of 200 rules tested, and we have fixed the variable shadowing bug in `src/totalistic_ga.py`.

Please perform the following tasks:

1. RUN THE EVOLUTIONARY GA (Step 3):
Run `PYTHONPATH=. python3 src/totalistic_ga.py`.
Verify that it runs to completion (generates `archive/iter_253/results/ga_results.csv` and `archive/iter_253/results/ga_summary.json`).
Verify that the total number of unique rules evaluated across sweep + GA is indeed at least 10,000 (the GA script has built-in logic to continue running generations or evaluate random rules to hit >= 10,000 unique rules).

2. CREATE COHERENCE TESTING SCRIPT (Step 4):
Create `src/glider_coherence_test.py`.
The script should:
- Re-generate the 46 standard sweep seeds exactly as done in `src/totalistic_rule_search.py` (Seeds 0 to 45: single bit, bit pairs, L-trominoes, random compact clusters).
- Load candidate rules. A rule is a candidate if:
  - It was identified as a candidate in the Sweep (0 found), OR
  - It is listed in the `candidate_rules` list from `archive/iter_253/results/ga_summary.json` (i.e., has fitness > 0 in the GA).
- For each candidate rule, check which of the 46 seeds survive, propagate, and are compact (using the sweep filters):
  - Survival: survives >= 300 steps.
  - Displacement: net displacement >= 5.0.
  - Bounding box: bounding extent <= 10 after step 100.
  - Bloom check: bit count <= 4x initial seed weight after step 100.
  - Cooperative survival: single-bit seed dies in <= 50 steps.
- For any rule+seed combination passing those sweep filters, perform the full Coherence Tests:
  1. Single-Bit Decomposition Test (F2): Run a single bit at center (20,20,20) for 50 steps; verify it dies in <= 50 steps.
  2. O_h Covariance Test (F3):
     - Load 48 O_h transforms from `src.rigorous_glider_audit.build_oh_transforms()`.
     - For each of the 48 transforms, rotate the seed coordinates relative to (20,20,20) using `M_g` matrix (rounding coords to nearest integers).
     - Filter out duplicate rotated seeds.
     - Simulate each unique rotated seed for 300 steps.
     - Verify that EVERY unique rotated seed survives, propagates (displacement >= 5.0), remains compact (bounding box <= 10 after step 100), and does not bloom (bit count <= 4x initial after step 100).
     - If any rotation fails, the candidate fails F3 (covariance).
  3. Bloom and Debris re-check (F5, F6) on the original seed.
  4. Full 300-step run: Verify survival >= 300 steps with net displacement >= 5.0.
- Save the coherence results to `archive/iter_253/results/coherence_results.csv` with columns: `rule_str, seed_id, decomposition_pass, oh_covariance_pass, bloom_pass, debris_pass, full_pass`.

3. DOCUMENTATION AND SUMMARY (Step 5):
Create `archive/iter_253/results/summary.json` containing:
- `verdict`: "supported" (if at least one candidate passed all coherence tests) or "refuted" (if all failed).
- `total_rules_tested`: total number of unique rules evaluated across sweep and GA.
- `candidates_found`: number of unique rule+seed combinations passing the sweep/GA filters.
- `candidates_passing_coherence`: number of combinations passing all coherence tests.

If no candidates pass all coherence tests (verdict "refuted"), then write a beautiful, detailed scientific write-up in your final report. Describe the totalistic cellular automata phase space on the FCC lattice (how lambda values relate to rapid death, localization, explosion, stationary still-lives, etc.), using the generated data in `phase_diagram.csv` and `ga_results.csv`.

Ensure all files are correctly created and structured. Let's run this full pipeline systematically!