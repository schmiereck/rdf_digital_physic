# Current Research State
Phase: Evolutionary Search with Asymmetric Seeds

## Goal
Discover a rule that supports a stable, moving particle (glider) in a 2D hexagonal lattice.

## Confirmed
- **Symmetry Breaking:** An asymmetric particle seed enables C2-symmetric rules to induce motion (iter_170.1).
- **Evolvable Motion:** The trait of moving an asymmetric particle is evolvable (iter_170.2, iter_171.2).
- **Fitness Function Exploits:**
  - A fitness function rewarding low final bit count (`~1 / (1+bits)`) selects for particle annihilation (iter_170.2).
  - A fitness function rewarding high final bit count (`~bits`) selects for explosive, non-glider growth that results in a large, static "still life" (iter_171.2, 171.3). The motion is a transient side-effect of the initial expansion.

## In Progress
- Iteratively refining the fitness function to select for the desired phenotype of a compact, mobile particle.

## Open Questions
- How can we design a fitness function that rewards *sustained velocity* while penalizing unbounded bit-count growth?
- What dynamics will emerge when evolution is forced to optimize for both motion and compactness?
- Can rules evolved on one particle generalize to others?
