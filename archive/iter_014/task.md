# Task – iter_014

**Hypothesis:** composite: A rule can be constructed to make a two-cell particle (e.g., '0110') propagate stably with v=c/2.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_014/results/` (relative to the project root).

## Task

Modify the simulator in `src/simulate.py` (which should exist from previous work) to test a composite particle.

1.  **Target Dynamics:** A two-cell particle, represented by the pattern `'01','10'` at adjacent positions `i` and `i+1`, should propagate at an effective velocity of v=c/2. This requires a two-step cycle:
    a. **Step 1 (OSCILLATE):** The particle at `i, i+1` with state `'01','10'` flips its internal state to `'10','01'` while remaining at positions `i, i+1`.
    b. **Step 2 (MOVE):** The particle at `i, i+1` with state `'10','01'` moves to `i+1, i+2` and resets its state back to `'01','10'`.

2.  **Rule Construction:** Implement a local, reversible, and bit-conserving rule that produces these dynamics for an isolated particle. The rule should consist of specific mappings for the few non-zero neighborhoods required to create the dynamics, with all other neighborhood states mapping to themselves (identity).

3.  **Simulation Setup:**
    a. Initialize a lattice of size 100 with all cells set to `'00'`.
    b. Set the initial condition by placing the particle at the start: cell 20 = '01', cell 21 = '10'.
    c. Run the simulation for 100 steps.

4.  **Analysis and Output:**
    a. Track the "center of mass" of the '1' bits that constitute the particle.
    b. Create `archive/iter_006/result.yaml` with the following keys:
       - `behavior_class`: `COMPOSITE_GLIDER` if successful, otherwise `DECAY`, `CHAOTIC`, or `STATIONARY_OSCILLATOR`.
       - `effective_velocity`: The calculated average velocity.
       - `is_stable`: A boolean, `true` if the two-cell pattern remains contiguous and does not shed bits.
       - `final_position`: The final center of mass of the particle.


## Success Criteria

- The particle's effective velocity is between 0.49 and 0.51.
- The `is_stable` flag in the result is `true`, indicating the particle did not decay.
- The final pattern is identical to the initial one, just shifted.

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
