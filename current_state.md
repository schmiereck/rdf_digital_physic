Phase: Phase 3: Die 2D-Hex-Kollision (Streuung)

## 1. Goal
Demonstrate that complex physical phenomena can emerge from minimal, local, reversible rules on a discrete, symmetric lattice.

## 2. Confirmed Findings
- **Milestone Reached (Phase 1):** A 1D lattice supports bit-conserving rules that allow for stable particle propagation at v=c (iter_009, iter_010).
- **Milestone Reached (Phase 2):** Increasing bit-depth to 2 bits/cell allows for internal oscillations (v=0) and the emergence of "massive" particles with effective velocities v < c (iter_011, iter_012, iter_013, iter_014).
- **Rule Existence (2D-Hex):** Non-trivial, reversible, bit-conserving rules exist for a 2D hexagonal, 7-cell neighborhood (iter_015).

## 3. Current Best Result
- **Fastest Particle (1D):** v=c (1.0 cells/step) using a 1-bit rule (iter_010).
- **"Massive" Particle (1D):** v=c/2 (0.5 cells/step) using 2-bit rules (iter_013, iter_014).

## 4. In Progress
- **iter_016:** Testing if a simple bit-rotation rule produces stable gliders on the 2D hexagonal grid.

## 5. Open Questions
- Does a simple neighborhood bit-rotation rule produce stable gliders in 2D-hex?
- What is the velocity and period of a glider produced by a neighborhood bit-rotation rule?
- Can two gliders produced by the rotation rule collide and scatter elastically?
- Are there other simple permutations of the W=1 neighborhood states that produce gliders with different velocities or properties?
- How do multi-bit initial patterns evolve under the simple rotation rule?
