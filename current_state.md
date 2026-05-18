# Current Research State
Phase: Phase 3 (v<c Glider Search) - Blocked by Platform Error

## Goal
Discover fundamental, binary operations on a discrete lattice that give rise to emergent physical laws. The immediate goal is to find a stable, sub-light speed (`v<c`) glider in the 2D hexagonal grid, which would represent the emergence of mass.

## Confirmed
- A stable `v=1c` glider exists (`g10_rule_001`, iter_179).
- A rule supporting perfectly elastic, bit-conserving `v=1c` glider collisions exists (iter_193, iter_195).
- The `v=1c` glider rule is brittle in non-head-on collisions (iter_197).
- Multiple fitness function exploits for `v<c` search have been identified and documented (`puffer`, `compact oscillator`, `phase-sampling`). A robust fitness function must defend against these (iter_201-203).

## Refuted
- Simple, hand-crafted symmetric rules are insufficient to produce complex dynamics (iter_016-030).
- Early evolutionary fitness functions were easily exploited, leading to non-viable candidates (iter_171-177, iter_201-203).

## Best Result
The most significant positive result is the discovery of a rule supporting perfect elastic collisions for `v=1c` gliders (iter_193). This demonstrates that physics-like interactions can emerge.

## In Progress
- The primary research effort is focused on finding a `v<c` glider. Phase 211 attempted to launch a new evolutionary search, but was blocked by a platform error (iter_211.1).

## Open Questions
- Can a rule be evolved that supports a stable `v<c` glider?
- What is the minimal set of components for a fitness function that is robust against all known exploits?
- Does the standard L-tromino seed provide sufficient asymmetry to discover `v<c` motion?
