# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A rule supporting perfect, bit-conserving elastic collisions for **head-on** impacts has been discovered (iter_193, iter_195.1).
- The elastic scattering angle for head-on collisions is systematically dependent on the impact parameter (iter_195.2).
- A new fitness function, `SparseGliderFitness`, robust against the "grid-filling" exploits seen in `iter_197.2`, has been developed and validated (iter_199.3).

**Refuted:**
- The hypothesis that the `v=1c` elastic collision rule is generally robust. The rule fails to support stable gliders at a 60-degree orientation (iter_199.1).
- The timeout observed in `iter_197.1` was not caused by a computational explosion in the CA dynamics, but by technical overhead in visualization code (iter_199.1).

**Best Result:**
- A rule (`archive/iter_193/iter_002/results/champion_rule.json`) that produces robust elastic collisions for head-on and near-head-on impacts. Its generality is now known to be limited.

**In Progress:**
- The search for massive (`v<c`) particles is now unblocked and ready to proceed with a new, more robust fitness function.

**Open Questions:**
- Now that a robust fitness function (`SparseGliderFitness`) exists, can a full evolutionary search discover a stable `v<c` glider?
- Can we evolve a new rule that exhibits elastic collisions across multiple impact angles (e.g., 0 and 60 degrees) by using a more complex fitness scenario?
- What are the dynamics of three-body or multi-body collisions under the champion `v=1c` elastic rule in the head-on configuration?
- What is the maximum interaction offset for the `v=1c` elastic scattering rule?
