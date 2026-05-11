# Task – iter_097

**Hypothesis:** from-chaos: At least one 'dense' C2 rule from iter_096, when seeded with random noise, will resolve into a low-density state of persistent, non-chaotic objects.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_097/results/` (relative to the project root).

## Task

Create a new script, `src/filter_soup_rules.py`, to identify promising rules from the "dense" C2 population generated in the previous (failed) iteration.

1. **Load Rules:** Load all 100 "dense" C2-symmetric rules from the `archive/iter_096/population/` directory.

2. **Evaluate Each Rule:** For each of the 100 rules:
   a. Initialize a 150x150 grid with 25% random noise (a "soup"). Use a fixed random seed for reproducibility.
   b. Simulate for 1000 steps.
   c. At step 1000, record the final number of live cells (`final_bit_count`).

3. **Classify and Report:** After evaluating all rules, analyze the distribution of `final_bit_count`.
   a. Classify each rule based on its `final_bit_count`:
      - `DEAD`: `final_bit_count` < 20
      - `CHAOTIC`: `final_bit_count` > 1000
      - `INTERESTING`: 20 <= `final_bit_count` <= 1000
   b. Create `archive/iter_097/result.yaml` with the following keys:
      - `dead_rules_count`: The number of rules classified as DEAD.
      - `chaotic_rules_count`: The number of rules classified as CHAOTIC.
      - `interesting_rules_count`: The number of rules classified as INTERESTING.
   c. Create a text file `archive/iter_097/results/interesting_rules.txt` and list the filenames of all rules classified as INTERESTING, one per line. If none are found, this file should be empty.


## Success Criteria

- At least one rule is classified as INTERESTING.
- The script successfully evaluates all 100 rules without crashing.

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
