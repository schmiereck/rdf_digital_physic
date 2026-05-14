Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A composite fitness metric, `total_displacement / (1 + std_dev)`, effectively penalizes inactive "settler" rules while rewarding displacement. The mean fitness for a random C2 rule population is ~0.45. (iter_151)
- The composite metric provides a valid evolutionary signal. Gen-2 mean fitness improved by 34.9% over Gen-1 (0.45 -> 0.61). (iter_152)
- Evolutionary momentum is sustained. Gen-3 mean fitness improved by 25.8% over Gen-2 (0.61 -> 0.77). (iter_153)
- A new champion rule, `rule_021`, has emerged with a fitness score of 3.465, an outlier that is 2.6x higher than the previous generation's maximum. (iter_153)

**Open Questions:**
- What are the qualitative dynamics of the new champion, `rule_021`? Does it produce a true glider?
- Is the high fitness of `rule_021` robust to different initial random seeds?
- Can `rule_021` be used as a parent to create an even more fit Gen-4?
