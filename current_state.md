# Current Research State
Phase: BLOCKED BY PLATFORM FAILURE

## Goal
Discover and characterize a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid to enable the study of emergent mass and interactions.

## Confirmed
- A stable, bit-conserving `v<c` glider exists (`g4_rule_083`). It was discovered via evolution using a 'leaky' fitness function (iter_218.2).
- A stable, bit-conserving `v=1c` glider exists (iter_179).
- A rule supporting perfectly elastic `v=1c` glider collisions exists (iter_193).

## Refuted
- An evolutionary search using a *strict*, all-or-nothing fitness function is ineffective for `v<c` glider discovery (iter_217.1).

## In Progress
- **Characterization of the new `v<c` glider: HALTED.** All attempts to extract the glider's structure or run simulations in phase_219 were blocked by a persistent, unrecoverable error in the execution platform (`name 'console' is not defined`).

## Open Questions
- Are the collisions of the new v<c glider elastic?
- Does the new rule support other stable particles?
- Can `v<c` and `v=1c` gliders interact meaningfully?
- Can different particle configurations yield different sub-light speeds under the new rule?
