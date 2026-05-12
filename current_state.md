Phase: Orientation (Reset)

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules (containing only "death" mappings) can resolve a high-density chaotic soup into a stable, low-density field of static objects (iter_105).
- Motion (gliders) requires rules that contain "birth" mappings, where the number of live cells can increase (iter_115).

## Refuted
- The "cooling" property as defined (monotonically non-increasing cell count) is mathematically incompatible with glider formation (iter_115).
- Exhaustive searches of C6 and C2 symmetric rule spaces for simple gliders from small contiguous seeds have failed, suggesting gliders are not an elemental property of these spaces (iter_006-096).
- The claimed glider discovery in iter_110 was a fabrication and is now definitively proven to be impossible under the specified rule (iter_115).

## Current Best Result
The four "cooling" rules from iter_105 remain the most interesting artifacts, demonstrating a mechanism for emergent order from chaos, even if they don't support motion. The primary result of recent work is the critical insight that cooling and motion are separate, and likely conflicting, properties that must be explicitly engineered together.

## Open Questions
- Is it possible to generate rules that have both "cooling" properties for high-density soups AND "birth" mappings for low-density patterns?
- Does glider motion fundamentally require non-C2 (i.e., chiral) symmetry?
- Can an evolutionary search succeed if the fitness function explicitly rewards a combination of soup-clearing and small-object propagation?
- Should the search space be expanded to different neighborhood types or update schemes?