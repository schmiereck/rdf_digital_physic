Phase: 3 - Second W=3 Rule

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. We have found a second W=3 rule (from kernel A=11, B=14) and confirmed it supports at least one stable, stationary 3-bit object. However, it is unknown if this rule supports any moving objects ("gliders"), which are required to stage a collision.

### Confirmed Findings
- A second valid, contiguous, center-flipping, conflict-free W=3 rule kernel exists (A=11, B=14) (iter_058).
- The rule from (A=11, B=14) supports at least one stable, 3-bit stationary "still life" object (iter_058).

### Refuted Hypotheses
- The *first* W=3 rule (A=7, B=14) does not support any 3-bit or 4-bit gliders (iter_052, iter_054).
- Composite objects under the first W=3 rule do not produce gliders (iter_055, iter_056, iter_057).

### In Progress
- **iter_059:** Exhaustively searching all 11 unique 3-bit patterns under the second W=3 rule to check for the existence of a glider.
