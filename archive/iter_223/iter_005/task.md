Create and execute a python script src/test_vc_collision.py that performs systematic collision experiments between two sub-light gliders (v=0.469c) under Rule A (champion_rule_perfect.json from archive/iter_222/results/).

Details:
1. Load champion_rule_perfect.json.
2. Initialize a 128x128 toroidal grid.
3. Glider A (moves NW) is placed at (80, 48): cells [(80, 48), (81, 48), (81, 49)].
4. Glider B (moves SE) is placed at (48 + offset, 80 + offset): cells [(r, c), (r-1, c), (r-1, c-1)] where r = 48 + offset, c = 80 + offset.
5. Simulate for 200 steps for transverse offsets from -4 to +4.
6. For each offset, record:
   - initial/final bit counts
   - max bit count achieved (any step)
   - final state classification (extinct, stable remnant, chaotic, or elastic scatter)
   - whether the gliders survived the collision or destroyed each other.
7. Save the quantitative results to archive/iter_223/results/collision_results.json.
8. For the 0-offset head-on collision, generate a clean GIF animation showing the collision sequence and save it to archive/iter_223/results/head_on_collision.gif.
9. Print a clear text summary of the findings.