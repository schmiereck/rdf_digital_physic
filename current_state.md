Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A composite fitness metric, `total_displacement / (1 + std_dev)`, effectively penalizes inactive "settler" rules while rewarding displacement. (iter_151)
- The composite metric provides a valid evolutionary signal, driving mean population fitness up for three consecutive generations. (iter_151, 152, 153)

**Refuted:**
- The champion rule from Gen-3, `rule_021`, is not a stable glider. It is a "transient puffer" that exhibits high velocity for ~500 steps before decelerating significantly. Its high fitness score (3.465) was an artifact of an evaluation period that was too short to capture this decay in motion. (iter_154)

**Open Questions:**
- Can a longer fitness evaluation period (e.g., 2000 steps) effectively filter out transient puffers like `rule_021`?
- Will re-running the Gen-3 evolution with a longer evaluation window produce a champion with more persistent motion?
- Is there an alternative fitness metric that is less susceptible to being fooled by transient puffers?
