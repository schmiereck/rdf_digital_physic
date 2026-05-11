# Task – iter_065

**Hypothesis:** search-2-3-cycle: A valid kernel (A,B) exists where popcount(A)=2, popcount(B)=3, and the pair satisfies all known structural constraints (contiguity, center-flip, disjoint orbits, conflict-free closure).

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_065/results/` (relative to the project root).

## Task

Create a new script, `src/find_nonconserving_kernel.py`, to perform a combinatorial search.

1.  **Search Space:** The script should search through pairs of states `(A, B)` where `A` has Hamming Weight 2 and `B` has Hamming Weight 3.
2.  **Constraints:** A pair `(A, B)` is valid if it satisfies all four of the following conditions:
    a. **Contiguity:** Both state `A` and state `B` must represent contiguous patterns.
    b. **Center-Bit Flip:** The center bit of `A` must be different from the center bit of `B`.
    c. **Disjoint Orbits:** The 6-fold rotational orbits of `A` and `B` must be mutually disjoint.
    d. **Conflict-Free Closure:** The joint rotational closure, formed by the 12 states `{rotate(A,i), rotate(B,i)}` for `i` in `0..5`, must contain exactly 12 unique states.
3.  **Execution:** Iterate through combinations and stop at the *first* valid pair found.
4.  **Output:** Create `archive/iter_065/result.yaml` with the following keys:
    - `kernel_found`: `true` or `false`.
    - `popcount_A`: 2
    - `popcount_B`: 3
    - `pairs_checked`: The total number of pairs checked.
    - `kernel_A`, `kernel_B`: The integer representations of the found states.
    - `kernel_A_binary`, `kernel_B_binary`: The 7-bit string representations.


## Success Criteria

- The script terminates and reports `kernel_found: true`.
- The reported kernel pair (A, B) must satisfy all four specified constraints.

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
