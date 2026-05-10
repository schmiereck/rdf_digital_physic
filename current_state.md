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
- Simple, unconditional rules on a 2D hex grid result in trivial global shifts, not local particles (iter_017).
- The standard CA update model is unable to execute a simple bit-conserving conditional swap, leading to bit loss (iter_019).
- Simple conditional swap rules, even with complex seeds or asymmetric logic, fail to produce motion and result in stationary oscillators or fixed points (iter_021, iter_022, iter_023).

### Current Best Result
A stable, stationary two-bit oscillator in 2D (iter_020).

### In Progress
- **iter_024:** Attempting to construct a stable, moving 3-bit glider by returning to the standard CA model with a carefully hand-crafted, reversible permutation rule. This is a direct attempt to overcome the limitations of the simpler rules and particles that have failed to produce motion.
