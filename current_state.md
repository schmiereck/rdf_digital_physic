Phase: Phase 3: Die 2D-Hex-Kollision (BLOCKED - Rule Generation)

## Confirmed
- 1D systems can support simple (v=c) and composite (v<c) particles (iter_010, iter_014).
- A hand-crafted, non-symmetric CA rule can support a stable 2D glider (the "arrowhead," iter_024).
- A method for finding mathematically conflict-free kernels for symmetric rules exists (iter_033).

## Refuted
- Hand-crafted 2D rules are brittle and lack rotational symmetry, making them a dead end (iter_028, iter_029).
- Simple local swap rules on the 2D hex grid produce trivial or stationary patterns (iter_017, iter_021, iter_023).
- Programmatic symmetrization of flawed or internally-symmetric kernels leads to conflicting or inert rules (iter_029, iter_032, iter_035). A valid kernel's generator states (A,B) must not be in the same rotational orbit.

## Current Best Result
A validated, formal method for identifying the necessary mathematical properties of a symmetric rule kernel (refined in iter_033 and iter_035).

## In Progress
- **iter_036:** Performing a formal search for a conflict-free kernel where the generator states belong to different rotational orbits.

## Open Questions
1. Does a kernel exist where states A and B are in different rotational orbits and the closure is conflict-free?
2. If such a kernel exists, does the rule generated from it produce non-trivial dynamics?
3. What is the simplest initial condition that activates a valid symmetric rule?
4. Can this new type of rule support stable gliders that exhibit rotational symmetry?
5. Can two such gliders collide in a non-trivial, bit-conserving way?
