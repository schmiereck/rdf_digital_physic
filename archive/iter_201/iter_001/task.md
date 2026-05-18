Create a Python script `src/characterize_v_lt_c_glider.py`. This script must perform a detailed analysis of the `v<c` glider discovered in `iter_200`.

**Requirements:**

1.  **Load the correct rule:** The script must load the champion rule from `archive/iter_200/results/champion_v_lt_c_rule.json`.
2.  **Use the standard seed:** Initialize the simulation with the 3-bit 'L-tromino' seed particle at the center of a 128x128 toroidal grid.
3.  **Run a long simulation:** Simulate for 1024 steps to gather sufficient data.
4.  **Perform quantitative analysis:** For each step, calculate and record:
    *   The center of mass (CoM) of the particle.
    *   The total number of active bits (to verify conservation).
    *   A hash of the particle's state relative to its CoM (to detect periodicity).
5.  **Calculate and report key metrics:** After the simulation, compute:
    *   **Average Velocity:** Calculate the mean velocity vector over the last 512 steps.
    *   **Period:** Identify the period of internal oscillation by finding the cycle length in the recorded state hashes.
6.  **Output results:**
    *   Save the per-step data (step, CoM_x, CoM_y, bit_count, state_hash) to `archive/iter_201/results/glider_timeseries.csv`.
    *   Print the final calculated velocity and period clearly to stdout.
7.  **Dependencies:** The script should rely on existing libraries and helpers in the `src/` directory (`src/ca_hex.py`, `src/rules.py`, etc.).