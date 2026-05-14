Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A composite fitness metric, `total_displacement / (1 + std_dev)`, effectively penalizes inactive "settler" rules while rewarding displacement. (iter_151)
- The composite metric provides a valid evolutionary signal, driving mean population fitness up for three consecutive generations. (iter_151, 152, 153)

**Refuted:**
- The champion rule from Gen-3, `rule_021`, is a "transient puffer" that decelerates significantly after ~500 steps. (iter_154)
- Simply extending the evaluation window to 2000 steps is **insufficient** to penalize transient puffers. The `total_displacement / (1 + std_dev)` metric is fundamentally flawed because the initial high-velocity burst dominates the calculation, masking later decay. (iter_155)

**Open Questions:**
- Will a fitness metric based purely on late-stage displacement (e.g., steps 1200-2000) correctly assign a low score to the transient puffer `rule_021`?
- Is late-stage displacement a sufficient signal to drive a new evolutionary search?
- Should a new fitness metric also include a penalty for population growth to avoid selecting for space-fillers?
