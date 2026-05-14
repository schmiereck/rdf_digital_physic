Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A fitness metric based solely on velocity stability (`1 / (1 + std_dev)`) is flawed, as it strongly favors rules that quickly become inactive. (iter_150)
- A composite fitness metric, `total_displacement / (1 + std_dev)`, successfully penalizes inactive "settler" rules while rewarding displacement. The mean fitness for a random C2 rule population with this metric is ~0.45. (iter_151)
- The composite metric provides a valid evolutionary signal. Breeding the top 10% of a random population (Gen-1) resulted in a Gen-2 with a 34.9% higher mean fitness (0.45 -> 0.61), confirming the search is progressing. (iter_152)

**Open Questions:**
- Can this evolutionary momentum be sustained into Gen-3?
- What are the qualitative dynamics of the top rules selected by this new metric? Are they puffers, gliders, or a new type of object?
- At what fitness level do visually compelling, glider-like structures emerge?
- Is an elite fraction of 10% optimal for this search?
