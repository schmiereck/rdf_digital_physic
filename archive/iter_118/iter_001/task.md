
Create a Python script `src/run_two_stage_simulation.py` to test if a sequential application of two different rule sets can produce gliders from a chaotic soup.

**Stage 1: Cooling Phase**
1.  Load the pure "cooling" rule `rule_023.json` from `archive/iter_105/population/`.
2.  Initialize a 150x150 toroidal grid with 25% random noise, using a fixed random seed of 42 for reproducibility.
3.  Simulate for 1000 steps to produce a stable, low-density "ash" of static objects.
4.  Save the set of live cell coordinates from the final grid state of this phase.

**Stage 2: Motion Phase**
1.  Load the "glider-friendly" (non-conserving, with births) C6-symmetric rule from `src/symmetric_rule_nonconserving_A3_B14.json`. This rule was analyzed in iter_069 and is known to support a rich variety of still-lifes but is not overly chaotic.
2.  Initialize a new 150x150 grid using the live cell coordinates saved from the end of Stage 1.
3.  Simulate for an additional 1000 steps using this second rule.
4.  After the simulation, analyze the final grid state to identify all distinct objects (using a connected components algorithm).
5.  For each object, determine if it is a still-life, an oscillator, or a glider by tracking its structure and center of mass over a sufficient number of steps (e.g., 100) to detect cycles and net displacement.

**Reporting**
Write the final results to `archive/iter_118/result.yaml` with the following metrics:
- `glider_count`: The number of unique moving objects found.
- `oscillator_count`: The number of unique oscillating objects found.
- `still_life_count`: The number of unique stationary objects found.
- If `glider_count` > 0, include details of the first glider found:
    - `glider_period`: The period of the glider's cycle.
    - `glider_bit_count`: The number of live cells in the glider.
    - `glider_velocity`: A tuple `(dq, dr)` of its velocity in hex coordinates.
- `ash_bit_count`: The number of live cells at the end of the cooling phase.
- `final_bit_count`: The number of live cells at the end of the motion phase.
