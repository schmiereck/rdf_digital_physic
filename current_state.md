Phase: Focused Exploration

## Goal
Demonstrate that complex phenomena (e.g., stable, moving particles) can emerge from a minimal set of local, reversible rules on a discrete grid.

## Confirmed
- A class of "cooling" C2-symmetric rules (containing only "death" mappings) can resolve a high-density chaotic soup into a stable, low-density field of static objects (iter_105).
- Motion (gliders) requires rules that contain "birth" mappings, where the number of live cells can increase (iter_115).

## Refuted
- A randomly generated hybrid rule with both cooling and birth mappings failed to cool a soup or produce gliders, as the birth mappings were too chaotic (iter_116).
- A hybrid rule with "center-bit-preserving" birth mappings also failed to cool a soup or produce gliders (iter_117).
- The "cooling" property as defined (monotonically non-increasing cell count) is mathematically incompatible with glider formation (iter_115).
- Exhaustive searches of C6 and C2 symmetric rule spaces for simple gliders from small contiguous seeds have failed, suggesting gliders are not an elemental property of these spaces (iter_006-096).

## Current Best Result
The four "cooling" rules from iter_105 remain the most interesting artifacts, demonstrating a mechanism for emergent order from chaos, even if they don't support motion.

## Open Questions
- Is the failure to cool the soup a result of an imbalance in the number of cooling vs. birth mappings?
- If generating a single hybrid rule at a time continues to fail, should we test a larger batch of them per iteration?
- Does glider motion fundamentally require non-C2 (i.e., chiral) symmetry?
- Could a two-rule system (a cooling rule followed by a motion rule) be more effective than a single hybrid rule?
