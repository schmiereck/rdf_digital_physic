Run a multi-step investigation to probe and characterize stable gliders under:
1. The sub-light speed glider rule from `archive/iter_222/results/champion_rule_perfect.json` (uses DisplacementConsistencyFitness).
2. The elastic collision rule from `archive/iter_193/iter_002/results/champion_rule.json` (uses RecessionBiasedFitness).

For each rule:
- Write and run a python script `src/probe_gliders_223.py` to test different 3-bit and 4-bit contiguous seeds (including all rotations/reflections/orientations).
- Run each seed for 200 steps on a 128x128 grid.
- Track step-by-step active cell counts and COMs, and calculate:
  - If the pattern preserves its initial bit count exactly at step 200 (or oscillates with a small period).
  - The mean speed (displacement per step, properly unwrapped).
  - The consistency of speed (standard deviation of velocity magnitudes across 5 windows).
- Classify stable, moving structures:
  - v=1c glider if speed is near 1.0 (e.g. > 0.9)
  - v<c glider if speed is sub-light (e.g. 0.1 to 0.9)
- Save a JSON summary file to `archive/iter_223/results/glider_probe_results.json`.
- Summarize the results clearly. Specifically, does either rule support BOTH a v<c glider and a v=1c glider? If so, which seeds produce them?