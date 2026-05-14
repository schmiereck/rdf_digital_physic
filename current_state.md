# Current Research State
Phase: Evolutionary Search with Asymmetric Seeds

## Goal
Discover a rule that supports a stable, moving particle (glider) in a 2D hexagonal lattice.

## Confirmed
- **Symmetry Lock:** A C2-symmetric rule cannot displace the center of mass of a C2-symmetric particle (iter_167).
- **Symmetry Breaking:** Using an asymmetric particle seed (a 3-bit L-tromino) enables C2-symmetric rules to induce motion (iter_170.1).
- **Evolvable Motion:** The trait of moving the L-tromino is evolvable. A second generation of rules bred from founders showed a 2.4x improvement in fitness for the best non-degenerate rule (iter_170.2).

## Newly Identified Issues
- The current fitness function, `displacement / (1 + final_bit_count)`, is flawed. It heavily rewards rules that annihilate the particle entirely, creating a degenerate evolutionary attractor (iter_170.2).

## In Progress
- Evolutionary search for stable gliders using the "glider nursery" method (evolving rules on a specific, small, asymmetric particle).

## Open Questions
- How can the fitness function be modified to penalize annihilation?
- What new glider dynamics will emerge once the annihilation loophole is closed?
- Can rules evolved on one particle generalize to others?
