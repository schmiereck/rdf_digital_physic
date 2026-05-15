# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid.

**Confirmed:**
- A stable, v=1c glider (3-bit L-tromino) under rule `g10_rule_001` is reproducible (iter_179, iter_181.1).
- A 5-bit composite particle, formed from the fusion of a 3-bit glider and a single bit, is also a stable, v=1c glider (iter_182.1).
- The rule `g10_rule_001` is NOT generally bit-conserving; its behavior is highly density-dependent.
- **High-density interaction (2 gliders, head-on):** Catastrophically inelastic, creating a 192-bit static "ash" (iter_181.2).
- **Medium-density interaction (1 glider + 1 bit):** Constructive inelastic fusion, resulting in the stable 5-bit composite glider (iter_181.3).
- **Interaction Range:** The interaction between gliders is strictly local (contact-only), with no effect observed at a 54-cell lateral separation (iter_182.2).

**Refuted:**
- The implicit assumption that rule `g10_rule_001` is intrinsically bit-conserving is refuted. Conservation is an emergent property of specific low-density patterns.

**Best Result:**
- The discovery and characterization of the `v=1c` glider and its complex, density-dependent interaction physics. The particle "zoo" now contains two confirmed stable gliders (3-bit and 5-bit) and two stable static structures (192-bit ash).

**In Progress:**
- Characterization of glider interactions.

**Open Questions:**
- What is the outcome of a true glancing collision between two 3-bit gliders with a lateral separation of only 1-2 cells?
- What happens in a collision between the original 3-bit glider and the newly confirmed 5-bit glider?
- Can the 192-bit static 'ash' be altered or activated by a collision with a glider?
- Can we evolve a rule that produces truly elastic collisions?
