Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is catastrophically blocked. All attempts to seed an evolutionary search for gliders have failed. Random populations of C6, C2, and "dense" C2 rules have all proven to be barren of motion when evaluated with a comprehensive suite of small, contiguous seeds (iter_094-096). A pivot to evaluating rules in a "primordial soup" of random noise also failed, as the "dense" rules tested were too chaotic to produce structure (iter_097).

### Confirmed
- **Dense C2 Rules are Too Chaotic for Soup (iter_097):** All 100 dense C2 rules maintained a high-density, chaotic state when seeded with random noise.
- **Random Populations are Barren (iter_094, 095, 096):** Random populations of C6, C2, and dense C2 rules contain zero simple gliders findable from small contiguous seeds.
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to all non-moving rule archetypes.
- **Formal Search Exhausted (iter_049-081):** Top-down, principled rule design has failed to produce motion.

### In Progress
- **iter_098:** Testing a new hypothesis: that rules known to be stabilizing (but not chaotic) with small seeds might be capable of "cooling" a chaotic soup into a low-density state of persistent, emergent objects.
