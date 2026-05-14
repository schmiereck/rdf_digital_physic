Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A fitness metric based *only* on late-stage displacement (steps 1200-2000) **successfully** identifies the transient puffer `rule_021` as a low-fitness individual (score=0.133). (iter_156)
- The champion rule from the previous evolution, `rule_021`, is a "transient puffer" that decelerates significantly after ~500 steps. (iter_154)

**Refuted:**
- The composite fitness metric, `total_displacement / (1 + std_dev)`, is a flawed measure of sustained motion because it is dominated by initial high-velocity bursts. (iter_155)

**Open Questions:**
- Is the late-stage displacement signal strong enough to drive a new evolutionary search to find true gliders?
- Will a simple late-displacement metric select for 'creepers' that expand slowly and steadily, rather than compact gliders?
- Should a penalty for population growth be reintroduced to the fitness function to ensure compact objects are favoured?
