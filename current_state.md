# Current Research State
Phase: v<c Search Strategy Revision

## Goal
Discover a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid.

## Confirmed
- A new fitness function, `LateWindowDisplacementFitness`, has been implemented and validated. It correctly measures displacement in a late time window (steps 500-1000), making it robust against "transient drift" exploits (iter_214.1, iter_214.2).
- The "transient drift" oscillator from iter_213.10 is confirmed to be stationary after an initial settling period, scoring 0.0 with the new fitness function (iter_214.2).
- A 10-generation evolutionary search using a random initial population and the new robust fitness function failed to find any rules producing sustained motion. The fitness landscape for random C2-symmetric rules appears to be flat at 0.0 (iter_214.3).

## Refuted
- The hypothesis that simply fixing the fitness function would be sufficient to discover a v<c glider with a standard evolutionary search.

## Open Questions
- How can we introduce a useful fitness gradient into the apparently flat search space?
- Is a "warm start" strategy, seeding evolution with rules known to produce at least transient motion, more effective than a random start?
- Is the search budget (10 generations) too small to find promising regions?
