# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- **A rule supporting perfect elastic collisions has been discovered** (`archive/iter_193/iter_002/results/champion_rule.json`). This rule facilitates a bit-perfect, two-body collision between 3-bit L-tromino gliders, where the gliders recede to their original separation distance (iter_193.3).
- The "fusion" local optimum can be overcome by using a fitness function with a continuous gradient that rewards particle recession (`RecessionBiasedFitness`), a key methodological advance (iter_193.1).
- The "leaky conservation" combined with a "warm start" population remains a highly effective strategy for bootstrapping the evolutionary process (iter_193.2).
- A "leaky" fitness function with a soft penalty for non-conservation provides a viable evolutionary gradient where strict functions fail (iter_192.1).
- A stable v=1c glider (`g10_rule_001`) exists (iter_179).

**Refuted:**
- The hypothesis that the fusion local optimum was a fundamental barrier is refuted. It was an artifact of a fitness function with a poor gradient.
- The "conservation-first" strategy of pre-screening for bit-conserving rules and then evolving for motion is ineffective (iter_192.2).

**Best Result:**
- A rule that produces perfect, bit-conserving elastic collisions between two v=1c gliders. The interaction is visually confirmed in `archive/iter_193/iter_003/results/elastic_collision.gif`.

**In Progress:**
- The research has successfully transitioned from "discovering" a rule for elastic collisions to needing to "characterize" the properties of this interaction.

**Open Questions:**
- How robust is the elastic collision? Do other high-fitness rules from the final population also exhibit it?
- How does the collision angle and offset affect the outcome for the champion rule?
- Now that a v=1c elastic collision exists, can this methodology be adapted to find v<c gliders with similar interaction properties?
- What are the dynamics of three-body or multi-body collisions under this new rule?
- Is the discovered interaction long-range or does it only occur on contact?
