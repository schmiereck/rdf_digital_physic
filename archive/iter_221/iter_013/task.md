1. Analyze the champion rule from archive/iter_221/results/champion_rule.json.
2. Simulate it for 500 steps starting with L_TROMINO_3bit seed on a 128x128 grid.
3. Track and print:
   - Final bit count and max bit count during the run
   - Bounding box size (max width/height) during the run
   - Unwrapped center-of-mass coordinates at t=0, 100, 200, 300, 400, 500
   - Velocity vector and speed (cells/step)
   - Period detection: does it repeat its shape with a translation? If so, what is the period T?
4. Save the characterization report to archive/iter_221/results/trajectory_analysis.txt. Print the report to stdout.