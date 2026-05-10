Phase: Phase 3 – Focused Exploration (2D Hex Interactions)
## Goal
Validate interaction logic (e.g., collisions, scattering) in the 2D hexagonal grid.

## Confirmed
- A hand-crafted, reversible, bit-conserving rule can produce a stable 3-bit 'arrowhead' glider with velocity v=(1,0) in a standard 2D hex CA (iter_024).
- A grid-wrapping horizontal or vertical stripe is a stable, stationary "still life" under the arrowhead rule (iter_030).

## Refuted
- The arrowhead rule is NOT rotationally symmetric; a rotated seed pattern decays chaotically (iter_028).
- An automated 6-fold symmetrization of the arrowhead rule's kernel creates conflicts and results in a rule that is chaotic even for the original glider (iter_029).
- Small, localized patterns (1 or 2 bits) are not stationary under the arrowhead rule (iter_026, iter_027).

## Current Best Result
- A stable, non-trivial 2D glider (the "arrowhead") with v=(1,0).

## In Progress
- iter_031: Staging a collision between the arrowhead glider and a stationary stripe pattern to observe interaction dynamics.

## Open Questions
1. What is the outcome of a collision between the arrowhead glider and a stationary stripe?
2. Can a fully symmetric rule be designed that supports multiple, interacting gliders?
3. Does the arrowhead rule support any other types of localized stable patterns?
4. What happens at the intersection of two stationary stripes (e.g., one horizontal, one vertical)?
