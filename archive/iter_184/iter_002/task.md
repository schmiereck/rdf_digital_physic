**Task: Characterize the 5-bit Composite Particle**

**Goal:** Determine if the 5-bit particle, formed in `iter_181.3`, is a stable glider, and if its stability is direction-dependent, like the 3-bit glider from `iter_184.1`.

**Background:** Sub-agent `184.1` discovered that the 3-bit L-tromino is only a stable glider in one orientation (East-moving). The 5-bit particle's stability was claimed in `iter_183` but never actually executed. We must verify its properties before conducting collision experiments.

**Methodology:**
1.  Load the simulation environment with rule `g10_rule_001`.
2.  Initialize a 256x256 grid.
3.  Re-create the 5-bit particle. The particle's shape was the result of a 3-bit East-moving glider fusing with a stationary bit. From `iter_181.3`, the initial state was:
    *   Glider at (112, 128) -> `[(112, 128), (113, 128), (113, 129)]`
    *   Stationary bit at (128, 128)
    *   After 20 steps, they fused into a 5-bit particle. Re-run this setup for 20 steps to obtain the exact 5-bit particle shape and location.
4.  Run the simulation for an additional 400 steps with this 5-bit particle as the initial condition.
5.  Track the bit count and the center of mass at each step.
6.  **Crucially, attempt to rotate the 5-bit particle by 180 degrees** and run a separate simulation to see if the "West-moving" orientation is also stable.
7.  Record the results for both orientations.
8.  Save an animation of the stable orientation to `archive/iter_184/results/5bit_glider_stable.gif`.
9.  Write a summary of findings (stability, velocity, bit count evolution for both orientations) to `archive/iter_184/results/5bit_characterization.json`.

**Success Criterion:** The simulation determines whether the 5-bit particle is a stable glider and if its stability is orientation-dependent. The JSON output contains bit count and velocity data for both the original and rotated particle.