# Task – iter_058

**Hypothesis:** search-next-w3-rule: The second valid W=3 kernel produces a rule that supports at least one stable, bit-conserving, non-trivial 3-bit object.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_058/results/` (relative to the project root).

## Task

This is a two-part task: first find the next valid kernel, then test it.

**Part 1: Find the Second W=3 Kernel**
1. Create a script `src/find_next_w3_kernel.py`.
2. This script must search for state-pairs `(A, B)` at Hamming Weight 3 that satisfy all four established conditions: Center-Bit Flip, Disjoint Orbits, Conflict-Free Closure, and Contiguity.
3. The script must find and **ignore** the first valid kernel (`A=7, B=14`) and then find and report the **second** valid kernel.
4. The script should print the integers and binary strings for this second kernel pair to stdout for verification.

**Part 2: Generate Rule and Search for Objects**
1. Create a script `src/generate_and_search_w3.py`.
2. This script must programmatically take the new kernel pair `(A2, B2)` from Part 1 as input.
3. It must generate the full 6-fold symmetric rule and save it to `src/symmetric_rule_w3_next.json`.
4. It must then systematically test all 11 unique, contiguous 3-bit seeds for stability under this new rule.
5. For each seed, simulate for up to 200 steps, checking for bit-conservation and cyclic behavior.
6. The script should stop as soon as it finds the *first* stable object (still life, oscillator, or glider).
7. The script's final action must be to create `archive/iter_058/result.yaml` with the results of the search.

**YAML Output for iter_058:**
- `kernel_A`: The integer `A2` used.
- `kernel_B`: The integer `B2` used.
- `object_found`: `true` if a stable 3-bit object was found, `false` otherwise.
- `patterns_checked`: The number of 3-bit seeds tested before finding an object.
- `object_type`: `STILL_LIFE`, `OSCILLATOR`, or `GLIDER`.
- `object_period`: The period of the found object.
- `net_displacement`: The net displacement of the object's center of mass over one period.


## Success Criteria

- The `find_next_w3_kernel.py` script successfully identifies a second valid W=3 kernel.
- The `generate_and_search_w3.py` script completes its search and produces a result.yaml.
- The `object_found` key in the result indicates whether any stable 3-bit configuration exists for the new rule.

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
