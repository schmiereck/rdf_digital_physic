# Current Research State
Phase: Phase 3 (2D Hex Glider and Collision Dynamics) successfully completed.

## Goal
Discover and physically characterize stable sub-light speed (v<c) gliders and their multi-body interaction properties on the 2D hexagonal grid.

## Confirmed
- A stable, period-1, diagonal-moving sub-light speed glider exists under a C2-symmetric, bit-conserving rule (`champion_rule_perfect.json`, iter_222.4.2) and moves at exactly `0.469c` with exceptional velocity stability (std_dev = 0.0044, iter_222.7).
- The sub-light speed glider's physical interaction cross-section is strictly local (iter_223.8). At transverse offsets outside [0, 1, 2] (specifically offsets -4, -3, -2, -1, +3, +4), two colliding gliders pass each other completely unaffected, maintaining their NW and SE trajectories and speed (v ≈ 0.460c after step 190).
- Head-on (offset 0) and offset 2 collisions are highly inelastic and trigger a runaway chaotic explosion, with the bit count growing from 6 to 364 (offset 0) and 343 (offset 2) by step 200 (iter_223.7, iter_223.8).
- Offset 1 collisions result in **perfect mutual annihilation** (iter_223.8). The two gliders completely destroy each other and leave a perfect vacuum (0 bits) by step 190, which persists through step 200, serving as a clean deterministic analog to matter-antimatter annihilation.
- The v<c and v=1c glider regimes represent disjoint rule classes under our current evolutionary corpus (iter_223.4.1); none of the 151 scanned rules supported both.

## Refuted
- The assumption that sub-light gliders exhibit elastic (bouncing) collisions under Rule A (`champion_rule_perfect.json`) (iter_223.8).
- The assumption that mixed-speed glider co-existence can be easily found in rule pools evolved under single-speed regimes (iter_223.4.1).

## In Progress
- Initiating Phase 4.1: Devising the 3D Cuboctahedron (FCC lattice) CA simulation engine.

## Open Questions
- Can we evolve rules that explicitly support the co-existence of both v<c and v=1c gliders?
- How do the 12 spatial directions of the 3D Cuboctahedron affect glider stability and speed?
