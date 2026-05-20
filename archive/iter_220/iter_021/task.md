Characterize the new consistency champion rule from `archive/iter_220/results/champion_vc_rule_consistency.json`:
1. Load the rule dict from the JSON.
2. Run a 500-step simulation on a 128x128 toroidal grid with the 3-bit L-tromino seed.
3. Measure and record: CoM, active cell count, displacement, and step velocity.
4. Detect its period of oscillation and canonical shapes.
5. Classify the motion (STATIONARY, OSCILLATING, MOVING/GLIDER) and determine its exact average velocity `v`.
6. Verify if it is a true, stable `v<c` glider that perfectly or near-perfectly conserves its size without growing or breeding.
7. Save the detailed trajectory analysis to `archive/iter_220/results/trajectory_log_consistency.txt` and create an animated GIF of its propagation if possible.