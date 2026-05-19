# Current Research State
Phase: v<c Glider Debunked

## Goal
Discover and characterize a stable, `v<c` (sub-light speed) glider in the 2D hexagonal grid to enable the study of emergent mass and interactions.

## Confirmed
- A stable, bit-conserving `v=1c` glider exists (iter_179).
- A rule supporting perfectly elastic `v=1c` glider collisions exists (iter_193).

## Refuted
- **The `v<c` glider (`g4_rule_083`) from iter_218 is NOT a glider.** Direct analysis of the discovery animation file shows it is a stationary 2-4 cell object. The high fitness score was an artifact of an exploited fitness function (iter_219.7).
- An evolutionary search using a *strict*, all-or-nothing fitness function is ineffective for `v<c` glider discovery (iter_217.1).

## In Progress
- None. The search for a `v<c` glider must be restarted.

## Open Questions
- How can we design a fitness function for v<c gliders that is immune to stationary/oscillator exploits?
- Does the 'leaky' conservation principle still hold value when combined with a robust displacement metric?
- Is a warm-start approach (seeding with v=1c glider rules) a more promising path for finding v<c gliders than random search?
