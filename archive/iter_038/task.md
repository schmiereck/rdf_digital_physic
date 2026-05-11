# Task – iter_038

**Hypothesis:** search-center-flipping: There exists a state-pair (A, B) that is conflict-free, has disjoint orbits, and has different center-bit parities.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_038/results/` (relative to the project root).

## Task

Create a new Python script `src/find_center_flipping_kernel.py`. This script will perform a combinatorial search, not a simulation.

1.  **Implement Utilities:** Create helper functions for hexagonal rotation of 7-bit integer states and for checking the center bit of a state.
2.  **Define State Space:** Generate all 7-bit states for a given Hamming weight (start with W=2, then W=3 if no results are found).
3.  **Search Loop:**
    a. Iterate through all unique pairs of states `(A, B)` for the current Hamming weight.
    b. For each pair, check three conditions in order of increasing cost:
       i.   **Center-Bit Flip (New):** The center bit of A must be different from the center bit of B.
       ii.  **Disjoint Orbits:** State B must not be in the 6-fold rotational orbit of state A.
       iii. **Conflict-Free Closure:** The joint 12-state rotational closure of {A, B} must contain exactly 12 unique states.
    c. If a pair `(A, B)` satisfies all three conditions, the search is successful. Stop and report this pair.
4.  **Output:**
    Create `archive/iter_038/result.yaml`. The YAML file must contain:
    - `valid_kernel_found`: `true` or `false`.
    - `hamming_weight_searched`: The integer Hamming weight at which a kernel was found (e.g., 2).
    - `pairs_checked`: The total number of pairs checked before finding a valid one.
    - `kernel_A`: The integer representation of the first valid 'A' state found.
    - `kernel_B`: The integer representation of the first valid 'B' state found.
    - `kernel_A_binary`: The 7-bit string representation of 'A'.
    - `kernel_B_binary`: The 7-bit string representation of 'B'.


## Success Criteria

- The script terminates and reports `valid_kernel_found: true`.
- The reported kernel_A and kernel_B must have different center bits.
- The reported kernel passes the disjoint orbit and conflict-free closure checks.

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
