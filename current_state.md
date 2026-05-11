Phase: 3 - W=3 Rule Dynamics

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. We have a mathematically valid W=3 rule and stable 3-bit and 4-bit stationary targets ("still lifes"), but all attempts to find or construct a moving particle ("glider") have failed. The search for a projectile is the critical path.

### Confirmed Findings
- A valid, contiguous, center-flipping, conflict-free rule kernel exists at Hamming Weight 3 (A=7, B=14) (iter_049).
- The W=3 rule supports at least one stable, 3-bit stationary object (a straight-line "still life") (iter_051).
- The W=3 rule supports at least two stable, 4-bit stationary objects (iter_054).

### Refuted Hypotheses
- The W=3 rule does not support any stable, bit-conserving 3-bit gliders from monolithic seeds (iter_052).
- The W=3 rule does not support any stable, bit-conserving 4-bit gliders from monolithic seeds (iter_054).
- Composite gliders do not form when two 3-bit still lifes are placed in a symmetric configuration (collinear, either adjacent or with a 1-cell gap) (iter_055, iter_056).

### In Progress
- **iter_057:** Testing if two 3-bit still lifes, placed in an *asymmetric* adjacent configuration, can interact to form a stable, composite glider.
