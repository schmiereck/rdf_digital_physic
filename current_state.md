# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, `v<c` glider.

**Confirmed:**
- The `RobustCumulativeDisplacementFitness` function is vulnerable to a "puffer" exploit, where particles gain fitness by expanding their bounding box without moving (iter_203.1).
- A fitness function based on *cumulative* displacement divided by bounding box size (`DisplacementOverBoundingBoxFitness`) successfully defeats the "puffer" exploit but is vulnerable to a "compact oscillator" exploit, where particles accumulate high fitness by oscillating in-place (iter_203.3).
- The failure to find a `v<c` glider is a systematic issue with the fitness landscape, not an artifact of unlucky initial conditions (iter_203.1).

**Refuted:**
- The hypothesis that the `iter_202` failure was due to an unlucky random seed (iter_203.1).

**Best Result:**
- The `v=1c` elastic collision rule (`iter_193`) remains the best confirmed result for particle physics. No progress has been made on finding a `v<c` glider.

**In Progress:**
- The `v<c` glider search is stalled, pending the development of a new fitness function based on *net* displacement to defeat the compact oscillator exploit.

**Open Questions:**
- Can a fitness function based on *net* displacement (start-to-end distance) finally break the cycle of exploits and discover a true `v<c` glider?
- Is the 3-bit L-tromino seed too prone to oscillation, and should we explore larger, more rigid seeds?
- Are there other search techniques besides evolution (e.g., direct construction) that might be better suited for finding `v<c` gliders?
