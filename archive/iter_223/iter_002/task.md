Search through all previous final population files and champion files of sub-light speed glider campaigns (specifically look in directories like `archive/iter_215/results/`, `archive/iter_218/results/`, `archive/iter_221/results/`, `archive/iter_222/results/` for JSON files containing populations or rules) to find any rule that supports BOTH:
1. A stable v<c glider (speed between 0.1 and 0.9 with perfect bit conservation, such as the L-tromino).
2. A stable v=1c glider (speed > 0.95 with perfect bit conservation, using any other 3-bit or 4-bit seed).

If you find any such rule:
- Identify the exact seeds and orientations that produce the v<c glider and the v=1c glider under that rule.
- Run a collision simulation between them on a 128x128 grid for at least 300 steps. Try different relative velocities, offsets, and initial distances to see if you can find any elastic or bit-conserving collisions.
- Save the rule and the collision metrics/results to `archive/iter_223/results/mixed_collision_results.json`.
- If no such rule exists in the archives, try to run a brief evolutionary search using a combined fitness function that rewards a rule for supporting BOTH a v<c glider (e.g. from the L-tromino) AND a v=1c glider (e.g. from a straight 3-bit tromino), and then search for collisions.
Summarize your findings in detail.