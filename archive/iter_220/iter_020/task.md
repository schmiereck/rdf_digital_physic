1. Write a python script src/test_rebuilt_glider.py that:
   - Loads the original 179 champion rule.
   - Extracts its generator pairs.
   - Rebuilds the rule using _try_build_c2_rule with those pairs.
   - Runs a 200-step simulation of both rules from the L-tromino seed.
   - Checks if they have 100% identical center of mass and active cells at every step.
2. Run the script and print its output.