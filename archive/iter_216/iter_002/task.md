The previous attempt to characterize the v<c glider (iter_216.1) was blocked by platform errors. This task is a direct retry to confirm platform stability and perform a basic characterization.

1.  **Load Rule:** Load the champion rule from `archive/iter_215/results/champion_rule.json`.
2.  **Load Seed:** Use the standard 3-bit L-tromino particle as the initial seed.
3.  **Run Simulation:** Execute a simulation for 500 steps on a 256x256 grid.
4.  **Log Data:** Record the bit count and center of mass at every step.
5.  **Calculate Metrics:** At the end of the simulation, calculate and report the following:
    *   Initial and final bit count (to confirm conservation).
    *   Net displacement of the center of mass between step 250 and step 500.
    *   Average velocity (displacement / steps) over this window.
6.  **Artifacts:** Save the simulation logs and calculated metrics to `archive/iter_216/results/characterization.json`.

The primary success criterion is the successful completion of the simulation without platform errors. The secondary goal is to obtain the first quantitative data on the new glider.