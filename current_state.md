# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid.

**Confirmed:**
- A fitness metric (`SimpleMotionFitness`) that penalizes transient bit count growth is effective at guiding evolution away from complex "bloater" objects (iter_176.2).
- An evolutionary search using this new metric has successfully discovered a new champion rule that exhibits simple, directed motion without explosive growth (iter_176.3).
- The previous champion from iter_174 is a complex period-64 oscillator that expands to 129 bits (iter_176.1).

**Refuted:**
- The previous assumption that a high `StableVelocityFitness` score necessarily corresponds to a simple glider.

**Best Result:**
- The current champion is the rule discovered in iter_176.3, with a `SimpleMotionFitness` score of 0.0888. It is believed to be a simple, non-explosive glider.

**In Progress:**
- The transition from evolving complex "wobblers" to simpler "gliders" is complete. The next step is to analyze the new champion.

**Open Questions:**
- Is the new champion rule from 176.3 a truly stable, long-range glider? This requires a longer simulation and visualization.
- Can the current fitness plateau of ~0.089 be surpassed by extending the evolutionary search?
- How does the new champion rule interact with other patterns?
