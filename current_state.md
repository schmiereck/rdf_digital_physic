# Current Research State
Phase: Phase 3 (2D Hex Glider Discovery) successfully completed.

## Goal
Discover and characterize a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid.

## Confirmed
- A stable, period-1, diagonal-moving `v<c` glider exists under a C2-symmetric, bit-conserving rule (`champion_rule_perfect.json`, iter_222.4.2).
- The glider moves at exactly `0.469c` with exceptional velocity stability (std_dev = 0.0044 over 500 steps, iter_222.7).
- The center-of-mass boundary crossing artifact is fully resolved using trigonometric toroidal CoM and step-by-step unwrapping (iter_222.7).
- The particle has 3 initial bits (L-tromino) and 4 final bits, with perfect size conservation throughout the run.
- The corrected, artifact-free fitness of the glider is `0.350669` (iter_222.7).

## Refuted
- The assumption that sub-light gliders cannot be found under simple, sparse C2-symmetric rules (a sparse 42-entry LUT is sufficient).

## In Progress
- Preparing the transition of our cellular automaton framework to 3D Cuboctahedron geometry (Phase 4.1).

## Open Questions
- What are the elastic collision properties of the v=0.469c sub-light glider?
- How does the 2D hexagonal logic generalize to 3D and 4D FCC spacetime grids?
