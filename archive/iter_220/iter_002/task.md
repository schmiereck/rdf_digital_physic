**Goal:** Characterize the champion rule found by the evolutionary search in sub-task 220.1 to determine if it produces a true `v<c` glider.

**Context:** The planner in 220.1 found a champion rule in `archive/iter_220/results/champion_rule.json`. However, since this rule was found in generation 0 and never surpassed, we must verify if it represents genuine progress or just a stable, non-moving particle.

**Task:**
1.  **Create a new Python script:** `src/characterize_champion_220.py`.
2.  **Load the Champion Rule:** The script must load the rule from `archive/iter_220/results/champion_rule.json`.
3.  **Run a Long Simulation:**
    *   Grid size: 256x256 (torus).
    *   Seed: Standard 3-bit L-tromino.
    *   Duration: 2000 steps.
4.  **Perform Analysis:**
    *   **Bit Conservation:** Verify that the bit count remains exactly 3 for all 2000 steps.
    *   **Velocity:** Calculate the particle's velocity over multiple 400-step windows to check for consistency and ensure `v < 1.0`.
    *   **Behavior:** Describe the particle's motion qualitatively. Is it a glider, an oscillator, or something else?
5.  **Produce Outputs:**
    *   **Report:** Write the analysis results (bit conservation status, average velocity, qualitative description) to `archive/iter_220/results/characterization_report.txt`.
    *   **Animation:** Generate an animation of the first 500 steps of the simulation and save it as `archive/iter_220/results/champion_animation.gif`.