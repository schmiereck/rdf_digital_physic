The experiment in `iter_167` failed because a C2-symmetric rule cannot move a C2-symmetric seed. This task is to re-run that experiment with a critical change: use an asymmetric seed to break the symmetry.

Your task is to:
1.  Implement a new evolutionary search (`evolve.py`) based on the existing framework.
2.  Use the same fitness metric: `displacement / (1 + final_bit_count)`.
3.  Seed the simulation grid not with a symmetric `2x2` block, but with an asymmetric 3-bit "L-tromino" particle placed at the center. The L-tromino should occupy cells `(63, 63)`, `(64, 63)`, and `(64, 64)`.
4.  Evaluate a fresh, random population of 100 C2-symmetric rules.
5.  The hypothesis is that breaking the seed's symmetry will allow for motion. The experiment is successful if at least one rule in the population achieves a fitness score > 0.1.
6.  Write the full results, including `mean_fitness`, `max_fitness`, and the ID of the top rule, to `archive/iter_170/results/gen_0_results.json`.