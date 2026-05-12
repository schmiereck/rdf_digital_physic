
## Task: Long-Run Verification of Champion Rule `rule_016`

This experiment will verify if the motion produced by the current champion rule (`rule_016` from iter_142) is sustained over a long simulation.

### 1. Setup
- Load the canonical initial state from `src/ash_pattern.json`.
- Load the champion rule from `archive/iter_142/results/gen_4_rules/rule_016.json`.
- Use a sufficiently large grid (e.g., 400x400) with wrapping boundaries to prevent self-interaction.

### 2. Simulation and Measurement
- Run the simulation for a total of **2000 steps**.
- During the simulation, record the center of mass (COM) at steps 400, 800, 1200, and 1600.
- Calculate the displacement during the original fitness window: `disp_400_800 = distance(COM_800, COM_400)`.
- Calculate the displacement during a later window: `disp_1200_1600 = distance(COM_1600, COM_1200)`.
- Calculate the velocity decay ratio: `velocity_ratio = disp_1200_1600 / disp_400_800`. Handle the case where the denominator is zero.

### 3. Output
- Save all raw metrics to a JSON file at `archive/iter_143/results/long_run_metrics.json`.
- The final YAML report printed to standard output must include the following structure:

```yaml
status: ok
artifacts:
  - "archive/iter_143/results/long_run_metrics.json"
metrics:
  disp_400_800: <float>
  disp_1200_1600: <float>
  velocity_ratio: <float>
  final_bit_count_at_2000: <int>
  motion_sustained: <bool> # True if velocity_ratio >= 0.9, False otherwise
log_excerpt: |
  ...
experimenter_view: |
  A qualitative summary of the findings. Was the motion sustained? Did the velocity decay? Was the simulation stable?
notes: "Long-run verification for rule_016 from iter_142 complete."
```
