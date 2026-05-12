# Task – iter_105

**Hypothesis:** cooling-rules-simplified: A population of C2-rules with a simplified 'cooling' bias (HW(A) > HW(B)) contains at least one rule that resolves a random soup into a low-density state.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch.
Write results and data files to `archive/iter_105/results/` (relative to the project root).

## Task

This task is a corrected and simplified re-run of iter_101. Create a new script `src/run_cooling_soup_search_v2.py`.

**1. Implement Simplified 'Cooling' Rule Generation:**
- Create a function to generate one C2-symmetric rule with exactly 8 kernel pairs (16 non-identity mappings).
- To generate the kernels, repeatedly select random pairs `(A, B)` from the pool of all 128 states.
- A pair is valid only if:
  a. `HammingWeight(A) > HammingWeight(B)`.
  b. The C2-symmetric closure of the pair `(A, B)` does not conflict with already-mapped states.
- Once 8 valid, conflict-free pairs are found, finalize the rule.

**2. Generate and Evaluate Population:**
- Generate a population of 100 "cooling" rules and save them to `archive/iter_105/population/`.
- Evaluate each rule using the established soup methodology:
  - Initialize a 150x150 grid with 25% random noise (use random seed=42 for reproducibility).
  - Simulate for 1000 steps.
  - Record the `final_bit_count`.

**3. Classify and Report:**
- Classify each rule's outcome based on its `final_bit_count`:
  - `DEAD`: `final_bit_count` < 20
  - `CHAOTIC`: `final_bit_count` > 1000
  - `INTERESTING`: 20 <= `final_bit_count` <= 1000
- Create `archive/iter_105/result.yaml` with the counts for each class (`dead_rules_count`, `chaotic_rules_count`, `interesting_rules_count`).
- Create `archive/iter_105/results/interesting_rules.txt`, listing the filenames of all rules classified as `INTERESTING`.


## Success Criteria

- The script completes without a `code_error`.
- The number of `interesting_rules_count` is greater than 0.

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
