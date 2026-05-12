
Create a new script `src/test_long_run_motion.py`.

This script will perform a long-duration simulation of the top-evolved rule from iter_131 to verify if its motion is sustained.

**1. Setup:**
   - Load the rule from `archive/iter_131/population/rule_011.json`.
   - Load the initial grid state from the canonical ash pattern file, `src/ash_pattern.json`.
   - The grid should be large enough to accommodate movement over 1000 steps (e.g., 200x200 with wrapping boundaries).

**2. Simulation and Data Logging:**
   - Run the simulation for a total of 1000 steps.
   - At every 20 steps (i.e., step 0, 20, 40, ..., 1000), record the following metrics:
     - Step number
     - Total number of live cells (bit count)
     - Number of distinct connected components (object count)
     - Center of mass (q, r coordinates)
   - Save this time-series data to a CSV file at `archive/iter_132/results/long_run_metrics.csv`.

**3. Analysis and Reporting:**
   - After the simulation, calculate the total displacement of the center of mass from its initial position at step 0 for each recorded time point.
   - Identify the displacement at step 200 and step 1000.
   - Determine if motion was sustained. The criterion for sustained motion is: `displacement_at_1000_steps > 4.5 * displacement_at_200_steps`.

**4. Final Output:**
   - The script must terminate by writing a `result.yaml` file to `archive/iter_132/result.yaml`. This file must contain the following keys:
     - `status`: 'ok' if the script ran to completion.
     - `metrics`: A dictionary with these keys:
       - `initial_bit_count`: The bit count at step 0.
       - `final_bit_count`: The bit count at step 1000.
       - `remnant_stable`: A boolean, true if the bit count at step 1000 is within 5% of the bit count at step 200.
       - `displacement_at_200_steps`: The displacement value at step 200.
       - `displacement_at_1000_steps`: The displacement value at step 1000.
       - `motion_sustained`: A boolean, true if the sustained motion criterion was met.
     - `experimenter_view`: A textual description of the results, noting whether the displacement grew linearly and if the remnant's form was stable.
