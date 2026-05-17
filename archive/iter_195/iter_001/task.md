**Goal:** Analyze the robustness of the elastic collision discovery by evaluating the top 5 rules from the final population of iter_193.

**Inputs:**
- The final population from the successful evolutionary run: `archive/iter_193/iter_002/results/final_population.json`.
- The standard collision seed generation function from `src/seeds.py`.

**Steps:**
1.  Create a new script `src/characterize_top_rules.py`.
2.  Load the `final_population.json` file.
3.  Identify and load the top 5 rules based on their fitness scores.
4.  For each of the 5 rules:
    a. Generate the standard two-glider head-on collision seed.
    b. Run a simulation for 500 steps.
    c. Save the simulation as a GIF animation (e.g., `top_1_collision.gif`, `top_2_collision.gif`, etc.) into `archive/iter_195/results/`.
    d. Programmatically classify the collision outcome. The primary success criterion is a perfect elastic collision, identified by:
        i.  The final bit count equals the initial bit count (6 bits).
        ii. The final distance between the two gliders' centers of mass is equal to or greater than the initial distance.
5.  Generate a summary report `summary.json` in `archive/iter_195/results/` that lists each of the top 5 rules, their fitness score from the population file, and the classified outcome of their collision simulation.
