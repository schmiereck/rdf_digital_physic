The characterization in 216.2 revealed that the supposed `v<c` glider is actually a `v=1c` glider. This implies a flaw in the `LateWindowDisplacementFitness` function used in the successful `iter_215` search.

Your task is to analyze the fitness function's implementation and behavior to understand why it selected for a `v=1c` glider and then propose a new fitness function that specifically targets `v<c` particles.

1.  **Analyze `src/fitness_functions.py`:**
    *   Locate the `LateWindowDisplacementFitness` class.
    *   Examine its `__call__` method.
    *   Identify why maximizing `late_window_displacement` would favor a `v=1c` glider over a slower one.

2.  **Hypothesize a `v<c` Fitness Metric:**
    *   Propose a new fitness function principle that explicitly rewards sub-light-speed motion. A key idea is to look for internal oscillations. A `v<c` glider *must* have an internal state that changes with a period greater than its movement step (e.g., period 4 oscillator that moves 1 cell every 4 steps). A `v=1c` glider has no such complex internal structure.
    *   Consider metrics like `displacement / period` or a fitness function that requires a minimum period > 2.

3.  **Design the New Function:**
    *   Outline the implementation of a new fitness function class, `SubLightFitness`.
    *   Describe the metrics it would need to calculate (e.g., displacement, bit count, and particle state periodicity).
    *   Explain how these metrics would be combined to create a fitness score that is high for `v<c` gliders and low for `v=1c` gliders, stationary oscillators, and chaotic patterns.

4.  **Output:** Write your analysis and the design for the new fitness function into a markdown file at `archive/iter_216/results/fitness_analysis.md`.