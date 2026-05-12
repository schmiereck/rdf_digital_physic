Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- **BREAKTHROUGH:** A stable, 6-bit, period-4 moving particle ("glider") has been discovered emerging from a chaotic soup under rule `archive/iter_105/population/rule_023.json` (iter_110).
- The glider's precise 4-phase structure has been programmatically extracted and documented in `archive/iter_113/results/glider_structure.json` (iter_113).
- The "primordial soup" evaluation method is a successful strategy for finding rules that generate complex, emergent structures (iter_105).

## Refuted
- Simple, contiguous initial seeds are not a reliable source of gliders for the rule spaces explored (iter_006-096).
- Abstract complexity and simple stability are poor proxy metrics for evolving glider-supporting behavior (iter_082-089).

## Current Best Result
We have a concrete structural definition of a 6-bit, period-4 glider that moves with velocity (-1, 0) under a known C2-symmetric rule.

## Open Questions
- Can the newly characterized glider be created from a minimal, non-emergent seed?
- Do the other three "cooling" rules from iter_105 also produce gliders?
- How do two of these gliders interact when they collide?
- Is the glider's motion truly infinite, or does it decay on a much larger timescale?
