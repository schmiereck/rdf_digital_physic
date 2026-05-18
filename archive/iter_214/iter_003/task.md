Now that the `LateWindowDisplacementFitness` function has been implemented (`iter_214.1`) and validated (`iter_214.2`), launch a new evolutionary search for a `v<c` glider using this new fitness function.

1.  Configure the evolutionary search to use `fitness_v_lessthan_c.LateWindowDisplacementFitness`.
2.  Use the standard 3-bit L-Tromino seed.
3.  Run the evolution for 10 generations with a population size of 100.
4.  The goal is to discover a rule with a non-zero fitness score, which would indicate sustained motion in the late window (steps 500-1000).
5.  Save the final population, champion rule, and a plot of fitness vs. generation to `archive/iter_214/results/`.