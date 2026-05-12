**Part 1: Generate Canonical Ash Pattern**
1.  Create a script `src/generate_ash_pattern.py`.
2.  This script loads `archive/iter_105/population/rule_023.json`.
3.  It initializes a 150x150 grid with 25% random noise (seed=42).
4.  It simulates for 200 steps to create the 'ash'.
5.  It saves the final set of live cell coordinates `(q, r)` to `src/ash_pattern.json`.

**Part 2: Validate New Fitness Metric**
1.  Create a new script `src/validate_ash_fitness_metric.py`.
2.  This script loads the `src/ash_pattern.json`. It should report the initial number of cells and objects.
3.  It will test two rules against this pattern:
    -   **Inert Rule:** `src/symmetric_rule_nonconserving_A3_B14.json` (from `iter_118`).
    -   **Chaotic Rule:** `archive/iter_084/population/rule_023.json` (from `iter_119`).
4.  For each rule:
    a. Load the ash pattern onto a 150x150 grid.
    b. Simulate for 500 steps.
    c. Calculate the final `bit_count` and `object_count`.
    d. Calculate the net displacement of the grid's center of mass.
    e. Calculate `fitness = displacement / (1 + abs(initial_bits - final_bits) + abs(initial_objects - final_objects))`.
5.  The script's YAML output must contain:
    - `initial_ash_bits`: Bit count of the loaded ash pattern.
    - `initial_ash_objects`: Object count of the loaded ash pattern.
    - `inert_rule_fitness`: The calculated fitness for the inert rule.
    - `inert_rule_final_bits`: Final bit count for the inert rule.
    - `chaotic_rule_fitness`: The calculated fitness for the chaotic rule.
    - `chaotic_rule_final_bits`: Final bit count for the chaotic rule.