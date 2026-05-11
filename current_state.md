Phase: Phase 3: Die 2D-Hex-Kollision (BLOCKED - Kernel Search)

## Confirmed
- 1D systems can support simple (v=c) and composite (v<c) particles (iter_010, iter_014).
- A hand-crafted, non-symmetric CA rule can support a stable 2D glider (the "arrowhead," iter_024).
- A formal method exists for finding mathematically conflict-free rule kernels (iter_033).
- A valid kernel must have its generator states in disjoint rotational orbits (iter_036).

## Refuted
- Hand-crafted 2D rules are brittle and lack rotational symmetry, making them a dead end (iter_028, iter_029).
- Simple local swap rules on the 2D hex grid produce trivial or stationary patterns (iter_017, iter_021, iter_023).
- A kernel's generator states (A,B) must not be in the same rotational orbit, otherwise the resulting rule is inert (iter_035).
- A symmetric rule whose kernel only contains center-bit=0 states cannot produce dynamics from simple seeds, as it cannot create or move '1's (iter_037).

## Current Best Result
A refined, formal methodology for validating symmetric rule kernels based on three mathematical criteria (conflict-free closure, disjoint orbits, and center-bit parity).

## In Progress
- **iter_038:** Performing a combinatorial search for a rule kernel that satisfies all known criteria, including the ability to flip a cell's state.

## Open Questions
1. Does a rule kernel exist that is conflict-free, has disjoint orbits, AND can flip the center bit?
2. If such a kernel exists, does the resulting rule produce non-trivial dynamics (glider/oscillator)?
3. Does a rule generated from a center-flipping kernel respect lattice symmetry?
4. What is the full spectrum of particles and still-lifes supported by a fully valid symmetric rule?
5. Can two particles under this rule collide non-trivially and bit-conservingly?
