# Current Research State

## 1. Goal
Demonstrate that complex physical phenomena can emerge from minimal, local, reversible rules on a discrete, symmetric lattice.

## 2. Status
**Phase 2: Der "Zappel"-Detektor (Initiation)**
Phase 1 successfully identified rules for simple particle motion (v=c). We are now beginning Phase 2 by increasing the system's complexity to allow for internal states (2 bits per cell), which is a prerequisite for simulating mass (v < c).

## 3. Confirmed
- **Existence of 1-bit Rules:** There are 33 non-trivial, reversible, bit-conserving rules for a 1D, 3-bit neighborhood (iter_001).
- **Dynamics of 1-bit Rules:** From a single-bit initial condition, 22 of the 33 rules produce stable, propagating gliders (v=c), while 11 result in a stable, non-moving state (iter_002).

## 4. In Progress
- **iter_003:** Attempting to prove the existence of a non-trivial, reversible, bit-conserving rule for a more complex 1D system with 2 bits per cell.

## 5. Open Questions
- Do non-trivial, reversible, bit-conserving rules exist for a 1D, 2-bit-per-cell system?
- Can a rule for a 2-bit/cell system support internal oscillations ("Zappeln")?
- Can internal oscillations lead to emergent particles with velocity v < c?
- What is the size distribution of the state space when grouped by Hamming weight for the 2-bit/cell system?
- How can we efficiently search the vastly larger rule space of a 2-bit/cell system?
