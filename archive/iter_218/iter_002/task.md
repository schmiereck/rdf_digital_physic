Run a full evolutionary search for a `v<c` glider using the new `LeakySubLightFitness` function.

**Steps:**

1.  **Modify `src/run_vc_search.py`:**
    *   Add the import statement: `from leaky_fitness import LeakySubLightFitness`.
    *   In the main execution block, comment out the old fitness function (`SubLightFitness`) and instantiate `LeakySubLightFitness` instead.
    *   Use the standard configuration: 10 generations, population size of 100, 3-bit L-tromino seed.

2.  **Execute the Script:**
    *   Run the modified `src/run_vc_search.py`.
    *   Ensure that the final results, including the champion rule and the evolution log, are saved to `archive/iter_218/results/`.

The goal is to see if the new 'leaky' fitness function creates a searchable landscape and produces a rule with a high fitness score.