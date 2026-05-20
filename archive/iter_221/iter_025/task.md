Modify src/new_fitness.py to unwrap center-of-mass coordinates.
Specifically:
1. Locate where 'sorted_history = sorted(sim_history, key=lambda e: e["step"])' is defined in src/new_fitness.py (around line 222).
2. Insert the unwrapping code right after that line, replacing or modifying sorted_history so that it contains the unwrapped 'com' coordinates.
3. Write a python script to verify that the edit is correct by running 'run_champion_eval.py' (or a similar check) on the v=1c champion. Under the unwrapped fitness, its calculated mean velocity should be close to 1.0, and its final fitness should be 0.0 (rejected).
4. Run the validation and print the output. Do not output yaml block.