# Current Research State

## 1. Goal
Demonstrate that complex physical phenomena can emerge from minimal, local, reversible rules on a discrete, symmetric lattice.

## 2. Status
**Phase 2: Der "Zappel"-Detektor (Dynamics)**
We have confirmed that rules supporting internal states can exist. We are now performing the first simulation to observe the dynamics of the simplest such rule.

## 3. Confirmed
- **Existence of 1-bit Rules:** There are 33 non-trivial, reversible, bit-conserving rules for a 1D, 3-bit neighborhood (iter_001).
- **Dynamics of 1-bit Rules:** 22 of the 33 rules produce stable, propagating gliders (v=c) from a single-bit initial condition (iter_002).
- **Existence of 2-bit Rules:** At least one non-trivial, reversible, bit-conserving rule exists for a 1D, 3-neighborhood, 2-bit/cell lattice (iter_003).

## 4. In Progress
- **iter_004:** Simulating the minimal oscillating 2-bit/cell rule to verify that it produces a stable, stationary oscillation ("Zappeln").

## 5. Open Questions
- Can we construct a rule that combines oscillation with translation to create a particle with v < c?
- What is the simplest initial condition that leads to non-trivial behavior with the current rule?
- How can we systematically search for other simple, fundamental rules in the 2-bit/cell state space?
- What happens when two oscillating particles collide?
