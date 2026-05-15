# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid.

**Confirmed:**
- A stable, v=1c glider (3-bit L-tromino) under rule `g10_rule_001` is reproducible (iter_179, iter_181.1).
- The rule `g10_rule_001` is NOT generally bit-conserving. Its behavior is highly density-dependent.
- **High-density interaction:** A head-on collision between two gliders (6 bits) is catastrophically inelastic, resulting in a stable, 192-bit static "ash" (iter_181.2).
- **Medium-density interaction:** A collision between a glider (3 bits) and a single bit (1 bit) is a constructive inelastic fusion, resulting in a new, stable, 5-bit composite glider (iter_181.3).

**Refuted:**
- The implicit assumption that rule `g10_rule_001` is intrinsically bit-conserving is now refuted. Conservation is an emergent property of a specific low-density pattern (the single glider), not a general property of the rule.

**Best Result:**
- The discovery and characterization of the v=1c glider and its complex, density-dependent interaction physics. Two new stable structures have been identified: the 192-bit "ash" and a 5-bit composite glider.

**In Progress:**
- Characterization of the newly discovered glider and its interactions is underway.

**Open Questions:**
- What are the properties of the new 5-bit composite glider (velocity, stability)?
- What happens in a glancing (off-axis) collision between two of the original 3-bit gliders?
- What are the properties of the 192-bit 'ash' created in the head-on collision?
- Can we evolve a rule that produces truly *elastic* collisions?
