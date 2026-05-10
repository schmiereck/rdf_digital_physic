# Task – iter_030

**Hypothesis:** still-life: A stable, non-trivial, stationary bit pattern (a 'still life') exists for the arrowhead glider rule.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_030/results/` (relative to the project root).

## Task

Create a new script `src/find_still_life.py`.

1.  **Reuse Logic:** This script should reuse the hexagonal grid simulator and the 5-pair permutation rule defined in `src/simulate_hex.py` from iter_024.
2.  **Search Algorithm:**
    a. Systematically generate small, contiguous patterns of bits. Start with all 2-bit patterns, then all 3-bit patterns, where the bits are within a 2-cell radius of each other.
    b. For each candidate pattern:
        i.  Initialize a 50x50 grid with the pattern at the center.
        ii. Run the simulation for exactly ONE step.
        iii. Compare the grid state at step 1 with the state at step 0.
    c. If the states are identical, the pattern is a still life.
3.  **Outputs:**
    a. If any still lifes are found, create the directory `archive/iter_026/results/`.
    b. Save the first valid still life found as a list of its `(q, r)` coordinates to `archive/iter_026/results/still_life.json`.
    c. Create `archive/iter_026/result.yaml` with the following keys:
        - `still_life_found`: boolean (`true` or `false`).
        - `patterns_checked`: The total number of unique patterns tested.
        - `smallest_still_life_size`: The number of bits in the smallest found still life (or 0 if none).


## Success Criteria

- `still_life_found` is true in the output YAML.
- A `still_life.json` file is created containing the coordinates of the found pattern.

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
