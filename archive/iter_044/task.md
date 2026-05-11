# Task – iter_044

**Hypothesis:** A valid kernel constrained to contiguous bits will generate a dynamically non-trivial rule.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_044/results/` (relative to the project root).

## Task

This is a two-part task: first, refine the search for a valid kernel, and second, simulate the rule generated from it.

**Part 1: Find a Contiguous Kernel**
1. Create a new script: `src/find_contiguous_kernel.py`.
2. The script must search for a state-pair `(A, B)` at Hamming Weight 2 that satisfies four conditions:
    a. **Center-Bit Flip:** The center bit of A must be different from the center bit of B.
    b. **Disjoint Orbits:** The rotational orbits of A and B must be disjoint.
    c. **Conflict-Free Closure:** The joint 12-state rotational closure must have exactly 12 unique states.
    d. **Contiguity (New):** For both A and B, the two '1' bits must be in adjacent positions (e.g., center and a neighbor, or two adjacent neighbors).
3. The search should find the first valid kernel `(A, B)` that satisfies all four conditions.
4. The script should print the integers and binary strings for the found kernel pair to stdout.

**Part 2: Generate Rule and Simulate**
1. Modify `src/generate_and_simulate.py` to use the new kernel found in Part 1.
2. The script must generate the full 6-fold symmetric rule from this kernel and use it in the simulator with the standard CA update model.
3. Run the simulation for 100 steps on a 100x100 grid.
4. Use an initial condition that creates the neighborhood of the `B` state of the new kernel. For example, if B represents two adjacent neighbors, place two '1's in that configuration.
5. The script must create `archive/iter_044/result.yaml` with the standard keys: `kernel_A`, `kernel_B`, `behavior_class`, `net_displacement`, `oscillation_period`, `is_bit_conserving`, and `final_bit_count`.


## Success Criteria

- The search in Part 1 finds a valid kernel satisfying all four constraints.
- The `behavior_class` in Part 2 is `STATIONARY_OSCILLATOR` (with period > 1) or `GLIDER`.

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
