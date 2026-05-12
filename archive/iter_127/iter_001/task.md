
This task re-runs the failed experiment from iter_126 to unblock the research. The goal is to breed a new generation of rules (Gen-4) and evaluate them using a corrected "late-displacement" fitness metric that selects for sustained motion.

**1. Create the script `src/run_ash_evolution_gen4.py`**

**2. Script Logic:**

   a. **Load Assets:**
      - Load the canonical "ash" pattern from `src/ash_pattern.json`. Note its initial properties: 325 bits, 72 objects.
      - Load the top 5 unique elite rules from Gen-3, which all achieved the plateau fitness score. These are:
        - `archive/iter_122/population/rule_010.json`
        - `archive/iter_122/population/rule_055.json`
        - `archive/iter_123/population/rule_001.json`
        - `archive/iter_123/population/rule_002.json`
        - `archive/iter_123/population/rule_007.json`

   b. **Breed Gen-4 Population:**
      - Create a new population of 100 C2-symmetric rules (Gen-4).
      - Use the same breeding strategy as iter_122: For each new rule, randomly select two parents from the 5 elites. The new rule's kernels are a combination of kernels from both parents. Apply a 10% mutation chance (add/remove/change one kernel pair).
      - Save the new population to `archive/iter_127/population/`.

   c. **Evaluate Gen-4 with Late-Displacement Metric:**
      - For each of the 100 new rules:
        i.   Initialize the grid with the ash pattern.
        ii.  Simulate for **200 steps**.
        iii. Record the center of mass (COM) at step **100** and step **200**.
        iv.  Calculate the displacement: `dist = sqrt((q_200-q_100)**2 + (r_200-r_100)**2)`.
        v.   Record `final_bit_count` and `final_object_count` at step 200.
        vi.  Calculate fitness using the established formula, but with the late displacement:
             `fitness = dist / (1 + abs(final_bit_count - 325) + abs(final_object_count - 72))`

   d. **Save and Report:**
      - Save all scores to `archive/iter_127/results/fitness_scores.csv`. The CSV should include `rule_id`, `fitness`, `late_displacement`, `final_bits`, `final_objects`.
      - Find the best-performing rule.
      - Create the final `archive/iter_127/result.yaml` file with the following metrics:
        - `population_size`: 100
        - `rules_with_sustained_motion`: Count of rules with fitness > 1e-6.
        - `top_fitness_score`: The highest fitness score.
        - `top_rule_id`: Filename of the best rule.
        - `top_rule_displacement_100_200`: The displacement of the top rule.
        - `top_rule_final_bits`: Final bit count for the top rule.
        - `top_rule_final_objects`: Final object count for the top rule.
