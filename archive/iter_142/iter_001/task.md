### Task: Evolve Gen-4 with a Stringent Late-Late-Displacement Metric

**Context:**
The previous evolutionary champion (rule_049 from iter_140) was revealed to be a "false positive" in iter_141. Its high fitness score was due to a one-time transient expansion that completed by step 400, not sustained motion. This experiment will re-run the evolution with a much more stringent fitness metric to select for genuine, long-term motion.

**Instructions:**

1.  **Create a new evolution script:** Copy the last evolution script (`src/evolve_quadratic_local_ash.py` seems to be the latest variant based on recent iterations) to a new file: `src/evolve_sustained_motion.py`.

2.  **Modify the fitness evaluation:** In the new script, make the following critical changes:
    *   Increase the total simulation steps from 200 to **800**.
    *   Change the fitness evaluation window. The displacement should be calculated between the Center of Mass (COM) at **step 400** and the COM at **step 800**.
    *   Keep the quadratic fitness formula from recent experiments: `fitness = displacement_400_800 / (1 + (bit_ratio - 1)**2)`.

3.  **Set up the evolutionary run:**
    *   **Parents:** Use the top 5 best rules from the Gen-3 population, located in `archive/iter_140/results/population/`.
    *   **Population Size:** Generate a new population of 100 rules (Gen-4).
    *   **Initial Condition:** Use the standard `src/ash_pattern.json`.

4.  **Execute and Save Results:**
    *   Run the `src/evolve_sustained_motion.py` script.
    *   Save the resulting Gen-4 population to `archive/iter_142/results/population/`.
    *   Save the summary statistics (mean fitness, top fitness, number of viable rules, etc.) to `archive/iter_142/results/summary.json`.

**Success Criteria:**
The script completes successfully, and the `summary.json` file contains the results for the Gen-4 population evaluated under the new 400-800 step metric.
