Phase: Phase 3 – Focused Exploration (2D Hex-Kollision)

### Goal
To demonstrate that complex physical phenomena can emerge from a minimal set of local, reversible rules on a discrete lattice.

### Confirmed
- **1D System:**
  - Non-trivial, reversible, bit-conserving rules exist for 1D systems (iter_009, iter_011).
  - Stable gliders with v=c and v<c (mass) can be constructed (iter_010, iter_013, iter_014).
  - 1D glider rules can be classified by their interaction properties (ELASTIC, FUSION, CHAOTIC) (iter_018).
- **2D Hex System:**
  - A symmetric swap-based update model guarantees bit-conservation for local swaps (iter_020).
  - This model, with a conditional rule, can create a stable, localized, period-2 stationary oscillator (iter_020).

### Refuted
- Simple, unconditional neighbor-swap rules on a 2D hex grid result in trivial global shifts, not local particles (iter_017).
- The standard Cellular Automaton (node-centric) update model is unable to execute a symmetric, bit-conserving conditional swap, leading to bit loss (iter_019).
- A composite conditional swap rule with a symmetric two-bit seed does NOT produce a glider, but another stationary oscillator (iter_021).
- An asymmetric 'L-shaped' three-bit seed with the composite rule does NOT produce a glider, but a stable fixed point (iter_022).

### Current Best Result
A stable, stationary two-bit oscillator in 2D (iter_020).

### In Progress
- **iter_023:** Testing if a fundamentally asymmetric swap rule can finally produce a non-trivial 2D glider.
