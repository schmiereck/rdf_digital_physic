# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A rule supporting perfect, bit-conserving elastic collisions for **head-on** impacts has been discovered (iter_193, iter_195.1).
- The elastic scattering angle for head-on collisions is systematically dependent on the impact parameter (iter_195.2).
- A fitness function for `v<c` gliders requires more than just constant-velocity checks; it must be robust against "grid-filling" exploits where the center-of-mass is trivially stable (iter_197.2).

**Refuted:**
- The hypothesis that the `v=1c` elastic collision rule is robustly stable is now in question. A 60-degree collision simulation failed to complete, suggesting a potential for computationally explosive behavior (iter_197.1).

**Best Result:**
- A rule (`archive/iter_193/iter_002/results/champion_rule.json`) that produces robust elastic collisions for head-on and near-head-on impacts. Its general stability is now under investigation.

**In Progress:**
- The search for massive (`v<c`) particles. The initial attempt failed due to a flawed fitness function, and a revised approach is required.

**Open Questions:**
- Can a revised fitness function (with a capped complexity bonus and a particle-size check) guide evolution to a stable `v<c` glider?
- What is the mechanism causing the computational explosion in 60-degree collisions for the `v=1c` elastic rule?
- What are the dynamics of three-body or multi-body collisions under the champion elastic rule?
- What is the maximum offset at which the elastic scattering interaction occurs for the `v=1c` rule?
