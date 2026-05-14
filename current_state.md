Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A fitness metric based on `1 / (1 + std_dev)` of velocity over multiple time windows can measure motion stability. (iter_149)
- For a random population, this metric strongly favors rules that quickly become inactive ("settlers") over rules with sustained motion. The mean baseline fitness for random C2 rules is ~0.824. (iter_150)
- The "annihilation" failure mode (total erasure of the grid) appears to be rare in the C2 rule space. (iter_150)

**Refuted:**
- The initial hypothesis that random rules would have low velocity-stability fitness was incorrect. They achieve high scores through inactivity. (iter_150)
- The motion produced by champions from previous evolutionary runs (e.g., `rule_016`) was not stable and decayed over longer simulations. (iter_142, iter_149)

**Open Questions:**
- Can we evolve a rule with both high velocity-stability fitness (>0.9) AND significant total displacement (>10.0)?
- How can the fitness function be modified to explicitly reward total displacement alongside velocity stability?
- Will a multi-objective approach be more effective than a single composite score?
