Write and run a script `src/analyze_glider_240.18.py` to analyze Class 163 (LUT-08) simulation over 200 steps.
The script must:
1. Load the reference glider particle from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Simulate it using the exact same logic as `rigorous_glider_audit.py` (L=32, steps=200).
3. At each step, print the active bit count and bounding extent.
4. If it becomes unstable, identify the exact step and reason (e.g. bit count change or extent > 6).
5. Also, do the same simulation on a larger grid (e.g. L=64 or L=128) to verify if the "instability" is simply a toroidal wrapping artifact on the small L=32 grid!
6. Save the results and print the summary.