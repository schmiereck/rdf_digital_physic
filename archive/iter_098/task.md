# Task – iter_098

**Hypothesis:** soup-stability: A rule known to produce only still-lifes from small seeds will resolve a chaotic soup into a low-density state of persistent objects.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_098/results/` (relative to the project root).

## Task

Create a new script, `src/test_stable_rules_in_soup.py`.

1. **Identify Candidate Rules:**
   - Load the full multi-seed evaluation results for the 100 C2-symmetric rules from `archive/iter_095/results/c2_random_multiseed_scores.csv`.
   - From this data, identify the subset of rules that, across all 21 tested seeds, produced *only* still-lifes or decayed patterns. Exclude any rule that produced an oscillator or an explosion. These are the "stably boring" candidates.

2. **Evaluate Candidates in Soup:**
   - For each of the identified candidate rules:
     a. Initialize a 150x150 grid with 25% random noise (a "soup"). Use the same fixed random seed for the noise pattern as in iter_097 to ensure comparability.
     b. Simulate for 1000 steps.
     c. At step 1000, record the final number of live cells (`final_bit_count`).

3. **Classify and Report:**
   - After evaluating all candidates, classify each rule's outcome based on its `final_bit_count`:
     - `DEAD`: `final_bit_count` < 20
     - `CHAOTIC`: `final_bit_count` > 1000
     - `INTERESTING`: 20 <= `final_bit_count` <= 1000
   - Create `archive/iter_098/result.yaml` with the following keys:
     - `candidates_found`: The number of "stably boring" rules identified from the iter_095 population.
     - `dead_rules_count`: The number of candidates classified as DEAD.
     - `chaotic_rules_count`: The number of candidates classified as CHAOTIC.
     - `interesting_rules_count`: The number of candidates classified as INTERESTING.
   - Create a text file `archive/iter_098/results/interesting_rules.txt` and list the filenames of all rules classified as INTERESTING, one per line.


## Success Criteria

- interesting_rules_count >= 1

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
