Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules can resolve a high-density chaotic soup into a stable, low-density field of static objects ("ash") (iter_105).
- Motion (gliders) requires rules that contain "birth" mappings (iter_115).

## Refuted
- Hybrid rules combining "cooling" and "birth" mappings are dominated by chaos and fail to resolve a soup or support gliders (iter_116, 117).
- The "cooling" property (monotonically non-increasing cell count) is mathematically incompatible with glider formation (iter_115).
- A two-stage process using a "cooling" rule followed by a highly stable "glider-friendly" rule fails to produce motion, as the "ash" objects are also still-lifes under the second rule (iter_118).
- Exhaustive searches of C6 and C2 symmetric rule spaces for simple gliders from small contiguous seeds have failed (iter_006-096).

## Open Questions
- Can a two-stage simulation using a chaotic "motion" rule animate the stable "ash"?
- Does adding random noise (perturbations) to the "ash" before Stage 2 trigger dynamics?
- Is there an optimal "ash" density for fostering gliders?
- Does glider motion fundamentally require non-C2 (i.e., chiral) symmetry?
