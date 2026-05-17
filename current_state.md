# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid with stable, ideally elastic, collision dynamics.

**Confirmed:**
- A rule supporting perfect, bit-conserving elastic collisions has been discovered and validated (iter_193, iter_195.1).
- The elastic collision behavior is **robust**, with the top 5 rules from the discovery population all exhibiting the same property (iter_195.1).
- The champion rule handles imperfect collisions gracefully, producing **perfect elastic scattering** for head-on collisions with vertical offsets up to 3 cells (iter_195.2).
- The **scattering angle is systematically dependent on the collision's impact parameter** (vertical offset), a key physics-like property (iter_195.2).
- The "leaky conservation" and "recession-biased fitness" functions are a highly effective methodology for discovering complex collision dynamics (iter_192, iter_193).

**Refuted:**
- The hypothesis that the fusion local optimum was a fundamental barrier is refuted. It was an artifact of a fitness function with a poor gradient.

**Best Result:**
- A rule (`archive/iter_193/iter_002/results/champion_rule.json`) that produces robust, bit-conserving elastic collisions and scattering. Visual confirmation: `archive/iter_195/results/offset_3_collision.gif`.

**In Progress:**
- The research has successfully characterized the v=1c elastic collision. The next major step is to adapt this methodology to search for massive (v<c) particles.

**Open Questions:**
- Can the successful methodology be adapted to find v<c gliders with elastic collisions?
- What are the dynamics of three-body or multi-body collisions under the champion rule?
- How does the champion rule handle collisions at different angles (e.g., 60 degrees)?
- What is the maximum offset at which the elastic scattering interaction occurs?
