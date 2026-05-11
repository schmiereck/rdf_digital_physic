# Task – iter_101

**Hypothesis:** cooling-rules-fix: A population of C2-rules, biased to map medium-density states to lower-density states, contains at least one rule that resolves a random soup into a low-density state.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_101/results/` (relative to the project root).

## Task

This task is a re-run of iter_100. Please debug and fix the `code_error` from the previous attempt.

Create a script `src/run_cooling_soup_search.py`.

**1. Implement 'Cooling' Rule Generation:**
- Create a function to generate a single C2-symmetric rule with exactly 8 kernel pairs (16 non-identity mappings).
- To generate the kernels, randomly select pairs `(A, B)` such that:
  - The Hamming Weight of state `A` is in `{2, 3}` (medium density).
  - The Hamming Weight of state `B` is in `{0, 1}` (low density).
- The pools of medium- and low-density states must be sampled without replacement to ensure all 8 generated kernel pairs are unique and result in a conflict-free C2-symmetric rule.

**2. Generate and Evaluate Population:**
- Generate a population of 100 "cooling" rules and save them to `archive/iter_101/population/`.
- Evaluate each rule using the established soup methodology:
  - Initialize a 150x150 grid with 25% random noise (use the same fixed random seed as prior soup experiments, e.g., seed=42).
  - Simulate for 1000 steps.
  - Record the `final_bit_count`.

**3. Classify and Report:**
- Classify each rule's outcome based on its `final_bit_count`:
  - `DEAD`: `final_bit_count` < 20
  - `CHAOTIC`: `final_bit_count` > 1000
  - `INTERESTING`: 20 <= `final_bit_count` <= 1000
- Create `archive/iter_101/result.yaml` with the counts for each class (`dead_rules_count`, `chaotic_rules_count`, `interesting_rules_count`).
- Create `archive/iter_101/results/interesting_rules.txt`, listing the filenames of all rules classified as `INTERESTING`.


## Success Criteria

- The script runs without code errors.
- At least one rule is classified as 'INTERESTING' (final_bit_count between 20 and 1000).

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
