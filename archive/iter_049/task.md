# Task – iter_049

**Hypothesis:** search-w3-kernel: A valid rule kernel exists at Hamming Weight 3 that satisfies all known constraints (contiguity, center-flip, disjoint orbits, conflict-free closure).

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_049/results/` (relative to the project root).

## Task

The task is to perform a formal, combinatorial search, not a simulation.

1.  Modify the script `src/find_contiguous_kernel.py`.
2.  Change the search space from Hamming Weight 2 to **Hamming Weight 3**.
3.  The script must search for the **first** state-pair `(A, B)` at W=3 that satisfies all four established conditions:
    a. **Center-Bit Flip:** `center_bit(A) != center_bit(B)`.
    b. **Disjoint Orbits:** The rotational orbits of A and B must be disjoint.
    c. **Conflict-Free Closure:** The joint 12-state rotational closure must have exactly 12 unique states.
    d. **Contiguity:** For both A and B, all '1' bits must form a single connected cluster.
4.  The script should create `archive/iter_049/result.yaml` with the following keys:
    - `valid_kernel_found`: boolean
    - `hamming_weight_searched`: 3
    - `pairs_checked`: The total number of W=3 pairs checked.
    - `kernel_A`: The integer representation of the first valid A state found.
    - `kernel_B`: The integer representation of the first valid B state found.
    - `kernel_A_binary`: The 7-bit string for A.
    - `kernel_B_binary`: The 7-bit string for B.


## Success Criteria

- `valid_kernel_found` is `true` in the output YAML.
- The output YAML contains non-null integer values for `kernel_A` and `kernel_B`.

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
