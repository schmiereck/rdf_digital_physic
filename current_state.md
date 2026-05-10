Phase: Phase 3 – Focused Exploration (2D Hex-Kollision)

### Goal
To demonstrate that complex physical phenomena can emerge from a minimal set of local, reversible rules on a discrete lattice.

### Confirmed
- **1D System:**
  - Non-trivial, reversible, bit-conserving rules exist (iter_009, iter_011).
  - Stable gliders with v=c and v<c (mass) can be constructed (iter_010, iter_013, iter_014).
  - 1D glider rules can be classified by their interaction properties (ELASTIC, FUSION, CHAOTIC) (iter_018).
- **2D Hex System:**
  - A hand-crafted, reversible, bit-conserving rule using the standard CA model can support a stable, non-trivial 3-bit glider moving East at v=(1,0) (iter_024).
  - A symmetric swap-based update model guarantees bit-conservation for local swaps and can create stable, stationary oscillators (iter_020).

### Refuted
- Simple, unconditional rules on a 2D hex grid result in trivial global shifts, not local particles (iter_017).
- Standard CA updates cannot execute simple conditional swaps without violating bit-conservation (iter_019).
- Simple conditional swap rules fail to produce motion, resulting in stationary patterns (iter_021, iter_022, iter_023).
- A single '1' bit is not a stationary particle under the arrowhead-glider rule; it propagates at v=(1,0), preventing collisions (iter_026).
- A simple two-bit pattern is not stable under the arrowhead-glider rule and decays (iter_027).
- The hand-crafted arrowhead-glider rule is NOT rotationally symmetric; a rotated seed pattern decays chaotically instead of producing a rotated glider (iter_028).

### Current Best Result
A stable, 3-bit "arrowhead" glider that propagates at v=(1,0) in a 2D hexagonal grid, via a non-symmetric rule (iter_024).

### In Progress
- **iter_029:** Generating a fully symmetric rule by applying 6-fold rotational symmetry to the arrowhead glider kernel, and testing if it still supports the original East-moving glider.
