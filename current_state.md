# Current Research State
Phase: Breeder exploit closed, fitness landscape mapped.

## Goal
Discover and characterize a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid.

## Confirmed
- The previous champion was a stationary breathing breeder-oscillator of period 64 (iter_220.9).
- Setting `max_bit_threshold=12` in `DisplacementConsistencyFitness` completely eliminates breeders, forcing evolution to produce only compact, stable structures (iter_220.23).
- Hard-gated fitness metrics like `SubLightFitness` cause a flat 0.0 fitness landscape when starting from random rules, proving the necessity of leaky conservation and warm-starts (iter_220.80).
- The codebase in `src/` is fully `pandas`-free, preventing sub-agent execution errors (iter_220.17).

## Refuted
- Naive windowed CoM consistency without a bit-count ceiling is sufficient (it is easily exploited by breeders).

## In Progress
- Preparing a warm-started evolution run using iter_215's final population combined with the `max_bit_threshold=12` filter.

## Open Questions
- How can we design a C2-preserving crossover operator to maintain rule symmetry?
- What is the minimum population size needed for warm-start searches to converge?
