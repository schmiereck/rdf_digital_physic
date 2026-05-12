Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- **BREAKTHROUGH:** A stable, 6-bit, period-4 moving particle ("glider") has been discovered (iter_110). This is the first validated instance of motion in this research project.
- The "primordial soup" evaluation method is a successful strategy for finding rules that generate complex, emergent structures (iter_105).
- "Cooling" rules, which are biased to map higher-density states to lower-density ones, can reliably resolve a chaotic soup into a low-density "ash" of persistent objects (iter_105).

## Refuted
- Simple, contiguous initial seeds are not a reliable source of gliders for the rule spaces explored (iter_006-096).
- Abstract complexity and simple stability are poor proxy metrics for evolving glider-supporting behavior (iter_082-089).

## Current Best Result
We have discovered a 6-bit, period-4 glider that emerges naturally from a chaotic soup under C2-symmetric cooling rule `archive/iter_105/population/rule_023.json`. Its velocity is (-1, 0) in hex coordinates.

## Open Questions
- What are the precise coordinates and structure of the new glider?
- Can the glider be created reliably from a minimal seed, or is it purely emergent?
- Do the other three "cooling" rules from iter_105 also produce this glider or others?
- How do two of these gliders interact when they collide?
