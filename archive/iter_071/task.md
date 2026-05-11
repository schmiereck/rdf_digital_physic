# Task – iter_071

**Hypothesis:** update-model-2phase: A 2-phase (checkerboard) update schedule enables glider propagation for the non-conserving rule (A=3, B=14) with a 4-bit seed.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_071/results/` (relative to the project root).

## Task

1. Create a new script `src/simulate_2phase.py`.
2. Load the non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json`.
3. Implement a 2-phase update schedule based on a checkerboard coloring of the hex grid. A cell at `(q, r)` has color `(q + r) % 2`.
4. The simulation loop should consist of 2 phases per "full step":
   - Phase 0: Compute and apply updates for all color=0 cells.
   - Phase 1: Compute and apply updates for all color=1 cells based on the grid state after Phase 0.
5. Perform an exhaustive search for gliders using all 10 unique, one-sided contiguous 4-bit tetrahex seeds.
6. For each seed, simulate for 400 full steps (i.e., 800 phases).
7. Track stability (object enters a cycle with bit_count > 0) and net displacement.
8. Create `archive/iter_071/result.yaml` with the standard glider-search keys: `glider_found`, `patterns_checked`, `stable_object_count`, `decayed_seed_count`, `glider_period`, and `glider_velocity_hex`.


## Success Criteria

- The `glider_found` key in result.yaml is `true`.
- At least one stable object is found with a non-zero net displacement over its cycle period.

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
