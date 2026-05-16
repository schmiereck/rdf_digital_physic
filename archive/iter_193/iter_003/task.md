Take the champion rule discovered in sub-task 193.2, located at `archive/iter_193/iter_002/results/champion_rule.json`, and verify its dynamics.

**Steps:**
1.  Load the champion rule.
2.  Set up a simulation on a 128x128 grid using the standard two-glider collision seed (the same setup as the fitness function).
3.  Run the simulation for 500 steps.
4.  Generate a GIF animation of the entire simulation and save it to `archive/iter_193/iter_003/results/elastic_collision.gif`.
5.  At the end of the simulation, explicitly calculate and report the following metrics:
    -   `final_staged_score`
    -   `final_bit_error`
    -   `final_recession_score` (final_distance / initial_distance)

**Goal:**
Visually confirm that the champion rule produces a clean, elastic collision, matching the perfect fitness score of 2.0. The GIF should show two gliders approaching, interacting, and moving apart without losing their integrity or changing the total bit count.