# Current Research State
Phase: v<c Glider Discovery and Characterization

## Goal
Discover and characterize a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid to enable the study of emergent mass and interactions.

## Confirmed
- **A stable, bit-conserving `v<c` glider exists.** It was discovered via evolution using a 'leaky' fitness function (iter_218.2).
  - Rule: `g4_rule_083` (champion from iter_218.2)
  - Velocity: ~0.64 cells/step.
  - The 'leaky' fitness function, which penalizes rather than strictly rejects bit non-conservation, provides a searchable gradient for evolution (iter_218.1, 218.2).
- A stable, bit-conserving `v=1c` glider exists (iter_179).
- A rule supporting perfectly elastic `v=1c` glider collisions exists (iter_193).

## Refuted
- An evolutionary search using a *strict*, all-or-nothing fitness function is ineffective for `v<c` glider discovery, as it creates a flat fitness landscape with no gradient (iter_217.1).

## In Progress
- Characterization of the new `v<c` glider and its governing rule.

## Open Questions
- Are the collisions of the new v<c glider elastic?
- Does the new rule support other stable particles?
- Can `v<c` and `v=1c` gliders interact meaningfully?
- Can different particle configurations yield different sub-light speeds under the new rule?
