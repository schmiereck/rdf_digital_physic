Phase: 3 - Evolutionary Search

### Goal
Observe deterministic, bit-conserving scattering in a 2D hexagonal grid.

### Status
**MAJOR PIVOT.** The project is pursuing a bottom-up, evolutionary approach after all top-down, formal rule design methods failed. The core evolutionary loop has been validated and has successfully bred a second generation of rules with significantly higher average "complexity fitness" than the initial random population. The current focus is analyzing the behavior of the best evolved rules to see if they support the desired glider dynamics.

### Confirmed
- **Evolutionary Process Works (iter_084):** Crossover and mutation of elite rules from Gen-1 successfully produced a Gen-2 population with a 166% higher mean fitness score, confirming the evolutionary strategy is directionally correct.
- **Fitness Metric Validated (iter_082):** A metric based on population mean and variance effectively discriminates between rules that produce trivial (static, dead) and complex dynamics.
- **Formal Search Failure (iter_049-081):** A comprehensive search of formally designed rules (based on symmetry, conservation, etc.) failed to produce any moving particles. This paradigm has been abandoned.

### In Progress
- **iter_085:** Analyzing the single best rule from the evolved Gen-2 population to determine if its high abstract fitness score translates into concrete support for stable, moving gliders.
