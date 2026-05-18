# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, `v<c` glider.

**Confirmed:**
- The champion rule from `iter_200.1` produces a stable, bit-conserving, period-4 **stationary oscillator**, not a glider (iter_201.1, 201.2).
- The `SparseGliderFitness` function is vulnerable to a "phase-sampling exploit", where it mistakes the internal phase shifts of an oscillator for genuine translational motion (iter_201.3).
- The `v=1c` elastic collision rule from `iter_193` remains the best confirmed result for particle interaction.

**Refuted:**
- The claim that a `v<c` glider was discovered in `iter_200`. The result has been demonstrated to be a measurement artifact.

**Best Result:**
- The `v=1c` elastic collision rule (`iter_193`). The search for a `v<c` glider has been reset.

**In Progress:**
- The `v<c` glider search must be re-started after developing a more robust fitness function.

**Open Questions:**
- How can `SparseGliderFitness` be modified to be robust against phase-sampling exploits?
- Will measuring cumulative displacement from t=0, rather than inter-checkpoint displacement, prevent this exploit?
- Can a renewed evolutionary search with a corrected fitness function discover a true `v<c` glider?
