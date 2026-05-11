Phase: Focused Exploration (Phase 3 - Blocked)

**Goal:** Validate interaction logic (scattering) in a 2D hexagonal lattice. The immediate sub-goal is to create a symmetric, non-trivial rule that supports moving particles.

**Confirmed:**
- Hand-crafted, non-symmetric rules can produce stable 2D gliders (iter_024).
- A formal search can identify "conflict-free" kernels for generating symmetric rules (iter_033).
- A symmetric swap-based update model guarantees bit conservation for local swaps (iter_020).

**Refuted:**
- A symmetric rule generated from a kernel pair (A,B) where A and B are in the same rotational orbit is dynamically trivial (iter_035).
- Hand-crafted rules for 2D motion often lack rotational symmetry, making them unsuitable for general physics (iter_028, iter_029).
- Simple symmetric rules tend to produce inert or stationary patterns (fixed points/oscillators) rather than gliders (iter_021, iter_032, iter_035).
- Simple, local, unconditional rules on the hex grid tend to produce trivial global shifts, not localized particles (iter_017).

**Current Best Result:**
- Arrowhead Glider: A stable 3-bit glider moving East under a non-symmetric rule (iter_024).

**In Progress:**
- iter_036: A formal search for a conflict-free rule kernel (A,B) where A and B belong to disjoint rotational orbits.
