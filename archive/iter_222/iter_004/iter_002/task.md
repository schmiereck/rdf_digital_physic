Fix the projection bug in `src/run_evolution_exp_222.py` and run the corrected C2-symmetric evolutionary search.

Specifically:
1. Replace `rule_dict_to_chromosome_72` with the correct logic that detects if any member of an orbit is in the `rule_dict`, and if so, flips the default center bit of the orbit:
```python
def rule_dict_to_chromosome_72(rule_dict: dict) -> np.ndarray:
    chrom = np.zeros(NUM_ORBITS, dtype=np.uint8)
    members_per_orbit = [[] for _ in range(NUM_ORBITS)]
    for s in range(LUT_SIZE):
        members_per_orbit[ORBIT_IDX_OF_STATE[s]].append(s)
    for i, members in enumerate(members_per_orbit):
        default_c = (ORBIT_REPS[i] >> 6) & 1
        any_in_rule = any(s in rule_dict for s in members)
        if any_in_rule:
            chrom[i] = 1 - default_c
        else:
            chrom[i] = default_c
    return chrom
```
2. Run a test where you load the warm-start rules from `archive/iter_215/results/final_population.json`, project them using the corrected function, and print/evaluate their fitnesses. Verify that we now get non-zero, high-fitness scores!
3. Run the full evolutionary search in parallel using ProcessPoolExecutor for 50 generations with population size 100, elite size 10, crossover rate 0.5, and bit-flip mutation rate 0.02.
4. Verify and characterize the champion glider over 500 steps to ensure it is a stable, genuine sub-light speed (v < c) glider.
5. Generate the outputs in `archive/iter_222/results/`:
   - `champion_rule_perfect.json`
   - `evolution_summary_perfect.csv`
   - `champion_vc_glider_perfect.gif`
   - `trajectory_analysis.txt`
   and verify that the champion has high fitness (ideally > 1.0 or 2.0).