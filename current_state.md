# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, moving particle (glider) in a 2D hexagonal grid.

**Confirmed:**
- A new, robust fitness metric, `CheckpointFitness`, has been developed and validated (iter_177.3). It enforces strict bit-count stability at multiple checkpoints, preventing "transient bloomer" exploits.
- The `SimpleMotionFitness` metric used previously is flawed and susceptible to being gamed by unstable rules (iter_177.1).

**Refuted:**
- The champion rule discovered in iter_176.3 is not a stable glider. It is a 'transient bloomer' that exhibits unstable, chaotic growth (iter_177.1, 177.2).

**Best Result:**
- There are currently **no known** rules that produce stable, moving gliders. The best result of this phase is the `CheckpointFitness` metric itself, which is a methodological advance.

**In Progress:**
- The search for a stable glider has been reset. The immediate next step is to deploy the new, more robust fitness metric. **This was blocked in phase 178 by a persistent technical error.**

**Open Questions:**
- Will an evolutionary search using the new `CheckpointFitness` metric discover a true, long-range stable glider?
- Are there any rules in previous populations that pass the new, stricter fitness check?
- Is a 200-step evaluation horizon, even with checkpoints, sufficient to guarantee long-term stability?
