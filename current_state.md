Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- The motion produced by champions from previous evolutionary runs (e.g., `rule_016`) was not stable and decayed over longer simulations. (iter_142, iter_149)
- A fitness metric based solely on velocity stability (`1 / (1 + std_dev)`) is flawed, as it strongly favors rules that quickly become inactive. (iter_150)
- A composite fitness metric, `total_displacement / (1 + std_dev)`, successfully penalizes inactive "settler" rules while rewarding displacement. The mean fitness for a random C2 rule population with this metric is ~0.45. (iter_151)

**Open Questions:**
- Can an evolutionary search using the composite fitness metric produce a rule with both high displacement (>50) and high fitness (>1.0)?
- Will the first generation of this new evolution show a significant increase in mean fitness compared to the random baseline of ~0.45?
- What are the qualitative dynamics of the top rules selected by this new metric? Are they puffers, gliders, or a new type of object?
