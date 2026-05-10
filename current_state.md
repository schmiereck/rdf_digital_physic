Phase: Phase 3: Die 2D-Hex-Kollision (BLOCKED)

## Confirmed
- 1D systems can support simple (v=c) and composite (v<c) particles (iter_010, iter_014). (Phase 1 & 2 Milestones Met).
- A standard CA update model can support a hand-crafted, non-trivial 2D glider (the "arrowhead", iter_024).

## Refuted
- **Fundamental Block:** Hand-crafted rules for 2D particles lack the necessary rotational symmetry for general physical simulation. A rotated seed pattern under the arrowhead rule leads to chaotic growth, not a rotated glider (iter_028).
- Programmatic attempts to symmetrize non-symmetric rule kernels (iter_029) or simple symmetric kernels (iter_032) lead to conflicting or inert rules.
- Simple local rules on the 2D hex grid tend to produce trivial global shifts or stationary oscillators, not localized gliders (iter_017, iter_020, iter_021, iter_023).

## Current Best Result
The "arrowhead" glider (iter_024) is the only known stable, non-trivial 2D particle, but its governing rule is fundamentally flawed (non-symmetric) and thus a dead end.

## In Progress
- **iter_033:** Systematically searching for a conflict-free "rule kernel" to enable the construction of a valid, fully symmetric rule. This is a foundational step to unblock all of Phase 3.

## Open Questions
1. Does a conflict-free symmetric rule kernel even exist for low Hamming weights?
2. If a valid kernel is found, will the resulting symmetric rule produce any non-trivial dynamics from a simple seed?
3. If a glider is produced by a symmetric rule, does rotating the seed produce a correctly rotated glider?
4. What is the simplest multi-bit seed required to activate a symmetric rule?
