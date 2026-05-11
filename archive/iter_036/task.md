# Task – iter_036

**Hypothesis:** search-disjoint-orbits: There exists at least one reversible, bit-conserving state-pair (A, B) whose 6-fold rotational closure is conflict-free AND where A and B belong to different rotational orbits.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_036/results/` (relative to the project root).

## Task

Create a new Python script `src/find_disjoint_orbit_kernel.py`. This script performs a combinatorial search, not a simulation.

1. **Implement Hexagonal Rotation:** Create a helper function `rotate_neighborhood(state: int, steps: int)` that takes a 7-bit integer state and rotates the 6 neighbor bits clockwise.

2. **Define State Space:** Generate all 21 unique 7-bit states with a Hamming weight of 2 (W=2).

3. **Search Loop:**
   a. Iterate through all possible unique pairs `(A, B)` of these W=2 states.
   b. For each pair, perform two checks:
      i. **Disjoint Orbit Check (New):** Generate the 6 states in the rotational orbit of A. Check if B is in this set. If it is, this pair is invalid; continue to the next pair.
      ii. **Conflict Check (from iter_033):** Generate the "rotational closure": the set of 12 states `{rotate(A, i), rotate(B, i)}` for `i` from 0 to 5. The closure is conflict-free only if its size is exactly 12.
   c. The first pair `(A, B)` that passes *both* checks is the valid kernel.

4. **Output:**
   a. Create `archive/iter_036/result.yaml`.
   b. The YAML file must contain:
      - `valid_kernel_found`: `true` or `false`.
      - `hamming_weight_searched`: The integer `2`.
      - `pairs_checked`: The total number of pairs of W=2 states checked before finding a valid one.
      - `kernel_A`: The integer representation of the first valid 'A' state found.
      - `kernel_B`: The integer representation of the first valid 'B' state found.
      - `kernel_A_binary`: The 7-bit string representation of 'A'.
      - `kernel_B_binary`: The 7-bit string representation of 'B'.


## Success Criteria

- The script reports `valid_kernel_found: true`.
- The reported kernel pair (A, B) must pass both the disjoint orbit check and the conflict check.

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
