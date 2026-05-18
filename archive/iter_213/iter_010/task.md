**Goal:** Discover a stable, `v<c` (sub-light speed) glider using evolutionary search.

**Context:** The platform is now stable. This task is to finally solve the long-standing `v<c` glider problem. All previous attempts (`iter_201`, `203`, `204`) failed due to fitness function exploits. You must build upon those lessons.

**Your Task as a Planner:**
1.  **Review Past Failures:** Systematically review the findings from `iter_201` ("phase-sampling flaw"), `iter_203` ("puffer" and "oscillator" exploits), and `iter_204` (development of a robust fitness function).
2.  **Formulate a Robust Search Strategy:** Design an evolutionary search plan that explicitly uses the final, most robust fitness function, which incorporates `net_displacement` to defeat known exploits.
3.  **Execute the Search:** Launch the evolutionary run. This may take several generations.
4.  **Identify and Characterize the Champion:** Once the search converges, identify the champion rule. Perform a rigorous characterization to confirm it is a true, stable `v<c` glider and not another artifact. Measure its velocity and verify its stability over a long run (at least 1000 steps).
5.  **Report Findings:** Produce a final report containing the champion rule, a GIF of its behavior, and its measured properties.

This is a top-priority research goal. Success is defined as the unambiguous discovery and verification of a `v<c` glider.