# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid.

**Confirmed:**
- Simple fitness functions based on displacement or naive conservation are easily exploited, leading to pathological rules that either annihilate the particle or cause explosive, non-coherent growth (iter_170, iter_171).
- A new, more robust fitness metric, `StableVelocityFitness`, has been implemented. It rewards sustained, stable velocity while penalizing bit growth (iter_173.1).
- The `StableVelocityFitness` metric successfully identifies and rejects previously evolved pathological rules, assigning them a fitness score of 0.0 (iter_173.2).
- An evolutionary search guided by this new metric shows positive selection pressure, increasing mean population fitness by 47x over 3 generations (iter_173.3).

**Refuted:**
- Three generations of evolution with the new metric are not sufficient to produce a stable glider (fitness > 0.5).

**Best Result:**
- The current champion is `rule g2_rule_001` from iter_173.3, with a fitness score of 0.274. It produces a 13-bit object with high but unstable velocity.

**In Progress:**
- Evolutionary search for a stable glider using the `StableVelocityFitness` metric.

**Open Questions:**
- Will more generations of evolution allow the current search to overcome the fitness plateau of ~0.27?
- Can changes to evolutionary parameters (mutation rate, population size) improve the search?
- Is the object produced by the champion rule a precursor to a glider or simply unstable debris?
