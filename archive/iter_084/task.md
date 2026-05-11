# Task – iter_084

**Hypothesis:** evolution-crossover: The second generation of rules, bred from Gen-1 elites, has a higher mean fitness than the initial random population.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_084/results/` (relative to the project root).

## Task

Create a new script, `src/breed_next_generation.py`, to perform the crossover and mutation steps of the evolutionary algorithm.

**1. Load Gen-1 Elites:**
- Load the 10 elite rule files from `archive/iter_083/elites/`. Each rule is defined by a set of kernel pairs.

**2. Define Genetic Operators:**
- **Crossover:** Implement a function `crossover(parent1_kernels, parent2_kernels)` that creates a child's kernel set by taking a random half of the kernels from each parent.
- **Mutation:** Implement a function `mutate(kernels, probability=0.1)` that has a chance to apply one of the following mutations:
  - Add a new random kernel pair `(A, B)`.
  - Delete a random kernel pair.
  - Flip a single random bit in one of the integers of a random kernel pair.

**3. Generate Gen-2 Population:**
- Create a new population of 100 rules for the next generation.
- **Elitism:** The top 2 rules from the Gen-1 elites are copied directly into the Gen-2 population.
- **Breeding:** Generate the remaining 98 rules by:
  a. Randomly selecting two parents from the 10 elites.
  b. Creating a child rule by applying the `crossover` function.
  c. Applying the `mutate` function to the child's kernels.
- Save the 100 new rules to `archive/iter_084/population/`.

**4. Evaluate Gen-2 Population:**
- Using the same fitness evaluation script/logic from `iter_082/083`, calculate the fitness for each of the 100 new rules.
  - Grid: 100x100, 50% random noise.
  - Steps: 500.
  - Metric: `mean(bit_count_last_100) * stddev(bit_count_all)`.
- Save the results to `archive/iter_084/results/fitness_scores.csv`.

**5. Report & Compare:**
- Create `archive/iter_084/result.yaml` with the following keys:
  - `gen1_fitness_mean`: The mean fitness from iter_083 (value: 226850.54).
  - `gen2_fitness_mean`: The calculated mean fitness of the new Gen-2 population.
  - `fitness_improvement`: The percentage change from Gen-1 to Gen-2 mean fitness.
  - `gen2_top_fitness`: The single highest fitness score in the Gen-2 population.


## Success Criteria

- The mean fitness of the Gen-2 population must be greater than the Gen-1 mean fitness of 226850.54.

## Required Output

You MUST end your final response with a ```yaml``` code block in this exact schema (the orchestrator reads it to determine success):

```yaml
status: ok  # or experiment_failed or code_error
artifacts:
  - path/to/created/file  # relative to the project root
metrics:
  key: value  # any numeric results
log_excerpt: |  # last ~20 lines of relevant output
  ...
experimenter_view: |  # your qualitative observations
  ...
notes: brief technical remark
```
