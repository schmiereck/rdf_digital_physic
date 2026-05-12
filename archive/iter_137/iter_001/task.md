
This task is a re-evaluation of existing data, not a new simulation run. It aims to find a viable "founder" rule from the medium-density population generated in iter_136 by applying a stricter fitness function.

**1. Create a new script: `src/re_evaluate_with_penalty.py`**

**2. Load Existing Data:**
   - The script must load the 100 `medium_density` rules from `archive/iter_136/population/medium_density/`.
   - It should also load the simulation results (displacement and bit-ratio for each rule) from `archive/iter_136/results/medium_density_scores.csv`. NO NEW SIMULATIONS ARE NEEDED.

**3. Implement New Fitness Calculation:**
   - For each rule from the loaded data, calculate a new fitness score using a **quadratic penalty**:
     `quadratic_fitness = displacement / (1 + abs(bit_ratio - 1)**2)`
   - Also, re-calculate the original `linear_fitness` for comparison.

**4. Analyze and Report:**
   - Create a new CSV file `archive/iter_137/results/re_evaluation_scores.csv` with the following columns: `rule_name, displacement, bit_ratio, linear_fitness, quadratic_fitness`.
   - Identify the rule with the highest `quadratic_fitness`.
   - Determine if this top rule is "viable" using the established criteria: `quadratic_fitness > 0.001` AND `bit_ratio < 3.0`.
   - The script's primary output MUST be a YAML file at `archive/iter_137/results/result.yaml` containing the metrics for the best rule found under the new quadratic scoring:
     - `best_rule_filename`
     - `best_rule_quadratic_fitness`
     - `best_rule_displacement`
     - `best_rule_bit_ratio`
     - `viable_founder_found` (a boolean value)

**5. Final Executor Output:**
   The executor must end its response with a standard YAML block, copying the metrics directly from the `result.yaml` file.
