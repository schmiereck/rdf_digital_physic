Phase: Phase 3 – Focused Exploration (2D Hex-Kollision)

### Goal
To demonstrate that complex physical phenomena can emerge from a minimal set of local, reversible rules on a discrete lattice.

### Confirmed
- **1D System:**
  - Non-trivial, reversible, bit-conserving rules exist for 1D systems with 1-bit and 2-bit cells (iter_001, iter_003).
  - 1-bit rules support stable v=c gliders (iter_002).
  - 2-bit rules support stable v=0 oscillators and v<c gliders (single and composite) (iter_004, iter_005, iter_014).
  - 1D glider rules can be classified by their interaction properties (ELASTIC, FUSION, CHAOTIC) based on a two-bit seed (iter_018).
- **2D Hex System:**
  - Trivial v=c gliders (equivalent to global grid shifts) exist in 2D hex grids (iter_016).

### Refuted
- A simple, unconditional neighbor-swap rule on a 2D hex grid does NOT produce a local oscillator, but instead reduces to a trivial global shift (iter_017).

### Current Best Result
A stable, two-cell composite particle propagating at v=c/2 in 1D, demonstrating that particles with internal structure and reduced velocity are possible (iter_014).

### In Progress
- **iter_019:** Testing a conditional swap rule to create the first non-trivial, localized 2D glider.
