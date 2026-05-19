**Goal:** Diagnose the simulation environment with a minimal task.

**Task:**
1.  Create a new Python script `src/diag_sim.py`.
2.  The script should perform the simplest possible simulation run:
    *   Load the "still_life" rule from `archive/iter_056/results/rule_1.json`.
    *   Initialize a `Simulation` object with this rule on a small 32x32 grid.
    *   Run the simulation for only **10 steps**.
    *   Use the standard 3-bit L-tromino as the seed.
    *   Print "Minimal simulation diagnostic complete." upon successful completion.
3.  Execute the script.

**Success Criterion:** The script must run quickly (under 30 seconds) and terminate with the success message. If it hangs or fails, it points to a fundamental problem in the core simulation libraries.