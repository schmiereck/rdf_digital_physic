# Task – iter_061

**Hypothesis:** search-3cycle-kernel: A valid W=3 kernel exists as a 3-cycle (A,B,C) satisfying all known constraints.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_061/results/` (relative to the project root).

## Task

Create a new script `src/find_w3_cycle_kernel.py` to perform a combinatorial search for a valid 3-cycle kernel.

1. **Search Space:** The script should search through triplets of unique states `(A, B, C)` where each state has a **Hamming Weight of 3**.

2. **Constraints:** A triplet is considered valid if it satisfies all of the following conditions:
    a. **Contiguity:** All three states (A, B, and C) must represent contiguous patterns on the hex grid.
    b. **Center-Bit Flip:** The cycle must involve at least one flip of the center bit (i.e., the center bits of A, B, and C are not all identical).
    c. **Disjoint Orbits:** The 6-fold rotational orbits of A, B, and C must be mutually disjoint from each other.
    d. **Conflict-Free Closure:** The joint rotational closure, formed by the 18 states `{rotate(A,i), rotate(B,i), rotate(C,i)}` for `i` in `0..5`, must contain exactly 18 unique states.

3. **Execution:** The script should iterate through combinations of valid W=3 states and test them against the constraints, stopping as soon as the *first* valid triplet is found.

4. **Output:** The script must create `archive/iter_061/result.yaml` with the following keys:
    - `kernel_found`: `true` or `false`.
    - `hamming_weight_searched`: The integer `3`.
    - `triplets_checked`: The total number of triplets checked.
    - `kernel_A`, `kernel_B`, `kernel_C`: The integer representations of the found states.
    - `kernel_A_binary`, `kernel_B_binary`, `kernel_C_binary`: The 7-bit string representations.


## Success Criteria

- A valid triplet (A, B, C) is found that satisfies all four constraints.
- The script successfully creates the result.yaml file.

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
