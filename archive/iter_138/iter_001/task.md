Create a new script, `src/run_parity_constrained_search.py`, to generate and evaluate a population of C2-symmetric rules that adhere to a bit-count parity-conservation constraint.

**1. Implement Parity-Constrained Rule Generation:**
- Start with the rule generation logic from the medium-density arm of the density scan (iter_129).
- The function should generate C2-symmetric rules with exactly 8 kernel pairs (32 non-identity mappings).
- Add a critical new constraint: a randomly selected state pair `(A, B)` is only considered valid for a kernel if `HammingWeight(A) % 2 == HammingWeight(B) % 2`.
- Generate a population of 100 such parity-conserving rules and save them to `archive/iter_138/population/`.

**2. Evaluation:**
- Evaluate each of the 100 rules using the established "ash" simulation environment (`src/ash_pattern.json`).
- Use the "late displacement" metric, calculating displacement between simulation steps 100 and 200.
- Apply the quadratic fitness penalty function from iter_136: `fitness = displacement / (1 + (bit_ratio - 1)**2)`, where `bit_ratio` is `final_bits / initial_bits`.

**3. Reporting:**
- A rule is considered a "viable founder" if it has `fitness > 0.01` AND `bit_ratio < 3.0`.
- Create a summary file `archive/iter_138/results/summary.yaml` containing:
  - `viable_founder_count`: The number of viable founders found.
  - `top_fitness_score`: The highest fitness score in the population.
  - `top_fitness_bit_ratio`: The bit ratio of the rule with the highest fitness.
  - `top_fitness_rule_id`: The filename of the top-scoring rule.

The final output YAML for the orchestrator should include these same metrics.