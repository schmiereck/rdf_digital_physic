Phase: Phase 3: Die 2D-Hex-Kollision (BLOCKED - Rule Validation)

## Confirmed
- 1D systems can support simple (v=c) and composite (v<c) particles (iter_010, iter_014).
- A hand-crafted, non-symmetric CA rule can support a stable 2D glider (the "arrowhead," iter_024).
- A formal method exists for finding mathematically conflict-free rule kernels (iter_033).
- A valid kernel (A=3, B=6) exists that satisfies all known criteria, including disjoint rotational orbits (iter_036).

## Refuted
- Hand-crafted 2D rules are brittle and lack rotational symmetry, making them a dead end (iter_028, iter_029).
- Simple local swap rules on the 2D hex grid produce trivial or stationary patterns (iter_017, iter_021, iter_023).
- A kernel's generator states (A,B) must not be in the same rotational orbit, otherwise the resulting rule is inert (iter_035).

## Current Best Result
A validated, mathematically sound kernel (A=3, B=6) for generating a fully symmetric, reversible, bit-conserving rule (iter_036).

## In Progress
- **iter_037:** Simulating the dynamics of the first rule generated from a fully validated symmetric kernel.

## Open Questions
1. Does the rule generated from the valid (A=3, B=6) kernel produce non-trivial dynamics?
2. If so, is the result a glider or an oscillator?
3. Does this new rule respect the lattice symmetry (i.e., does a rotated seed produce a rotated particle)?
4. What is the full spectrum of particles and still-lifes supported by this rule?
5. Can two particles under this rule collide non-trivially and bit-conservingly?
