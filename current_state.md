# Current Research State
Phase: Methodological Pivot

## Goal
Discover a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid.

## Confirmed
- The strict `SubLightFitness` function correctly identifies and rejects `v=1c` gliders and stationary patterns (iter_216.4).
- A stable, bit-conserving `v=1c` glider exists and was found via evolution (iter_215.2, iter_216.2).

## Refuted
- An evolutionary search using the strict `SubLightFitness` function is **ineffective** for glider discovery, as it creates a flat, all-or-nothing fitness landscape with no gradient (iter_217.1).
- A 'warm-start' population seeded with rules known to produce `v=1c` motion is **not** a good starting point for a `v<c` search (iter_217.1). The rules are too unstable and fail bit conservation.

## In Progress
- Developing a new 'leaky' fitness function to provide a searchable gradient.

## Open Questions
- Will a fitness function that provides partial credit (e.g., for near bit-conservation) create a searchable gradient?
- Is a random starting population more effective for a `v<c` search?
- What new exploits will a 'leaky' fitness function enable?
