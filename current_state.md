Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A fitness metric based on the standard deviation of velocity over multiple time windows can successfully distinguish between stable and unstable/decaying motion. (iter_149)
- The metric correctly assigned a low fitness score (0.056) to `rule_016`, which was known to produce unstable, decaying puffers. (iter_149)
- Previous fitness metrics based on late-stage displacement were insufficient and rewarded transient motion. (iter_141, iter_125)

**Refuted:**
- The motion produced by champions from previous evolutionary runs (e.g., `rule_016`) was not stable and decayed over longer simulations. (iter_142, iter_149)

**Open Questions:**
- What is the baseline distribution of velocity-stability fitness scores for a random population of rules?
- Can we now evolve a rule with a fitness score > 0.9 (indicating high velocity stability)?
- How should we handle rules that achieve high scores by simply annihilating all particles?
