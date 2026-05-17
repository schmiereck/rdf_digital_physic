Your task is to write a standalone Python script, `src/characterize_glider.py`, to analyze the champion rule found in `200.1`. Do NOT execute the script.

**Script Requirements:**

1.  **File:** Create the script at `src/characterize_glider.py`.
2.  **Functionality:** The script should, when run, perform the following actions:
    *   Load the rule from `archive/iter_200/results/champion_v_lt_c_rule.json`.
    *   Initialize a 256x256 hexagonal grid with the 3-bit L-tromino seed.
    *   Run a 2000-step simulation.
    *   Track the bit count and center-of-mass (CoM) at each step.
    *   Calculate the average velocity over the last 1000 steps (1000-2000).
    *   Determine the period of the glider's shape oscillation.
    *   Check for perfect bit conservation over all 2000 steps.
    *   Save the results to `archive/iter_200/results/glider_properties.json` with keys `velocity_vc`, `period`, and `is_stable`.
    *   Generate a plot of the CoM trajectory (X and Y vs. time) and save it to `archive/iter_200/results/trajectory.png`.
3.  **Imports:** Use existing project utilities from `src.grid` and `src.rule` where possible.
4.  **Execution:** The script should be runnable from the project root via `python -m src.characterize_glider`.

Your sole output is the created script file `src/characterize_glider.py`. You do not need to run it.