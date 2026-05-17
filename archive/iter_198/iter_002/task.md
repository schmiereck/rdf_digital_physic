The goal is to discover a stable `v<c` glider (a "massive" particle) through evolution. This requires designing a new fitness function that overcomes the failures of previous attempts.

**Background & Constraints:**
1.  **`iter_197.2` Failure:** The last `v<c` search failed because a fitness function rewarding low velocity variance was exploited by a "grid-filling" pattern that trivially kept the center-of-mass stable.
2.  **`iter_198.1` Revelation:** The "elastic collision" rule from `iter_193` was discovered to be an artifact. The `RecessionBiasedFitness` did not produce gliders, but "fizzlers" that fragment into static debris. The fitness function was exploited.
3.  **New Fitness Function Requirements:** Your primary task is to design, implement, and use a new fitness function that explicitly selects for `v<c` motion and is robust against both "grid-filling" and "fizzler" exploits. A successful function should combine three elements:
    *   **Sustained Motion:** Reward consistent displacement over multiple checkpoints (similar to the successful `CheckpointFitness` from `iter_179`).
    *   **Low Velocity:** The displacement between checkpoints should be consistently less than the number of steps, but greater than zero.
    *   **Simplicity/Compactness Penalty:** Add a term that penalizes high bit counts or large bounding box areas. This is the key element to prevent the grid-filling exploit. A suggested metric is `displacement / (1 + final_bit_count * bounding_box_area)`.

**Plan:**
1.  **Sub-task 1 (Design & Implement):** Create and implement a new fitness class, `MassiveGliderFitness`, in `src/fitness.py`. It should incorporate the three requirements above.
2.  **Sub-task 2 (Evolve):** Run an evolutionary search using this new fitness function for at least 5 generations. The search should use the standard 3-bit L-tromino seed.
3.  **Sub-task 3 (Validate & Report):** Identify the champion rule from the search. Validate that it produces a genuine `v<c` glider and is not another exploit. Report the rule, its fitness, and the glider's properties (e.g., velocity, period). Visualize the glider's motion.

The final output should be a rule that produces a particle with a velocity measurably and consistently between 0 and c.