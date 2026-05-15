**Task: Investigate Glancing Collisions**

**Goal:** Determine the outcome of a glancing collision between two 3-bit v=1c gliders under rule `g10_rule_001`. This addresses the top open question from the current state.

**Methodology:**
1.  Load the simulation environment from `iter_181` which uses rule `g10_rule_001`.
2.  Initialize a 256x256 grid.
3.  Create two 3-bit L-tromino gliders:
    *   **Glider A:** Placed at approximately (64, 128), oriented to move East.
    *   **Glider B:** Placed at approximately (192, 130), oriented to move West.
    *   The **lateral offset** in the y-axis should be exactly **2 cells**. This is the critical parameter. This setup ensures they will not meet head-on but their edges will interact.
4.  Run the simulation for 200 steps, which is sufficient for them to meet and for the immediate aftermath to be observed.
5.  Record the initial (6 bits) and final bit counts.
6.  Generate an animation of the collision and save it to `archive/iter_184/results/glancing_collision.gif`.
7.  Write key metrics (`initial_bits`, `final_bits`, `outcome_description`) to `archive/iter_184/results/glancing_collision.json`.
8.  The `outcome_description` should be a brief string like "Annihilation", "Elastic Scattering", "Inelastic Fusion", or "Passing Through".

**Success Criterion:** The simulation completes, and the final state (bit count, animation) clearly shows the result of the glancing interaction.