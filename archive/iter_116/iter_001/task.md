
Create a new script, `src/generate_and_test_hybrid_rule.py`, to perform a two-phase experiment.

**Part 1: Hybrid Rule Generation**

1.  The script must generate a single, C2-symmetric, reversible, non-conserving rule with a hybrid mapping strategy.
2.  The rule should be constructed from two distinct sets of kernel pairs, ensuring no conflicts in the final rule table:
    *   **Cooling Kernels (4 pairs):** Randomly select 4 kernel pairs `(A, B)` where `HammingWeight(A) > HammingWeight(B)`. State `A` should be selected from a pool of medium-to-high density states (Hamming Weight >= 3) to ensure they are active in a dense soup. State `B` should be selected from low-density states (Hamming Weight < 3).
    *   **Glider/Birth Kernels (4 pairs):** Randomly select 4 kernel pairs `(C, D)` where `HammingWeight(C) < HammingWeight(D)`. State `C` should be selected from low-density states (Hamming Weight <= 2) to act on sparse patterns. State `D` should have a higher Hamming Weight.
3.  Save the generated hybrid rule to `archive/iter_116/results/hybrid_rule.json`.

**Part 2: Two-Phase Evaluation**

The script must evaluate the generated hybrid rule in two distinct tests.

**Test A: Soup Resolution**
1.  Initialize a 150x150 grid with 25% random noise (use random seed=42 for reproducibility).
2.  Simulate the hybrid rule for 1000 steps.
3.  Record the `final_bit_count`.
4.  Determine if the soup was resolved: `soup_resolved = True` if `20 <= final_bit_count <= 1000`, otherwise `False`.

**Test B: Glider Search**
1.  Perform a robust multi-seed search for gliders using the *same* hybrid rule.
2.  Test against all 21 standard contiguous seeds (11 trihexes, 10 tetrahexes).
3.  For each seed, simulate for 500 steps and calculate the motion fitness (`displacement / (1 + final_bit_count)`).
4.  The final `motion_fitness` for the rule is the maximum fitness found across all 21 seeds.
5.  Record whether a glider was found: `glider_found = True` if `motion_fitness > 0`, otherwise `False`.

**Part 3: Final Report**

The script must create the final `result.yaml` in `archive/iter_116/` with the following keys:
*   `status`: 'ok' if the script completes, 'experiment_failed' otherwise.
*   `soup_resolved`: (boolean) Result from Test A.
*   `final_soup_bit_count`: (integer) The final cell count from Test A.
*   `glider_found`: (boolean) Result from Test B.
*   `motion_fitness`: (float) The maximum motion fitness score from Test B.
*   `glider_seed_info`: A string describing the seed that produced the glider (e.g., "4-bit T-shape"), or "" if none found.
*   `glider_period`: The period of the found glider, or 0.
*   `glider_velocity`: The (dq, dr) velocity of the found glider, or (0,0).
