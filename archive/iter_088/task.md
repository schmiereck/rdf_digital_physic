# Task – iter_088

**Hypothesis:** evolution-new-metric: Breeding a new generation using a stability-rewarding fitness metric increases the population's mean fitness by >50%.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_088/results/` (relative to the project root).

## Task

Create a new script, `src/run_evolution_cycle_new_metric.py`, to perform a full generation, selection, and breeding cycle using the new fitness metric.

**1. Re-evaluate Gen-2 Population:**
- Load all 100 rules from the Gen-2 population stored in `archive/iter_084/population/`.
- For each rule, calculate its fitness using the new metric from iter_087:
  - Initialize a 150x150 grid with a single 4-bit "T-shape" seed.
  - Simulate for 500 steps.
  - Fitness = `1 / (1 + final_bit_count)`.
- Record these scores and calculate the mean fitness for this re-scored Gen-2 population.

**2. Select New Elites:**
- From the 100 re-scored rules, identify the top 10 with the highest new fitness scores.

**3. Breed Gen-3 Population:**
- Create a new population of 100 rules for "Gen-3".
- **Elitism:** Carry over the top 2 of the newly selected Gen-2 elites directly.
- **Breeding:** Generate the remaining 98 rules by:
  a. Randomly selecting two parents from the 10 new elites.
  b. Creating a child's kernel set by taking a random half of the kernels from each parent (crossover).
  c. Applying a mutation with 10% probability (add/delete a kernel pair, or flip a bit in a kernel).
- Save the 100 new Gen-3 rules to `archive/iter_088/population/`.

**4. Evaluate Gen-3 Population:**
- Calculate the fitness for each of the 100 new Gen-3 rules using the exact same method as in Step 1.
- Calculate the mean fitness for the new Gen-3 population.

**5. Report & Compare:**
- Create `archive/iter_088/result.yaml` with the following keys:
  - `gen2_rescored_fitness_mean`: The mean fitness of the Gen-2 population under the new metric.
  - `gen3_fitness_mean`: The mean fitness of the new Gen-3 population.
  - `fitness_improvement_pct`: The percentage change in mean fitness from Gen-2 to Gen-3.
  - `gen3_top_fitness`: The single highest fitness score in the Gen-3 population.


## Success Criteria

- The `gen3_fitness_mean` is at least 50% greater than `gen2_rescored_fitness_mean`.
- The number of chaotic rules (fitness < 0.001) in the Gen-3 population is less than half the number found in the re-scored Gen-2 population.

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
