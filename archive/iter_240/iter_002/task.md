Write and execute a robust, comprehensive python script `src/exhaustive_glider_search.py` to search for stable propagating sub-light gliders under the LUT-08 rule on the 3D FCC lattice.

The script must:
1. Load the LUT from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. Implement O_h symmetry and translation canonicalization to compute unique representative orbits of particle configurations:
   - Apply translation canonicalization to make the relative coordinate coordinates of the active bits lexicographically minimal.
   - Apply the 48 O_h permutations to find the unique lexicographically minimal rotation-translation orbit representative.
3. Compute the canonical orbit representative of the known LUT-08 glider to serve as a reference.
4. Set up a grid size of L=20 and a simulation duration of T=80 steps.
5. Track cumulative center-of-mass (circular-unwrapped) displacement and maximum spatial extent at each step.
   - A candidate is stable if its active bit count remains constant (exact weight W) and its maximum extent remains <= 6 across all 80 steps.
   - A candidate is a propagating glider if its net displacement norm at step 80 is >= 4.0 lattice units.
   - Check if the shape sequence is periodic (perfect shape recurrence).
6. Implement three independent, rigorous search methods:
   - **Method A: Systematic Connected Sweep** for W=4 and W=5:
     - Generate all unique connected coordinate shapes of size 1, 2, and 3 cells.
     - For each connected cell coordinate shape, distribute W bits among the channels.
     - Group these particles by their canonical orbit representative to simulate only unique orbits.
   - **Method B: Massive Randomized Compact Search** for 4 <= W <= 8:
     - Generate at least 1000 unique, contiguous, and compact random particles for each weight W.
     - Group by canonical orbit representative and simulate unique orbits.
   - **Method C: Genetic Algorithm (GA)** for 4 <= W <= 8:
     - Run a GA for each weight W with a population of 100 individuals for 20 generations.
     - Use compact random particles for initialization.
     - Mutation must preserve weight and connectedness (shift a bit to a neighboring empty slot).
     - Crossover must select W contiguous bits from the union of parents.
     - Fitness = net displacement norm (or 0 if maximum extent > 6). Give a fitness bonus if the shape is periodic.
7. Collect all unique discovered gliders. Check if any are in an O_h orbit disjoint from LUT-08.
8. Write a complete scientific report to `archive/iter_240/results/exhaustive_search_report.md` detailing the methods, sweep size, and findings (whether a new glider was discovered or a robust null result was confirmed).
9. Save any newly discovered gliders to JSON files in `archive/iter_240/results/`.
10. Save a summary of the search to `archive/iter_240/results/search_summary.json`.

Execute the script, verify that it runs to completion, and print its stdout and key metrics.