Execute Steps 2-5 of the pre-registered experiment for iteration 253.

First, read the pre-registration and falsification criteria in `src/pre_registration.md` and strictly adhere to them.

1. ENGINE VALIDATION:
Verify that the 3D FCC CA engine works properly by running `python3 src/synchronous_ca_fcc.py`.

2. STEP 2 — DESIGNED RULE SWEEP:
Create `src/totalistic_rule_search.py` to generate and sweep B/S rules on the FCC lattice.
- Grid: 40x40x40.
- Simulation steps: 500.
- Rule Generation (200 unique rules total, 0 not in B, S; B ⊆ {1,...,11}, S ⊆ {1,...,12}):
  - 100 sparse rules (|B| <= 2, |S| <= 3)
  - 50 medium rules (|B| = 2-3, |S| = 3-5)
  - 50 lambda-targeted rules (B,S giving Langton's lambda in [0.25, 0.45])
  Use random.Random(42) to generate these deterministically and avoid duplicates.
- Seed Generation (46 unique seeds):
  - Seed 0: Single bit at center (20,20,20)
  - Seeds 1-12: Bit pairs: origin (20,20,20) + one of the 12 neighbor offsets from FCC_OFFSETS.
  - Seeds 13-20: 8 variants of L-tromino analogs (e.g. connected 3-bit L-shapes).
  - Seeds 21-45: 25 variants of random compact clusters of size 3-6. Generate these deterministically using random.Random(42) starting from the center (20,20,20) and adding adjacent neighbor offsets to ensure they are connected and compact.
- Simulation and Tracking:
  - Run 500 steps for each rule x seed.
  - Track: bit_counts, coms (unwrapped_com), extents (bounding_extent) at each step.
- Filtering (identify candidate rule + seed combinations):
  - Survival: bit_count > 0 at step 300.
  - Displacement: net_displacement >= 5.0 lattice units over 300+ steps (use displacement at final step of survival or step 300).
  - Bounding box: max bounding box size <= 10 after step 100 (i.e. max(extents[100:survival_time+1]) <= 10).
  - Bloom check: max bit count <= 4x initial seed weight after step 100 (i.e. max(bit_counts[100:survival_time+1]) <= 4 * bit_counts[0]).
  - Cooperative survival: single-bit seed under this rule must die within <= 50 steps.
- Outputs:
  - Save to `archive/iter_253/results/sweep_results.csv`: columns = `rule_str, seed_id, survival, displacement, max_bit_ratio, max_bounding_box, verdict`
  - Save to `archive/iter_253/results/phase_diagram.csv`: aggregate statistics per rule lambda value — number of rules, fraction of seeds surviving, mean displacement, etc.

3. STEP 3 — EVOLUTIONARY GA:
Create `src/totalistic_ga.py`. If the sweep yielded < 5 candidate rules, execute this GA.
- Population: 200 rules.
- Genome: 26-bit representation (bits 0-10 = B set for counts 1-11, bits 11-23 = S set for counts 1-12, bits 24-25 unused).
  Enforce 0 not in B, S by construction.
- Generations: 50 (or keep running generations and/or additional search until the total number of unique rules evaluated across sweep + GA is >= 10,000!).
- Evaluation: Each rule is evaluated on 5 seeds (e.g. 1 bit pair, 1 L-tromino, and 3 random compact clusters) for 300 steps.
- Fitness function:
  - `survival_score = min(survival_steps / 300.0, 1.0)`
  - `displacement_score = min(net_displacement / 10.0, 1.0)`
  - `compact_score = 1.0 if max_bounding_box <= 10 else 0.0`
  - `no_bloom_score = 1.0 if max_bit_ratio <= 4.0 else 0.0`
  - `fitness = survival_score * displacement_score * compact_score * no_bloom_score`
  Take the mean fitness over the 5 seeds.
- GA Parameters:
  - Selection: tournament size 3.
  - Crossover: uniform crossover.
  - Mutation: bit-flip with p=0.1.
  - Elitism: top 5 survive unchanged.
- Output:
  - Save to `archive/iter_253/results/ga_results.csv`: columns = `gen, rule_str, mean_fitness, best_fitness`.

4. STEP 4 — COHERENCE TESTING:
Create `src/glider_coherence_test.py` to test any candidate rule+seed combinations passing the sweep or GA filters.
- Run the following tests:
  1. Single-Bit Decomposition Test (F2): Verify that a single bit seed under this rule dies in <= 50 steps.
  2. O_h Covariance Test (F3): Load the 48 O_h transforms using `build_oh_transforms()` from `src/rigorous_glider_audit.py`. Apply each matrix `M_g` to rotate the initial seed's coordinates relative to (20,20,20). Verify that all 48 rotations of the seed produce surviving, propagating, non-blooming, non-debris-shedding patterns. If any rotation fails, the candidate fails.
  3. Bloom and Debris re-check (F5, F6): Verify bit count <= 4x initial and bounding extent <= 10 after step 100.
  4. Full 300-step run: Verify survival >= 300 steps with net displacement >= 5.0.
- Output:
  - Save to `archive/iter_253/results/coherence_results.csv`: columns = `rule_str, seed_id, decomposition_pass, oh_covariance_pass, bloom_pass, debris_pass, full_pass`

5. STEP 5 — DOCUMENTATION & SUMMARY:
Create `archive/iter_253/results/summary.json` containing:
- `verdict`: "supported" (if at least one glider passed all tests) or "refuted" (if all failed).
- `total_rules_tested`: total number of unique rules evaluated across sweep and GA.
- `candidates_found`: number of candidates passing sweep/GA filters.
- `candidates_passing_coherence`: number of candidates passing all coherence tests.
If NO candidates pass all coherence tests, document this clearly as a first-class null result, describing the totalistic phase diagram of the FCC CA (what lambda ranges produce survival, explosion, or immediate death).

Let's run this full pipeline systematically. Ensure all results and outputs are correctly saved under `archive/iter_253/results/`. Report the summary of what you did.