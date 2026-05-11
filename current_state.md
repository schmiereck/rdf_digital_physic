Phase: 3 - Second W=3 Rule

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
BLOCKED. All attempts to find or construct a moving particle ("glider") under the first W=3 rule (from kernel A=7, B=14) have failed. The research has pivoted to finding and testing the next valid W=3 rule.

### Confirmed Findings
- A valid, contiguous, center-flipping, conflict-free rule kernel exists at Hamming Weight 3 (A=7, B=14) (iter_049).
- The rule from (A=7, B=14) supports stable 3-bit and 4-bit stationary "still life" objects (iter_051, iter_054).

### Refuted Hypotheses
- The W=3 rule (A=7, B=14) does not support any stable, bit-conserving 3-bit or 4-bit gliders from monolithic seeds (iter_052, iter_054).
- Composite gliders do not form from symmetric or asymmetric arrangements of 3-bit still lifes under the (A=7, B=14) rule; interactions result in larger still lifes or non-conserving decay (iter_055, iter_056, iter_057).

### In Progress
- **iter_058:** Finding and testing the *second* valid W=3 rule kernel to see if it supports non-trivial dynamics.
