
The primary goal is to perform a long-run analysis of the current champion rule (`rule_049` from iter_140) to determine if its high fitness score corresponds to sustained, coherent motion or a chaotic explosion.

**Methodology:**

1.  **Load Assets:**
    *   Load the champion rule: `archive/iter_140/results/rules/rule_049.json`.
    *   Load the initial ash pattern: `src/ash_pattern.json`.
    *   Load the target object definitions from the local fitness configuration used in the previous iterations.

2.  **Simulation:**
    *   Run the simulation for **1000 steps** on the local target region defined by the ash pattern and the target objects.
    *   The grid must be large enough to prevent boundary interactions for the duration of the run. A 200x200 grid with wrapping boundaries should be sufficient.

3.  **Data Logging and Analysis:**
    *   Create a time-series log file: `archive/iter_141/results/motion_log.csv`.
    *   Every **20 steps**, record the following data to the log: `step,live_cell_count,com_q,com_r,total_displacement`.
    *   Calculate two velocities:
        *   `velocity_early`: The average velocity (displacement per step) between step 100 and step 500.
        *   `velocity_late`: The average velocity between step 500 and step 900.
    *   Calculate a `velocity_decay_ratio = velocity_late / velocity_early`. A ratio close to 1.0 indicates sustained motion. A ratio close to 0.0 indicates the motion stopped.
    *   Determine `sustained_motion` boolean: `True` if `velocity_decay_ratio > 0.8` AND the final bit count is less than 3x the initial bit count.

4.  **Visualization Snapshots:**
    *   Save snapshots of the local grid state as text files at key steps: `t=0, 200, 400, 600, 800, 1000`.
    *   Place these files in a directory: `archive/iter_141/results/frames/`. Name them `frame_0000.txt`, `frame_0200.txt`, etc.

5.  **Final Report:**
    *   The `metrics` in the final YAML block must include:
        *   `initial_bit_count`: The bit count of the target objects at step 0.
        *   `final_bit_count`: The bit count at step 1000.
        *   `final_displacement`: The total displacement of the center of mass at step 1000.
        *   `velocity_decay_ratio`: As calculated above.
        *   `sustained_motion`: The final boolean determination.
    *   The `experimenter_view` should clearly state whether the motion is coherent and glider-like or explosive and chaotic, based on the logged data and your observations.
