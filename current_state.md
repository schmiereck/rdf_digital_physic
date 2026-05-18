# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, `v<c` glider.

**Confirmed:**
- A new fitness function, `RobustCumulativeDisplacementFitness`, has been developed and validated to be immune to both the "phase-sampling" and "annihilation" exploits (iter_202.3).
- An evolutionary search with this robust function does not produce a `v<c` glider within 20 generations. It consistently converges on a local optimum of stable, bit-conserving, but stationary patterns (iter_202.4).
- The `v=1c` elastic collision rule from `iter_193` remains the best confirmed result for particle interaction.

**Refuted:**
- The `v<c` glider from `iter_200` was refuted in `iter_201`.
- The `CumulativeDisplacementFitness` function was refuted as a reliable tool in `iter_202.2`.

**Best Result:**
- The `v=1c` elastic collision rule (`iter_193`). The search for a `v<c` glider has been reset to a new, more reliable baseline.

**In Progress:**
- The `v<c` glider search must be re-started from the new baseline, focusing on methods to escape the local optimum of stationary patterns.

**Open Questions:**
- How can the evolutionary search be modified (e.g., population size, mutation rate, new seeds) to escape the local optimum of stationary patterns?
- Is it possible that no simple rule supports a `v<c` glider for the 3-bit L-tromino, and that a different approach is needed?
