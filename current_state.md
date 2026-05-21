# Current Research State
Phase: Phase 4.1 (3D Cuboctahedron CA and Local Latency) successfully completed.

## Goal
Establish a reversible, bit-conserving 3D simulation space on the FCC lattice, discover stable 3D gliders under O_h symmetry, and validate gravitational time dilation through the local latency analogy.

## Confirmed
- A 3D Cuboctahedron (FCC lattice) CA simulation engine has been developed and verified as perfectly reversible and bit-conserving (iter_224.2).
- The 12 nearest-neighbor directions of the cuboctahedron map onto 6 in-plane hexagonal and 6 out-of-plane z-stack directions, ensuring perfect stack compatibility (iter_224.1).
- The 48-order octahedral symmetry group O_h acts faithfully on the 12-channel state space, dividing it into 144 orbits (iter_224.3).
- Four stable, bit-conserving, moving 3D gliders were discovered under fully equivariant symmetric bijections, with the cleanest candidate traveling along the column axis at v=1.0c (iter_224.3).
- Gravitational time dilation has been demonstrated and characterized using the local latency / CPU-throttling analogy. A Gaussian potential well (depth=2.0, sigma=2.0) slows the glider's coordinate velocity from -1.0c to -0.336c, resulting in a physical delay of 18.609 proper-time units over 30 simulation steps (iter_224.7).

## Refuted
- The assumption that 3D gliders cannot be easily found from random starts; under O_h-symmetric orbit-pairing, stable gliders are highly evolvable.

## In Progress
- Preparing Phase 4.2: Representing the FCC lattice as a 2D+1 space-time geometry.

## Open Questions
- Can we evolve 3D gliders that move strictly below the speed of light (v<c)?
- How do 3D gliders behave during 3D collisions?
