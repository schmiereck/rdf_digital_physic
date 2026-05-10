Phase: Phase 3 – Focused Exploration (2D Hex-Kollision)

### Goal
To demonstrate that complex physical phenomena can emerge from a minimal set of local, reversible rules on a discrete lattice.

### Confirmed
- **1D System:**
  - Non-trivial, reversible, bit-conserving rules exist (iter_009, iter_011).
  - Stable gliders with v=c and v<c (mass) can be constructed (iter_010, iter_013, iter_014).
  - 1D glider rules can be classified by their interaction properties (ELASTIC, FUSION, CHAOTIC) (iter_018).
- **2D Hex System:**
  - A hand-crafted, reversible, bit-conserving rule using the standard CA model can support a stable, non-trivial 3-bit glider moving through a static background (iter_024). This unblocks the study of 2D interactions.
  - A symmetric swap-based update model guarantees bit-conservation for local swaps and can create stable, stationary oscillators (iter_020).

### Refuted
- Simple, unconditional rules (e.g., bit-rotation) on a 2D hex grid result in trivial global shifts, not local particles (iter_017).
- The standard CA update model cannot execute simple conditional swaps without violating bit-conservation (iter_019).
- Simple conditional swap rules, even with complex seeds or asymmetric logic under a bit-conserving scheduler, fail to produce motion and result in stationary oscillators or fixed points (iter_021, iter_022, iter_023).
- A single '1' bit is NOT a stationary particle under the arrowhead-glider rule; it propagates at the same velocity as the glider (iter_026).

### Current Best Result
A stable, 3-bit "arrowhead" glider that propagates at v=(1,0) in a 2D hexagonal grid (iter_024).

### In Progress
- **iter_027:** Probing the arrowhead-glider rule for a simple, stationary two-bit pattern to serve as a valid collision target.
