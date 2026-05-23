Run the rigorous glider audit to test and group all 163 candidate glider files and the reference LUT-08 glider under the full 48-element O_h group.
1. Run `python3 src/rigorous_glider_audit.py`.
2. Inspect the terminal output of the audit to verify how many unique O_h orbits are found, whether the symmetry checker successfully groups candidates, and whether any STABLE gliders are disjoint from the LUT-08 orbit.
3. If there are issues, fix `src/rigorous_glider_audit.py` or the symmetry transformations, and run again.
4. Return the summary statistics from the run.