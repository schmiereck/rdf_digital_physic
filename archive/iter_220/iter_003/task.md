**Goal:** Write a Python script to reproduce the fitness function exploit. **Do not execute the script.**

**Task:**
1.  Create a Python script named `src/reproduce_exploit.py`.
2.  The script's purpose is to run a simulation and calculate fitness to demonstrate the exploit where a stationary object gets a high score.
3.  The script must contain the necessary logic to:
    a. Load the rule from `archive/iter_218/results/champion_rule.json`.
    b. Import `LeakyCheckpointFitness` from `src/fitness.py`.
    c. Import necessary simulation components like `HexGrid` and `Simulator`.
    d. Define the simulation parameters (128x128 grid, 3-bit L-tromino seed, 500 steps).
    e. Run the simulation.
    f. Calculate the fitness and net displacement.
    g. Print the final results in a clear format.
4.  The task is successful once the file `src/reproduce_exploit.py` is written and appears correct upon visual inspection.