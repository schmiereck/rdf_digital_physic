# Task – iter_090

**Hypothesis:** A motion-based fitness metric, `displacement / (1 + final_bit_count)`, will assign zero fitness to known chaotic, annihilating, and still-life rules.

## Working Directory

Your working directory is `src/` – a **persistent** directory shared across all iterations. Build on code from previous iterations; do not start from scratch each time.
Write results and data files to `archive/iter_090/results/` (relative to the project root).

## Task

Create a new script, `src/validate_motion_fitness_metric.py`, to test a new fitness function.

**1. Implement the Motion-Based Fitness Function:**
- The function takes a rule file as input.
- It initializes a 150x150 grid with a single 4-bit contiguous "T-shape" seed.
- It simulates for 500 steps, tracking the history of pattern configurations (sorted coordinates) and bit counts to detect a cycle.
- **Fitness Calculation:**
  - If no cycle is detected within 500 steps, or if the pattern decays to 0 bits, the fitness is 0.
  - If a cycle is detected, calculate the net displacement of the object's center of mass over one full period.
  - `fitness = displacement / (1 + final_bit_count)`, where `final_bit_count` is the bit count of the stable, cyclic object.

**2. Test on Known Rule Archetypes:**
The script will evaluate three specific rules to validate the metric's selectivity:
a. **Chaotic Rule:** The top-fitness rule from Gen-2, known to be explosive (`archive/iter_084/population/rule_023.json` from iter_085).
b. **Annihilating/Stabilizing Rule:** The best non-annihilating rule from Gen-3 (`archive/iter_088/population/rule_015.json` from iter_089).
c. **Classic Still-Life Rule:** The original non-conserving rule (`src/symmetric_rule_nonconserving_A3_B14.json` from iter_069).

**3. Report Results:**
Create `archive/iter_090/result.yaml` with the following keys:
- `chaotic_rule_score`: The new fitness score for the chaotic rule.
- `stabilizing_rule_score`: The new fitness score for the Gen-3 stabilizing rule.
- `still_life_rule_score`: The new fitness score for the classic still-life rule.
- `metric_is_selective`: `true` if all three scores are 0 (or < 1e-6 for the chaotic rule), `false` otherwise.


## Success Criteria

- The chaotic rule (from iter_085) achieves a fitness score < 1e-3.
- The stabilizing rule (from iter_089) achieves a fitness score of 0.
- The classic still-life rule (from iter_069) achieves a fitness score of 0.

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
