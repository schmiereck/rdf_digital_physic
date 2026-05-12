Create a Python script `src/run_biased_hybrid_rule_test.py` to generate and evaluate a single 'biased hybrid' cellular automata rule.

**1. Rule Generation:**
- Implement a function to generate one C2-symmetric, reversible (involution) rule with exactly 8 total kernel pairs (16 non-identity mappings). Use `random.seed(117)` for reproducibility.
- The rule must have a **6:2 cooling bias**:
    - **6 Cooling Pairs:** Randomly select 6 pairs `(A, B)` where `HammingWeight(A) >= 3` and `HammingWeight(B) < 3`.
    - **2 Birth Pairs:** Randomly select 2 pairs `(A, B)` where `HammingWeight(A) <= 2` and `HammingWeight(B) > HammingWeight(A)`, with the added constraint that the center bit must be preserved (i.e., `A % 2 == B % 2`).
- Ensure all mappings are chosen without replacement and are conflict-free under C2 symmetry.
- Save the generated rule to `archive/iter_117/rule/biased_hybrid_rule.json`.

**2. Dual Evaluation:**
- **Soup Test:**
    - Initialize a 150x150 grid with 25% random noise (using a fixed `numpy.random.seed(42)`).
    - Simulate the generated rule for 1000 steps.
    - Record the final number of live cells.
- **Motion Test:**
    - Evaluate the rule's motion fitness by testing it against all 21 standard contiguous 3- and 4-bit seeds.
    - For each seed, simulate for 500 steps, detect cycles, and calculate `fitness = displacement / (1 + final_bit_count)`.
    - The rule's final motion fitness is the maximum score achieved across all 21 seeds.

**3. Final Output:**
- The script MUST end by printing a YAML block to standard output with the results. This YAML block must contain:
  ```yaml
  status: ok
  artifacts:
    - "archive/iter_117/rule/biased_hybrid_rule.json"
  metrics:
    soup_resolved: 1 # 1 if final_soup_bit_count <= 1000, else 0
    final_soup_bit_count: ... # The integer count
    glider_found: 1 # 1 if motion_fitness > 0, else 0
    motion_fitness: ... # The float value
    cooling_pairs: 6
    birth_pairs: 2
  log_excerpt: |
    ...
  experimenter_view: |
    ...
  notes: "Biased hybrid rule generation and evaluation complete."
  ```