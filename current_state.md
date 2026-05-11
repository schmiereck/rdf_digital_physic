Phase: Phase 3: Die 2D-Hex-Kollision (UNBLOCKED)

## Confirmed
- 1D systems can support simple (v=c) and composite (v<c) particles (iter_010, iter_014).
- A hand-crafted, non-symmetric CA rule can support a stable 2D glider (the "arrowhead," iter_024).
- A conflict-free kernel for generating a valid, fully symmetric, reversible, bit-conserving rule exists (e.g., A=3, B=6 for W=2) (iter_033).

## Refuted
- Hand-crafted rules for 2D particles lack rotational symmetry, making them a dead end for general physical simulation (iter_028, iter_029).
- Simple local rules (e.g., swaps) on the 2D hex grid tend to produce trivial or stationary patterns (iter_017, iter_021, iter_023).
- Naive programmatic symmetrization of flawed kernels leads to conflicting or inert rules (iter_029, iter_032).

## Current Best Result
A validated method for generating conflict-free symmetric rules (iter_033). The arrowhead glider (iter_024) is the only known glider, but its rule is flawed.

## In Progress
- **iter_034:** Testing the dynamics of the first rule generated from a conflict-free symmetric kernel (A=3, B=6).

## Open Questions
1. Does the rule from the (3,6) kernel produce non-trivial dynamics?
2. If a glider is produced, does rotating the seed produce a correctly rotated glider?
3. What is the spectrum of behaviors for this new rule with different simple seeds?
4. Are there other conflict-free kernels that produce qualitatively different physics?
5. Can two gliders under a symmetric rule collide in a non-trivial, bit-conserving way?
