Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A fitness metric based *only* on late-stage displacement (steps 1200-2000) **successfully** identifies transient puffers as low-fitness individuals. (iter_156)

**Refuted:**
- A random population of 100 rules contains rules with significant (>0.2) late-stage displacement. The signal is very sparse. (iter_157)
- The small late-stage displacement observed in the top 3 rules of Gen-1 (iter_157) is not a heritable trait that can be amplified by breeding. The fitness landscape appears to be unnavigable from these starting points. (iter_157)

**Open Questions:**
- Since breeding failed, could a different random seed for the initial population yield a better starting point?
- Is the initial soup (density=0.25, seed=42) somehow hostile to the formation of late-stage movers?
- Should the fitness metric be modified to include a penalty for population size to explicitly select against slow, expansive "creepers"?
- Have we reached the limits of what can be found with a random soup initial condition? Should we switch to evolving on a specific, structured "object"?
