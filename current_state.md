# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A stable, v=1c glider (3-bit L-tromino) under rule `g10_rule_001` is reproducible (iter_179).
- A stable, v=1c 5-bit composite glider exists (iter_182.1).
- All tested interactions under rule `g10_rule_001` are catastrophically inelastic and non-conserving:
  - Head-on 3-bit vs 3-bit collision creates a 192-bit static 'ash' (iter_181.2).
  - Glancing 3-bit vs 3-bit collision creates a 321-bit period-2 oscillator (iter_185.1).
  - 3-bit vs 5-bit collision leads to a computationally intractable state explosion (iter_185.2).
- The 192-bit 'ash' is not inert; it is a reactive medium that can be catalyzed by a glider collision to grow into a larger, 322-bit stable static structure (iter_185.3).
- The interaction range of gliders is strictly local (contact-only) (iter_182.2).

**Refuted:**
- The hypothesis that rule `g10_rule_001` could support any form of simple or elastic scattering is now strongly refuted by overwhelming evidence from multiple collision scenarios.

**Best Result:**
- A thorough characterization of a rule that supports stable gliders but has complex, inelastic, density-dependent collision physics. This serves as a well-documented baseline for what to avoid in future searches.

**In Progress:**
- This line of inquiry is complete. A new evolutionary search is required.

**Open Questions:**
- Can an evolutionary search with a fitness function that directly rewards bit conservation *during* collisions produce a rule capable of elastic scattering?
- What is the underlying mechanism causing the computational explosion in the 3-bit vs. 5-bit collision?
- What properties of the initial state determine which of the high-bit-count attractors (e.g., 192-bit, 321-bit, 322-bit) the system falls into?
