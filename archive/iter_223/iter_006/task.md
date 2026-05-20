Write a python script `src/test_vc_collision.py` that implements a collision simulation between two sub-light gliders (v=0.469c) under Rule A (champion_rule_perfect.json from archive/iter_222/results/).

The script should:
1. Load champion_rule_perfect.json.
2. Initialize a 128x128 toroidal grid.
3. Glider A (moves NW, row decreasing, col increasing) is placed at (80, 48): cells [(80, 48), (81, 48), (81, 49)].
4. Glider B (moves SE, row increasing, col decreasing) is placed at (48 + offset, 80 + offset): cells [(r, c), (r-1, c), (r-1, c-1)] where r = 48 + offset, c = 80 + offset.
5. Simulate for 200 steps for transverse offsets from -4 to +4.
6. Record: initial/final bit counts, max bit count achieved, and save the quantitative results to archive/iter_223/results/collision_results.json.
7. Save the 0-offset head-on collision sequence to a GIF: archive/iter_223/results/head_on_collision.gif.

Write the code to `src/test_vc_collision.py` and execute it. Make sure to import all required libraries (numpy, json, PIL/imageio for GIF, math, pathlib).