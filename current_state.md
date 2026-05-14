Phase: Phase 7 - Velocity-Stable Evolution

**Goal:** Evolve a Cellular Automata rule that supports a stable, moving particle (glider) with non-decaying velocity over 2000+ steps.

**Confirmed:**
- A composite fitness metric, `total_displacement / (1 + std_dev)`, can identify high-velocity objects, but they may be transient "puffers" that decay over time (iter_153, iter_156).
- A fitness metric based on *late* displacement (e.g., steps 1200-2000) correctly identifies and penalizes these transient puffers (iter_156).
- A composite metric, `late_displacement / (1 + final_bit_count)`, effectively selects for rules that produce sustained motion while penalizing chaotic, explosive growth (iter_159).
- Breeding based on the composite metric is effective. Gen-2 showed a +481% improvement in mean fitness and a 14x improvement in the champion's fitness over Gen-1 (iter_163). The new champion rule achieves motion with significantly more compact structures (603 bits vs 8204 bits).

**Current Best:**
- **Rule:** `rule_022` from `iter_163`.
- **Fitness:** 0.000793 (`late_displacement / (1 + final_bit_count)`).

**Open Questions:**
- Can we continue the strong fitness improvement seen in `iter_163` into a third generation?
- What is the qualitative nature of the object produced by the new champion rule?
- Does the champion object's motion sustain over longer time horizons (e.g., 4000 steps)?
