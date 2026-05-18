**Objective: Discover a stable, non-trivial `v < c` (sub-light speed) glider.**

This is the most critical open task in Phase 3. Your goal is to orchestrate a definitive evolutionary search that succeeds where prior attempts have failed due to fitness exploits and platform errors. You must synthesize the lessons from past failures to construct and run a robust experiment.

**Methodology: Evolutionary Search**

1.  **Synthesize Past Lessons:** Your first step is to analyze the failures of `iter_197`, `iter_201`, `iter_203`, and `iter_204`. You must build a fitness function that is explicitly immune to the exploits discovered in those iterations.
2.  **Construct the Fitness Function:** The fitness function in your search script (`src/run_vc_search.py` or a new script) MUST combine the following principles:
    *   **Net Displacement:** It must reward total displacement from the start to the end of the simulation to defeat stationary but complex oscillators (`iter_203` exploit).
    *   **Strict Bit Conservation:** It must use the `CheckpointFitness` principle (`iter_179`) where the particle's bit-count must be perfectly stable at multiple checkpoints. Any deviation results in zero fitness. This defeats 'puffers' and 'bloomers'.
    *   **Phase-Sampling:** It must sample the particle's position at non-uniform intervals or multiple consecutive steps (e.g., steps 397, 398, 399, 400) to defeat periodic oscillators that appear stationary at a single checkpoint (`iter_201` exploit).
    *   **Compactness Metric (Optional but Recommended):** Reward particles that remain spatially compact to disfavor dispersal.
3.  **Configure and Run the Search:**
    *   Use the standard 3-bit L-Tromino as the seed particle.
    *   Run the evolution for a minimum of 10 generations, but continue as long as fitness is improving.
    *   The primary output should be the best rule found (`champion_rule.json`) and a log of the evolutionary progress.
4.  **Validate the Champion:**
    *   After the search, run a separate characterization of the champion rule.
    *   Generate a visualization (e.g., `champion_glider.gif`) of its behavior over at least 500 steps.
    *   Programmatically verify that its velocity is `0 < v < 1` and that it is stable (not shedding bits).
    *   Your final report must explicitly state whether the champion is a true `v<c` glider or another unforeseen exploit.

**Success Criterion:**
The final output of this planner run must be a definitive conclusion: either you have found and validated a true `v<c` glider, or you have identified a new, previously unknown failure mode/exploit.
