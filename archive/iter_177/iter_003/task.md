Develop a new, more robust fitness metric that is not susceptible to the 'transient bloomer' exploit observed in iter_177.1 and 177.2.

**Goal:** Create and validate a new fitness function that correctly assigns a very low score to the unstable champion rule from iter_176.3.

**Analysis of Failure:**
- The previous metric, `SimpleMotionFitness`, evaluated displacement over 200 steps.
- The failed rule `gen_5/rule_019.json` starts blooming around step 21, well within the evaluation window.
- The metric was flawed because its penalty for `max_bit_count` was not strong enough to counteract the apparent displacement of the expanding blob's center of mass.

**Planner Task:**
1.  **Design a new metric:** Propose a `CheckpointFitness` metric. This metric should perform several checks for bit-count stability during the simulation. If the particle's bit count does not match its initial bit count at any checkpoint, the simulation should be terminated early and a fitness of 0.0 returned. This acts as a hard constraint against blooming.
    - Proposed checkpoints: `[50, 100, 150, 200]` steps.
    - If all checkpoints are passed, the fitness should be the displacement, just like before.
2.  **Implement the new metric:** Create a new file `src/fitness.py` or modify the existing one to include this new `CheckpointFitness` function. It should be reusable for future evolutionary runs.
3.  **Validate the new metric:** Create a script to test the `CheckpointFitness` metric against the known pathological rule from `iter_176.3` (`archive/iter_176/results/gen_5/rule_019.json`) and its 3-bit seed.
4.  **Synthesize Results:** The final output should be the new fitness score for the pathological rule and a conclusion on whether the new metric is successful.

**Success Criterion:** The new `CheckpointFitness` metric must assign a fitness score of 0.0 to the rule from `iter_176.3`, demonstrating that it successfully identifies and penalizes the bit count instability.