# Task – iter_074

**Hypothesis:** re-evaluation: The C6 non-conserving rule (A=3↔B=14) does produce a stable, 4-bit glider, correcting the negative result from iter_069.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_074/results/` (relative to the project root).

## Task

This is a re-run of the experiment from iter_069 with extended simulation time and a focus on careful analysis to resolve a critical contradiction.

1. **Load Rule:** Load the full C6-symmetric, non-conserving rule from `src/symmetric_rule_nonconserving_A3_B14.json` (kernel A=3↔B=14, 12 non-identity mappings).
2. **Generate Seeds:** Use the exact same 10 unique, one-sided contiguous 4-bit patterns (tetrahexes) as in iter_069.
3. **Test Each Seed:** For each of the 10 seeds:
    a. Initialize a grid (e.g., 150x150) with the pattern.
    b. Simulate for **1000 steps** to ensure detection of slow-moving objects or long transients.
    c. A seed's evolution is a **stable object** if it enters a finite cycle with a bit_count > 0.
    d. For any stable object, meticulously calculate the net displacement of its center of mass over one full cycle period. A non-zero displacement indicates a glider.
4. **Report Results:** Create `archive/iter_074/result.yaml`. The `outcomes` field is critical for detailed analysis.
5. **YAML Output:**
    - `glider_found`: boolean
    - `patterns_checked`: 10
    - `glider_seed_index`: The 0-based index of the seed that produced the glider, or -1.
    - `glider_period`: Period of the glider, or 0.
    - `glider_velocity_hex`: (dq, dr) tuple, or (0,0).
    - `outcomes`: A list of strings, one for each seed, detailing its fate. For any glider, include its period and velocity. E.g., "Seed 7 (bent-shape): GLIDER, period 24, velocity (0.166, 0.083)".


## Success Criteria

- At least one of the 10 seeds results in a stable object with a non-zero net displacement over its cycle period.
- The final result.yaml definitively states whether a glider was found or not, resolving the contradiction.

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
