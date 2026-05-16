# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A robust evolutionary framework for finding rules with conserving collisions has been developed, including a symmetric `CollisionFitness` function that rewards preservation of bit and object counts (iter_187.2).
- An evolutionary search using this new fitness function successfully discovered a rule that perfectly conserves bit (6 -> 6) and object (2 -> 2) counts in a head-on collision scenario (iter_187.2).
- The previous rule `g10_rule_001` is confirmed to be incapable of elastic scattering (iter_181, iter_185).
- A stable v=1c glider (3-bit L-tromino) under rule `g10_rule_001` is reproducible (iter_179).

**Refuted:**
- Simple, non-symmetric fitness functions for collision dynamics are easily exploited by rules that lead to annihilation or explosive growth (iter_187.1).

**Best Result:**
- A new candidate rule from `iter_187.2` that appears to produce elastic collisions, based on final particle and bit counts. The dynamics of this collision are captured in `archive/iter_187/results/champion_collision.gif` and await analysis.

**In Progress:**
- Characterization of the new rule from `iter_187.2`.

**Open Questions:**
- What is the qualitative dynamic of the champion rule from 187.2 (is it true scattering or a trivial exploit like stasis)?
- How can the fitness function be improved to reward dynamic scattering properties (e.g., momentum change) and not just end-state counts?
- Now that a conserving collision rule exists, what do its glider-vs-still-life interactions look like?
