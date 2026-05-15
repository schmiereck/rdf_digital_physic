Perform a glancing (off-axis) collision experiment between two 3-bit v=1c gliders.

1.  **Setup:**
    - Create a 256x256 hexagonal grid.
    - Place the first 3-bit L-tromino glider (seed pattern from iter_179) centered at `(128, 100)`. This glider will move "East" (positive column direction).
    - Place a second, identical 3-bit L-tromino glider centered at `(128, 154)`. This glider will also move "East".
    - The gliders should be positioned on the same row, but separated horizontally such that their paths do not directly overlap, but are close enough for their edges to interact as they propagate.
2.  **Simulate:** Run the simulation for 300 steps using the `g10_rule_001`. This duration is sufficient to observe the pre-collision, the interaction, and the post-interaction state.
3.  **Analyze & Report:**
    - Report the initial and final total bit counts.
    - Describe the outcome of the interaction: Do the gliders pass through each other? Do they repel? Do they merge or annihilate? Are new particles created?
    - Save the results of the analysis, including bit counts over time, to `archive/iter_182/results/glancing_collision_report.txt`.
    - Generate an animation of the collision: `archive/iter_182/results/glancing_collision.gif`.
4.  **Goal:** Determine the outcome of a non-head-on collision and compare it to the known catastrophic head-on result and the constructive fusion result.