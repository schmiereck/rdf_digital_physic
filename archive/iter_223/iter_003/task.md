Write a python script `src/search_mixed_glider_rules.py` to search through the archived rule files for a rule that supports BOTH a stable, bit-conserving v<c glider and a stable, bit-conserving v=1c glider.

The script should search:
- `archive/iter_215/results/champion_rule.json`
- All rules in `archive/iter_215/results/final_population.json`
- All rules in `archive/iter_215/results/warm_start_population.json`
- `archive/iter_218/results/champion_rule.json`
- `archive/iter_218/results/champion_vc_rule.json`
- `archive/iter_221/results/champion_rule.json`
- `archive/iter_221/results/champion_rule_perfect.json`
- `archive/iter_221/results/champion_rule_unwrapped.json`
- `archive/iter_221/results/champion_vc_rule.json`
- `archive/iter_222/results/champion_rule_perfect.json`

For each rule, test all 11 contiguous 3-bit seeds and 44 contiguous 4-bit seeds for 200 steps on a 128x128 grid.
A glider is defined as:
- Perfect size conservation (final_bit_count == initial_bit_count).
- A stable, repeating period (period is detected and <= 20).
- Consistent velocity (velocity magnitude std_dev across 5 windows < 0.05).
- v<c glider: mean speed between 0.1 and 0.9.
- v=1c glider: mean speed > 0.9c (usually speed is around 1.0 in hex-steps, or around 1.34-1.42 in Euclidean coordinates).

Write the results of all discovered matching rules (rules supporting both) to `archive/iter_223/results/found_mixed_rules.json`. If none are found, search for rules that support both but allow a small bit error (e.g. final_bit_count is within +/- 1 of initial_bit_count) and save those as "leaky" mixed rules.
Run the script and output the summary.