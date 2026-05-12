Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules (containing only "death" mappings) can resolve a high-density chaotic soup into a stable, low-density field of static objects (iter_105).
- Motion (gliders) requires rules that contain "birth" mappings, where the number of live cells can increase (iter_115).

## Refuted
- Hybrid rules with a 4:4 or 6:2 cooling-to-birth ratio are dominated by the chaotic nature of the birth mappings, failing to cool a soup or support gliders (iter_116, 117).
- The "cooling" property as defined (monotonically non-increasing cell count) is mathematically incompatible with glider formation (iter_115).
- Exhaustive searches of C6 and C2 symmetric rule spaces for simple gliders from small contiguous seeds have failed, suggesting gliders are not an elemental property of these spaces (iter_006-096).

## Current Best Result
The four "cooling" rules from iter_105 remain the most interesting artifacts, demonstrating a mechanism for emergent order from chaos, even if they don't support motion.

## Open Questions
- Is the failure of hybrid rules a fundamental principle, or did we just get unlucky with our random samples?
- If a single rule cannot be both a 'cooler' and a 'mover', could a two-stage process work (apply a pure cooling rule, then switch to a pure motion rule)?
- Does glider motion fundamentally require non-C2 (i.e., chiral) symmetry?
