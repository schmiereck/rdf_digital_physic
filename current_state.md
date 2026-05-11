Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is catastrophically blocked. All attempts to seed an evolutionary search for gliders have failed. Random populations of C6, C2, "sparse" C2, and "dense" C2 rules are all barren of motion when evaluated with either small contiguous seeds or a "primordial soup" of random noise. The core problem is that the random rule generation strategies are not producing candidates with the right balance of activity and stability.

### Confirmed
- **Soup Evaluation Failure (iter_097, 098):** Neither "dense" nor "sparse" C2 rules can resolve a chaotic soup into a low-density state. Dense rules remain chaotic; sparse rules are inert because their mappings target low-density neighborhoods not found in the soup.
- **Random Populations are Barren (iter_094, 095, 096):** Random populations of C6, C2, and dense C2 rules contain zero simple gliders findable from small contiguous seeds.
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to all non-moving rule archetypes.
- **Formal Search Exhausted (iter_049-081):** Top-down, principled rule design has failed to produce motion.

### In Progress
- **iter_099:** Testing a new "targeted sparse" rule generation strategy. Rules are generated with their active mappings deliberately biased towards high-density neighborhoods to see if they can "cool" a chaotic soup into a structured state.
