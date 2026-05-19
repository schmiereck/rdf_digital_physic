**Goal:** Programmatically reproduce the fitness function exploit identified in `iter_219`.

**Task:**
1.  Create a Python script named `src/reproduce_exploit.py`.
2.  The script must perform the following steps:
    a. Load the rule from `archive/iter_218/results/champion_rule.json`.
    b. Load the `LeakyCheckpointFitness` function from `src/fitness.py`.
    c. Initialize a 128x128 hexagonal grid with the standard 3-bit L-tromino seed.
    d. Run the simulation for 500 steps.
    e. Calculate the fitness score using the `LeakyCheckpointFitness` function.
    f. Calculate the final net displacement of the center of mass (distance from its starting position).
    g. Print the final fitness score and the net displacement.
3.  The task is successful if the script runs and reports a high fitness score (e.g., > 10.0) and a near-zero displacement (e.g., < 0.1).