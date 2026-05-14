Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a CA rule that supports a stable, moving particle (a true glider) with sustained, non-decaying velocity.

**Confirmed:**
- A fitness metric based *only* on late-stage displacement (steps 1200-2000) **successfully** identifies transient puffers as low-fitness individuals. (iter_156)
- A composite fitness metric, `late_displacement / (1 + final_bit_count)`, **successfully** penalizes rules that result in diffuse, non-compact, high-entropy states, correctly assigning a near-zero score to a previously high-scoring but undesirable rule. (iter_159)

**Refuted:**
- The small late-stage displacement observed in random rules is not a heritable trait that can be amplified by breeding with a simple displacement metric. (iter_157)
- The failure to find "viable" rules (fitness > 0.2) in a random population is not due to an unlucky random seed. A second, independent search yielded nearly identical, low-fitness results, suggesting the desired behavior is intrinsically rare. (iter_158)

**Open Questions:**
- Will an evolutionary search using the validated composite fitness metric find any viable rules?
- Is the initial random soup (density=0.25) hostile to the formation of late-stage movers?
- Could a different initial condition provide a better substrate for evolving motion?
