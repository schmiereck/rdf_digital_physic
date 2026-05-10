# Task – iter_033

**Hypothesis:** search: There exists at least one reversible, bit-conserving state-pair (A, B) whose 6-fold rotational closure is conflict-free.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_033/results/` (relative to the project root).

## Task

Create a new Python script `src/find_symmetric_kernel.py`. This script will not run a simulation, but will perform a combinatorial search.

1.  **Implement Hexagonal Rotation:** Create a helper function `rotate_neighborhood(state: int, steps: int)` that takes a 7-bit integer state and rotates the 6 neighbor bits clockwise.
2.  **Define State Space:** Generate all 21 unique 7-bit states with a Hamming weight of 2 (W=2).
3.  **Search Loop:**
    a. Iterate through all possible unique pairs `(A, B)` of these W=2 states.
    b. For each pair, generate its "rotational closure": a set containing the 12 states `{rotate(A, i), rotate(B, i)}` for `i` from 0 to 5.
    c. **Check for Conflicts:** A conflict exists if the size of the generated set is less than 12. This indicates that some rotations of A and B overlap, which would create an invalid rule.
    d. If a conflict-free pair is found (set size is 12), the search is successful.
4.  **Output:**
    a. Create `archive/iter_033/result.yaml`.
    b. The YAML file must contain:
       - `valid_kernel_found`: `true` or `false`.
       - `hamming_weight_searched`: The integer `2`.
       - `pairs_checked`: The total number of pairs of W=2 states that were checked.
       - `kernel_A`: The integer representation of the first valid 'A' state found (or `null`).
       - `kernel_B`: The integer representation of the first valid 'B' state found (or `null`).
       - `kernel_A_binary`: The 7-bit string representation of 'A'.
       - `kernel_B_binary`: The 7-bit string representation of 'B'.


## Success Criteria

- The script successfully finds a pair (A, B) where the size of its rotational closure is 12.
- The `valid_kernel_found` key in `result.yaml` is `true`.

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
