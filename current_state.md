Phase: 3 - Second W=3 Rule

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. We are testing our second candidate W=3 rule (from kernel A=11, B=14). We have confirmed it supports stable 3-bit stationary objects, but an exhaustive search proved none of them move. We now lack a "projectile" to stage a collision.

### Confirmed Findings
- A second valid, contiguous, center-flipping, conflict-free W=3 rule kernel exists (A=11, B=14) (iter_058).
- The rule from (A=11, B=14) supports at least one stable, 3-bit stationary "still life" object (iter_058).

### Refuted Hypotheses
- The second W=3 rule (A=11, B=14) does not support any 3-bit gliders; all 11 stable 3-bit objects are stationary (iter_059).
- The *first* W=3 rule (A=7, B=14) does not support any 3-bit or 4-bit gliders (iter_052, iter_054).
- Composite objects under the first W=3 rule do not produce gliders (iter_055, iter_056, iter_057).

### In Progress
- **iter_060:** Exhaustively searching all contiguous 4-bit patterns under the second W=3 rule to check for the existence of a glider.
