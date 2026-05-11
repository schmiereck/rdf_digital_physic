Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid. This requires first finding a stable, moving particle ("glider").

### Status
The project is catastrophically blocked. All attempts to seed an evolutionary search for gliders have failed. Random populations of C6-symmetric, C2-symmetric, and "dense" C2-symmetric rules have all proven to be barren of motion when evaluated with a comprehensive suite of small, contiguous seeds (iter_094, 095, 096). This indicates the evaluation methodology itself, which assumes gliders are elemental particles, is likely flawed.

### Confirmed
- **Dense C2 Population Barren (iter_096):** A random population of 100 "dense" C2-symmetric rules contains zero simple gliders from small contiguous seeds. Increasing rule activity does not spontaneously create motion.
- **C2 Random Population Barren (iter_095):** A random population of 100 C2-symmetric rules contains zero simple gliders.
- **C6 Random Population Barren (iter_094):** A random population of 100 C6-symmetric rules contains zero simple gliders.
- **Motion-Based Fitness Metric is Selective (iter_090):** The metric `displacement / (1 + final_bit_count)` correctly assigns zero fitness to all non-moving rule archetypes.
- **Formal Search Exhausted (iter_049-081):** Top-down, principled rule design has failed to produce motion.

### In Progress
- **iter_097:** Pivoting the evaluation strategy. Instead of small seeds, we are now seeding with a "primordial soup" of random noise to find rules that can "cool" chaos into a low-density state of persistent objects. This is a search for emergent, rather than elemental, complexity.
