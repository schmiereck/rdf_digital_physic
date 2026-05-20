Write a python script `src/probe_gliders_223.py` to systematically search for all stable gliders supported by (1) the sub-light rule from `archive/iter_222/results/champion_rule_perfect.json` and (2) the elastic collision rule from `archive/iter_193/iter_002/results/champion_rule.json`.
Test all possible 3-bit and 4-bit contiguous seeds (including all rotations/translations on a hexagonal lattice). Run each for 200 steps on a 128x128 grid.
Track:
- Whether the particle remains stable (bit count remains small, e.g. <= 8 bits).
- The speed of propagation. Identify if any move at v=1c (speed close to 1.0) and others at v<c (sub-light, e.g. speed between 0.1 and 0.9).
- The exact seed and trajectory.
Write a summary JSON file to `archive/iter_223/results/glider_probe_results.json` detailing all discovered gliders for each rule, their velocities, and their periods. Run the script and report the findings.