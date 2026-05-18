# Current Research State
Phase: v<c Glider Discovered

## Goal
Discover a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid.

## Confirmed
- **A stable, bit-conserving `v<c` glider has been discovered** (iter_215.2). It moves at approximately 0.024 cells/step and was found using an evolutionary search. The champion rule is stored in `archive/iter_215/results/champion_rule.json`.
- The **"warm-start" evolutionary strategy is highly effective**. Seeding the population with rules known to produce transient motion successfully overcomes the "flat fitness landscape" problem encountered when starting from a random population (iter_215.2 vs. iter_214.3).
- The `LateWindowDisplacementFitness` function is robust and correctly identifies genuine, sustained motion while rejecting transient exploits (iter_214.1, iter_214.2, iter_215.2).

## Refuted
- The hypothesis that a simple evolutionary search from a random start is sufficient to find `v<c` gliders. The search space is too sparse.

## Open Questions
- How does the new v<c glider interact with other known particles, particularly the v=1c glider from iter_193?
- Can we evolve faster or more compact v<c gliders from this new baseline?
- What are the precise velocity and period of the new v<c glider?
