# Research Manager Journal & Strategic State

## 1. High-Level Strategy & Trajectory
*   **Current Phase:** Phase 7 (Particle Zoo & Interacting Field Theory) - Transitioning from 7.1 (Glider Taxonomy) to Multi-Site / Non-Local Interaction Rules.
*   **Active Direction:** Abandoning single-cell 13-channel LGCA and 2.5D stacking/coupling models. Moving to true multi-site block partition CAs or coupled integer field models on the 3D FCC lattice.
*   **Trajectory Update (Iteration 252):** Iteration 252 has established a definitive theoretical and empirical barrier to the "2D-stacking" approach. While a 2D hex glider (which propagates via cooperative survival, where local cell weights fluctuate) can be embedded into a [111] plane of the FCC lattice as an algebraic identity, any inter-plane coupling ($\alpha > 0$) siphons bits away and immediately destroys the glider. This confirms that 3D physical gliders cannot be constructed by simply coupling 2D layers under a single-cell LGCA framework.
*   **Confidence Score:** 99% (Highly confident that single-cell local coupling of dimensionally reduced planes is structurally incapable of preserving cooperative-survival gliders).

## 2. Strategic Insights & Lessons Learned
*   **The Cooperative Survival Constraint:** The 2D hex $v=0.469c$ glider is a genuine bound state because it utilizes *cooperative survival* (where a single isolated bit annihilates, but multiple bits in close proximity survive). This requires local non-bit-conservation (local Hamming weight fluctuations, though globally conserved across the grid).
*   **The Siphoning Flaw:** In a 13-bit single-cell LGCA, any coupling parameter $\alpha > 0$ that maps in-plane channels to out-of-plane channels acts as a destructive siphon. It strips away the constituent bits of the glider, breaking the precise spatial neighborhood patterns required for cooperative survival, resulting in rapid dispersion and annihilation.
*   **The Algebraic Impossibility of local 13-bit LGCA for 2D Hex:** A strictly bijective, bit-conserving local LUT on a single cell cannot support the 2D hex cooperative survival mechanics because it is mathematically impossible to map weight-1 states to 0 while maintaining overall bijectivity and bit-conservation inside a localized 13-bit state space without spatial buffering.

## 3. Loop & Bottleneck Detection
*   **Resolved Loop:** The attempt to construct 3D gliders by embedding and coupling 2D hex planes has been terminated with a clear null result. The $\alpha = 0$ state is a trivial, anisotropic 2.5D projection; the $\alpha > 0$ state is unstable.
*   **Next Potential Bottleneck:** Designing multi-site partitioning schemes (such as Margolus-like block neighborhoods on the FCC lattice) that conserve global bit count and maintain reversibility while allowing the local weight fluctuations necessary for cooperative survival.

## 4. Alternate Research Paths
*   **Multi-Site Partitioning CA (Highest Priority):** Partition the FCC lattice into multi-cell blocks (e.g., tetrahedral or octahedral blocks) where local block transitions are bijective and conserve total block bits, allowing internal bits to fluctuate between cells and emulate neighborhood-overlap cooperative survival.
*   **Subgroup Symmetry Reduction:** Investigate whether reducing the required symmetry from the full octahedral group $O_h$ to a subgroup (e.g., $D_{3d}$ or $C_{4v}$) opens up bijective, bit-conserving channel-mixing orbits that are otherwise forbidden by $O_h$ non-conjugate stabilizers.