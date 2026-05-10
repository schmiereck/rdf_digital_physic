# Task – iter_015

**Hypothesis:** existence-2D-hex: A non-trivial, reversible, bit-conserving rule exists for a 2D hexagonal, 7-cell neighborhood.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_015/results/` (relative to the project root).

## Task

Create a Python script `src/generate_rules_hex.py` to analyze the rule space of a 2D hexagonal lattice with 1 bit per cell.

1.  **Define State Space**: A neighborhood consists of a central cell and its 6 neighbors, for a total of 7 cells. The state space contains 2^7 = 128 unique neighborhood configurations (represented as 7-bit strings).
2.  **Group by Hamming Weight**: Iterate through all 128 states and group them by their Hamming weight (number of '1's).
3.  **Construct a Test Rule**: To prove existence without enumerating all possibilities, construct a single, simple, non-trivial rule:
    a. Choose two distinct neighborhood states from the same Hamming weight group (e.g., from the W=1 group, which contains 7 states like '1000000', '0100000', etc.).
    b. Define a rule that swaps these two states.
    c. For all other 126 states, the rule is the identity mapping (the state maps to itself).
4.  **Validate Rule**: Confirm that this constructed rule is non-trivial (i.e., it is not the identity rule where all 128 states map to themselves).
5.  **Write Output**: Create `archive/iter_015/result.yaml` with the following information:
    - `state_space_size`: The total number of neighborhood states (128).
    - `rule_found`: A boolean indicating if a non-trivial, reversible, bit-conserving rule was successfully constructed.
    - `hamming_group_sizes`: A dictionary mapping each weight ("W0" through "W7") to the number of states in that group. The sizes should follow the binomial coefficients C(7, k).


## Success Criteria

- `result.yaml` is created and `rule_found` is true.
- The sum of all values in `hamming_group_sizes` equals 128.

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
