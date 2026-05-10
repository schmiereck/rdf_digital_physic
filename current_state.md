Phase: Phase 3 – Focused Exploration (2D Hex Interactions)
## Goal
Validate interaction logic (e.g., collisions, scattering) in the 2D hexagonal grid.

## Confirmed
- A hand-crafted, reversible, bit-conserving rule can produce a stable 3-bit 'arrowhead' glider with velocity v=(1,0) in a standard 2D hex CA (iter_024).

## Refuted
- A single isolated '1' bit is NOT stationary under the arrowhead rule; it moves at v=(1,0), preventing simple collisions with the arrowhead glider (iter_025).

## Current Best Result
- A stable, non-trivial 2D glider (the "arrowhead").

## In Progress
- iter_026: Searching for a stable, stationary pattern ('still life') to use as a collision target.

## Open Questions
1. Can stationary objects exist in the arrowhead rule's universe?
2. What happens when two arrowhead gliders collide head-on?
3. Can the rule be extended to support gliders on other axes?
