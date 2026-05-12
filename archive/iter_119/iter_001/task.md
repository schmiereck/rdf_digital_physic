
Create a new script, `src/run_two_stage_chaotic_sim.py`, that performs a two-stage simulation to test if a chaotic rule can animate a pre-structured field of objects.

**Stage 1: Generate the "Ash"**
1.  Load the best "cooling" rule: `archive/iter_105/population/rule_023.json`.
2.  Initialize a 150x150 grid with 25% random noise (using a fixed `random_seed=42`).
3.  Simulate for 200 steps to allow the soup to resolve into a stable field of static objects (the "ash"). Store the grid state at step 200.
4.  Record the `ash_bit_count` (the number of live cells in the ash).

**Stage 2: Animate the Ash**
1.  Load a known chaotic, high-fitness rule from the first evolutionary attempt. The top-performing rule from Gen-2 was `rule_023` from `archive/iter_084/population/`.
2.  Apply this chaotic rule to the "ash" grid state from Stage 1.
3.  Simulate for an additional 1000 steps (from t=200 to t=1200).
4.  At the end of the simulation, record the `final_bit_count`.

**Analysis & Reporting**
1.  After Stage 2 is complete, perform an object analysis on the final grid state.
2.  Identify all connected components. For each component, run a separate simulation to check for stability (cycles) and motion (displacement).
3.  Create `archive/iter_119/result.yaml` with a summary of the findings. The YAML must contain:
    -   `ash_bit_count`: The number of live cells after Stage 1.
    -   `final_bit_count`: The number of live cells after Stage 2.
    -   `outcome_class`: A string classification. If `final_bit_count` > 5000, classify as "CHAOTIC_EXPLOSION". If the grid is identical to the ash, classify as "FROZEN". Otherwise, classify as "DYNAMICS_OBSERVED".
    -   `glider_count`: The number of stable, moving objects found.
    -   `oscillator_count`: The number of stable, non-moving oscillating objects found.
    -   `still_life_count`: The number of stable, non-moving static objects found.
    -   `decayed_object_count`: The number of initial ash objects that were destroyed.
