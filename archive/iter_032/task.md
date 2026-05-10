# Task – iter_032

**Hypothesis:** symmetrized-rule: A fully symmetrized, reversible, bit-conserving rule produces a stable, non-trivial pattern (glider or oscillator) from a single-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_032/results/` (relative to the project root).

## Task

Create a new Python script `src/simulate_symmetric_hex.py` that uses the standard CA update model.

1.  **Implement Hexagonal Rotation:** Create a helper function `rotate_neighborhood(state: str, steps: int)` that takes a 7-bit neighborhood string 'b0b1b2b3b4b5b6' and rotates the neighbor bits (`b1` to `b6`) by the given number of steps.

2.  **Generate a Symmetric Rule:**
    a. Define a "generator" mapping. Use a non-trivial, bit-conserving, reversible pair. For example:
       `A = '0100100'` (W=2)
       `B = '1000010'` (W=2)
    b. Initialize a rule dictionary where every state maps to itself (identity).
    c. Loop 6 times (for 0 to 5 rotations):
       i.   Calculate `A_rot = rotate_neighborhood(A, i)` and `B_rot = rotate_neighborhood(B, i)`.
       ii.  Add the mappings to the rule: `rule[A_rot] = B_rot` and `rule[B_rot] = A_rot`.
    d. This will create a rule table with 12 non-identity mappings that is symmetric by construction.

3.  **Simulation:**
    a. Use a 100x100 hexagonal grid with periodic boundaries.
    b. Run for 100 steps.
    c. Initial Condition: A single '1' bit at the grid center `(50,50)`.

4.  **Analysis and Output:**
    a. Track bit count and coordinates at each step.
    b. Create `archive/iter_029/result.yaml` with these keys:
       - `is_bit_conserving`: `true` if the bit count changes from its initial value of 1.
       - `behavior_class`: `STABLE_GLIDER`, `STATIONARY_OSCILLATOR`, `DECAY`, `CHAOTIC_GROWTH`, or `TRIVIAL_SHIFT`.
       - `final_bit_count`: The number of '1's at the final step.
       - `final_pattern_summary`: A brief description of the final state (e.g., "3-bit oscillator", "6-bit glider").


## Success Criteria

- The simulation produces a final state that is not a single bit and not chaotic (final_bit_count > 1 and < 20).
- The final pattern must be stable (not changing shape or bit count) or periodic in the last 20 steps.
- The behavior must not be a trivial global shift of the entire grid.

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
