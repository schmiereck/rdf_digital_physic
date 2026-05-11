# Task – iter_072

**Hypothesis:** search-c2-kernel: A valid, reversible, non-conserving C2-symmetric rule kernel (A(2)↔B(3)) exists.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_072/results/` (relative to the project root).

## Task

Create a new script, `src/find_c2_kernel.py`, to perform a combinatorial search for a valid rule kernel with only C2 symmetry.

1. **Search Space:** The script should search through pairs of states `(A, B)` where `A` has Hamming Weight 2 and `B` has Hamming Weight 3.

2. **Constraints:** A pair `(A, B)` is considered a valid C2 kernel if it satisfies all of the following:
    a. **Contiguity:** Both state `A` and state `B` must represent contiguous patterns.
    b. **Center-Bit Flip:** The center bit of `A` must be different from the center bit of `B`.
    c. **Conflict-Free C2 Closure:** The state `A` must not be a 180-degree rotation of `B` (`A != rotate(B, 3)`), and neither state can be its own 180-degree rotation (`A != rotate(A, 3)`). This ensures the four states `{A, B, rotate(A, 3), rotate(B, 3)}` are all distinct and can form a conflict-free C2-symmetric rule.

3. **Execution:** The script should iterate through combinations of contiguous W=2 and W=3 states and test them against the constraints, stopping as soon as the *first* valid pair is found.

4. **Output:** The script must create `archive/iter_072/result.yaml` with the following keys:
    - `kernel_found`: `true` or `false`.
    - `pairs_checked`: The total number of pairs checked before finding a valid kernel.
    - `kernel_A`, `kernel_B`: The integer representations of the found states.
    - `kernel_A_binary`, `kernel_B_binary`: The 7-bit string representations.


## Success Criteria

- The script finds a pair `(A, B)` that satisfies all three C2 kernel constraints.
- `result.yaml` is created with `kernel_found: true`.

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
