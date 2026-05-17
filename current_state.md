# Current Research State

**Goal:** Evolve a Cellular Automata rule that produces a stable, `v<c` glider.

**Confirmed:**
- A stable, slow (`v << c`) glider has been discovered via evolutionary search (`iter_200.1`). The champion rule is located at `archive/iter_200/results/champion_v_lt_c_rule.json`.
- The `SparseGliderFitness` function is an effective tool for evolving `v<c` motion (`iter_200.1`).
- The discovered particle is compact, non-diffuse, and maintains perfect bit-conservation over hundreds of steps (`iter_200.1`, `iter_200.5`).
- The `v=1c` elastic collision rule from `iter_193` remains the best result for particle interaction.

**Refuted:**
- The belief that a persistent `ValueError` was blocking progress. The issue was resolved in the previous phase (`iter_200` second run).

**Best Result:**
- The `v<c` glider rule discovered in `iter_200.1`. This is a major breakthrough.

**In Progress:**
- The *quantitative* characterization of the new `v<c` glider (precise velocity, period) is currently blocked by persistent platform token limit errors.

**Open Questions:**
- What is the precise velocity and period of the `v<c` glider from `iter_200.1`?
- Can the platform instability (token limits) be resolved to allow for quantitative analysis scripts to run?
- Will the new `v<c` glider rule also support elastic collisions?
