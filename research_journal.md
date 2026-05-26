# Research Manager Journal & Strategic State

## 1. High-Level Strategy & Trajectory
*   **Current Phase:** Phase 7 (Particle Zoo & Interacting Field Theory) - Transitioning from 7.1 (Glider Taxonomy) to Multi-Site / Non-Local Interaction Rules.
*   **Active Direction:** Investigating mathematical and physical formulations of multi-site interaction rules on the 3D FCC lattice, specifically to bypass the single-cell and weight-2 orbit limitations identified in Iteration 251.
*   **Trajectory Update (Iteration 251):** Iteration 251 has established a major theoretical and empirical roadblock for the 13-channel (rest-mass) single-cell LGCA architecture. We have demonstrated that:
    1. Group-theoretic constraints prevent any $O_h$-equivariant bijections between weight-2 orbits ($C \leftrightarrow E$ and $B \leftrightarrow D$) due to non-conjugate stabilizer subgroups. This mathematically rules out simple weight-2 channel mixing.
    2. The addition of a rest-mass channel to cooperative trapping rules acting on adjacent 2-bit seeds produces stationary oscillators rather than moving gliders, dropping average displacement by 29x (7.35 vs 214.35).
    These findings strongly indicate that single-cell LGCA models—even with a rest channel—cannot support genuine, moving multi-bit bound states. This solidifies our pivot to true multi-site (neighborhood-overlap) or field-coupled architectures.
*   **Confidence Score:** 99% (Highly confident in the mathematical impossibility of single-cell $O_h$ weight-2 mixing and the freezing effect of the rest channel).

## 2. Strategic Insights & Lessons Learned
*   **The Stabilizer Subgroup Barrier:** On the FCC lattice, different orbits under the $O_h$ symmetry group have non-conjugate stabilizer subgroups. Consequently, we cannot construct a symmetric, bijective rule that maps elements of one weight-2 orbit directly to another (e.g., swapping a pair of parallel channels for a pair of orthogonal channels). This severely restricts the algebraic design space for single-cell collisions.
*   **The Rest-Mass Trapping Paradox:** A rest-mass channel intended to act as a binding core instead acts as an absolute kinetic brake. Cooperative trapping forces the propagating bits to orbit or cycle around the rest bit, locking the center of mass in place and producing stationary oscillators rather than translating composites.
*   **The Conservation Duality:** Our positive control (2D Hex $v=0.469c$ glider) succeeds precisely because it does *not* enforce strict per-cell bit conservation (the local bit count fluctuates between 3 and 4 during its period-6 propagation, though the total grid bit count remains conserved). Designing 3D rules with similar behavior requires shifting from per-cell channel permutations ($C: \mathbb{B}^{12} \to \mathbb{B}^{12}$) to multi-site blocks or field-like updates where local bit count fluctuates but global bit count is strictly conserved.

## 3. Loop & Bottleneck Detection
*   **Resolved Loop:** The search for stable gliders using the 13-channel single-cell rest-mass model has been terminated with a definitive null result.
*   **Next Potential Bottleneck:** Ensuring global conservation laws (total bit count and bijectivity/reversibility) in a multi-site or field-coupled framework. Multi-site update schemes often struggle to maintain strict bijectivity without complex, non-local coordination.

## 4. Alternate Research Paths
*   **Multi-Site Partitioning CA (Highest Priority):** Partition the 3D FCC lattice into blocks (e.g., 4-cell tetrahedral blocks or 8-cell octahedral blocks) and perform bijective, bit-conserving permutations on these multi-site blocks to mimic the neighborhood-overlap dynamics of 2D Hex.
*   **Coupled Integer Field Models:** Formulate the CA as coupled integer-valued fields on the FCC lattice nodes where local transitions emulate wave packet propagation and self-focusing, rather than tracking discrete point-like channel bits.