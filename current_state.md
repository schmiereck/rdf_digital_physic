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

### Refuted
- Simple, unconditional neighbor-swap rules on a 2D hex grid do NOT produce local oscillators, but result in trivial global shifts (iter_017).
- The standard Cellular Automaton (node-centric) update model is unable to execute a symmetric, bit-conserving conditional swap, leading to bit loss (iter_019).

### Current Best Result
A stable, two-cell composite particle propagating at v=c/2 in 1D (iter_014).

### In Progress
- **iter_020:** Testing if a symmetric, swap-based update model can finally produce a non-trivial, localized 2D glider. This is a critical experiment to unblock 2D exploration.
