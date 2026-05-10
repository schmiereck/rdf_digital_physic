Phase: Phase 3 – Focused Exploration (2D Hex-Kollision)

### Goal
To demonstrate that complex physical phenomena can emerge from a minimal set of local, reversible rules on a discrete lattice.

### Confirmed
- **1D System:**
  - Non-trivial, reversible, bit-conserving rules exist for 1D systems (1-bit and 2-bit cells) (iter_009, iter_011).
  - Stable gliders with v=c and v<c (mass) can be constructed (iter_010, iter_013, iter_014).
  - 1D glider rules can be classified by their interaction properties (ELASTIC, FUSION, CHAOTIC) (iter_018).
- **2D Hex System:**
  - Formal rule space exists and supports trivial v=c gliders (global grid shifts) (iter_015, iter_016).
  - A symmetric swap-based update model enables the creation of a stable, localized, period-2 oscillator using a conditional rule (iter_020).

### Refuted
- Simple, unconditional neighbor-swap rules on a 2D hex grid do NOT produce local oscillators, but result in trivial global shifts (iter_017).
- The standard Cellular Automaton (node-centric) update model is unable to execute a symmetric, bit-conserving conditional swap, leading to bit loss (iter_019).

### Current Best Result
A stable, two-cell composite particle propagating at v=c/2 in 1D (iter_014). In 2D, a stable, stationary two-bit oscillator (iter_020).

### In Progress
- **iter_021:** Testing if a composite conditional swap rule can produce a non-trivial, localized 2D glider.
