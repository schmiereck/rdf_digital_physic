Phase: 3 - W=3 Rule Dynamics

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. We have a mathematically valid W=3 rule and stable 3-bit and 4-bit stationary targets, but we lack a moving particle (projectile) to stage a collision. The search for a projectile is the critical path.

### Confirmed Findings
- A valid, contiguous, center-flipping, conflict-free rule kernel exists at Hamming Weight 3 (A=7, B=14) (iter_049).
- The W=3 rule supports at least one stable, 3-bit stationary object (a straight-line "still life") (iter_051).
- The W=3 rule supports at least two stable, 4-bit stationary objects (iter_054).

### Refuted Hypotheses
- The W=3 rule does not support any stable, bit-conserving 3-bit gliders. All 11 contiguous 3-bit patterns are either unstable or stationary (iter_052).
- The W=3 rule does not support any stable, bit-conserving 4-bit gliders. All 10 unique contiguous 4-bit patterns are either unstable or stationary (iter_054).
- The W=2 rule (`A=3, B=6`) is not bit-conserving during multi-particle interactions and has been abandoned (iter_048).

### In Progress
- **iter_055:** Testing if two 3-bit still lifes can interact to form a stable, composite glider.
