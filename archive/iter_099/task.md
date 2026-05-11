# Task – iter_099

**Hypothesis:** A population of C2-rules with mappings biased to high-density neighborhoods will contain at least one rule that resolves a random soup into a low-density state.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_099/results/` (relative to the project root).

## Task

Create a new script, `src/run_targeted_soup_search.py`.

**1. Implement Targeted Rule Generation:**
- Create a function to generate one C2-symmetric rule with exactly 8 kernel pairs (16 non-identity mappings).
- Define "high-density states" as those with a Hamming Weight of 4, 5, or 6 (there are 35+21+7=63 such states, plus the all-1s state for a total of 64 if you include weight 7).
- To generate the rule's kernels, randomly select pairs `(A, B)` exclusively from the pool of unmapped, high-density states. This ensures all active mappings are in the high-density regime. The generation must ensure the resulting C2-closure for each pair is valid and conflict-free.

**2. Generate and Evaluate Population:**
- Generate a population of 100 of these "targeted sparse" rules and save them to `archive/iter_099/population/`.
- Evaluate each rule using the established soup methodology:
  - Initialize a 150x150 grid with 25% random noise (use the same fixed random seed as iter_097/098).
  - Simulate for 1000 steps.
  - Record the `final_bit_count`.

**3. Classify and Report:**
- Classify each rule's outcome based on its `final_bit_count`:
  - `DEAD`: `final_bit_count` < 20
  - `CHAOTIC`: `final_bit_count` > 1000
  - `INTERESTING`: 20 <= `final_bit_count` <= 1000
- Create `archive/iter_099/result.yaml` with the counts for each class (`dead_rules_count`, `chaotic_rules_count`, `interesting_rules_count`).
- Create `archive/iter_099/results/interesting_rules.txt`, listing the filenames of all rules classified as `INTERESTING`. This file should be empty if none are found.


## Success Criteria

- At least one rule is classified as 'INTERESTING'.
- The `interesting_rules_count` in result.yaml is greater than 0.

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
