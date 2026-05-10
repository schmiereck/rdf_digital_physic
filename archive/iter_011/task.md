# Task – iter_011

**Hypothesis:** existence-2bit: A non-trivial, reversible, bit-conserving rule exists for a 1D, 3-neighborhood, 2-bit/cell lattice.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_011/results/` (relative to the project root).

## Task

Create a Python script `archive/iter_003/code/generate_rules_2bit.py`.

1.  **Define State Space**: A cell can be in one of 4 states: '00', '01', '10', '11'. A neighborhood is a tuple of three cell states, so there are 4^3 = 64 neighborhood states.
2.  **Calculate Hamming Weights**: The Hamming weight of a cell state is the number of '1's (e.g., hw('10') = 1, hw('11') = 2). The total weight of a neighborhood is the sum of the weights of its three cells.
3.  **Group States**: Group all 64 neighborhood states by their total Hamming weight (which can range from 0 to 6).
4.  **Construct a Test Rule**: Create a specific rule with the following logic:
    a. Define a mapping for a stationary particle oscillation: `('00', '01', '00')` maps to `('00', '10', '00')`.
    b. To ensure reversibility, its inverse must also exist: `('00', '10', '00')` maps to `('00', '01', '00')`.
    c. Note that both these neighborhoods have a total Hamming weight of 1, so this is a valid bit-conserving permutation within that group.
    d. For all other 62 neighborhood states, the rule should be the identity mapping (`state -> state`).
5.  **Validation**: Verify that this constructed rule is non-trivial (i.e., it is not the global identity rule).
6.  **Output**: Write a summary to `archive/iter_003/result.yaml` with the following keys:
    - `rule_found`: boolean (True if the constructed rule is valid and non-trivial).
    - `state_space_size`: 64
    - `hamming_group_sizes`: A dictionary mapping each weight (e.g., "W0", "W1") to the number of states in that group.


## Success Criteria

- The script produces `result.yaml`.
- The key `rule_found` in `result.yaml` is `True`.
- The `hamming_group_sizes` dictionary is present and its values sum to 64.

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
