Your primary goal is to discover a rule that produces a stable, sub-light speed (`v<c`) glider in the 2D hexagonal grid. This is the main unsolved problem of Phase 3.

**Background & Lessons Learned:**
The search for a `v<c` glider has failed multiple times due to subtle fitness function exploits. Review `iter_201`, `202`, `203`, and `204` to understand these failures:
-   **`iter_201`:** A stationary oscillator exploited a 'phase-sampling' flaw.
-   **`iter_203`:** 'Puffer' and 'compact oscillator' exploits were defeated by adding a `net_displacement` term.
-   **`iter_204`:** Developed a more robust function but was blocked by platform errors.

**Your Plan:**
1.  **Synthesize Fitness Function:** Create the most robust fitness function yet by combining the successful elements from previous iterations. It MUST include:
    *   **Checkpointing:** To ensure stability over the entire run (see `CheckpointFitness` from `iter_179`).
    *   **Net Displacement:** To defeat stationary oscillators and 'puffer' exploits (see `iter_203`).
    *   **Velocity Calculation:** A robust method to calculate `v<c` that is not fooled by periodic motion.
    *   **Bit Conservation:** Strict penalty for any change in bit count.
2.  **Evolve:** Run a full evolutionary search using this new fitness function. Use the standard configuration from `goal.md` (128x128 grid, L-tromino seed, population of 100).
3.  **Validate:** If a champion rule with high fitness is found, perform a basic validation run. Generate an animation (`champion.gif`) and a plot of its center-of-mass displacement over time (`displacement.png`). This is to visually confirm it is a true `v<c` glider and not another exploit before declaring success.

**Final Output:**
-   The champion rule as a JSON file.
-   The validation animation and displacement plot.
-   A summary of the fitness function used and the evolutionary progress.