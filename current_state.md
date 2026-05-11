Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is catastrophically blocked. All attempts to seed an evolutionary search for gliders have failed. The core problem is that random rule generation strategies are not producing candidates with the right balance of activity and stability to show motion, giving the evolutionary algorithm no initial material to work with.

### Confirmed
- **Density Paradox (iter_097-099):** In a "primordial soup" evaluation, "dense" rules remain chaotic, while "sparse" rules (whether targeted to low- or high-density states) are too inactive to affect the soup's structure.
- **Random Populations are Barren (iter_094-096):** Random populations of C6, C2, and dense C2 rules contain zero simple gliders findable from small contiguous seeds.
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to all non-moving rule archetypes.
- **Formal Search Exhausted (iter_049-081):** All top-down, principled rule design strategies have failed to produce motion.

### In Progress
- **iter_101:** Re-running the "cooling" rule generation experiment from iter_100, which failed due to a code error. This strategy creates rules that map medium-density states to low-density states, a direct attempt to resolve the "density paradox". This is the last unexplored rule generation strategy.
