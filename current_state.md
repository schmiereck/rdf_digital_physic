# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid.

**Note:** Phase 180 was a complete failure due to persistent technical errors in the execution environment. All attempts to simulate glider collisions failed. The state of knowledge is unchanged since the end of phase 179.

**Confirmed:**
- A stable, v=1c glider has been successfully evolved (iter_179.3, 179.4). The champion rule (`g10_rule_001`) moves the 3-bit 'L-tromino' seed at 1 cell per step with perfect bit conservation.
- The `CheckpointFitness` metric, which enforces strict bit-count stability at multiple checkpoints, was the key to this discovery (iter_179.3).
- All "champion" rules from prior evolutionary runs (iter_174, 176) are unstable under the `CheckpointFitness` metric, scoring 0.0 (iter_179.1).

**Refuted:**
- The implicit assumption that previous, simpler fitness metrics (like `SimpleMotionFitness`) were sufficient to evolve stable gliders is now explicitly refuted. Those metrics allowed for "transient bloomer" exploits.

**Best Result:**
- The champion rule discovered in `iter_179.3` and the corresponding animation (`champion_glider.gif` in `iter_179.4`) showing a perfect, stable, v=1c glider.

**In Progress:**
- The properties of this newly discovered glider (e.g., collision dynamics, robustness) have not yet been investigated due to the technical failures in phase 180.

**Open Questions:**
- What are the collision dynamics of the newly discovered v=1c glider?
- How robust is the glider to noise or perturbations?
- Can the champion rule be minimized to identify its essential components?
- Can we evolve other, different types of gliders?
