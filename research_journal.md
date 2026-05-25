# Research Manager Journal & Strategic State

## 1. High-Level Strategy & Trajectory
*   **Current Phase:** Phase 7 (Particle Zoo) - Sub-phase 7.3 (Antiparticles & CPT Symmetries)
*   **Active Direction:** Evaluating CPT-like symmetries and testing whether the P-reflected (enantiomeric) counterpart of the LUT-08 sub-light glider behaves as an annihilating antiparticle.
*   **Trajectory Update (Iteration 245):** Iteration 245 successfully executed the Phase 7.3 protocols. It established a definitive, first-class **null result**: the P-reflected enantiomer ($p_B$) is stable but does *not* annihilate upon collision with the original glider ($p_A$); instead, opposite-chirality collisions are perfectly elastic, while O_h non-covariance was triggered due to lattice-axis sensitivity for non-axis-aligned gliders. We are now preparing to transition to Phase 7.4 (Pair Production & Annihilation) or re-evaluate the exact CPT operations under time-reversal on larger grids to eliminate finite-size boundary effects.
*   **Confidence Score:** 50% (Slightly adjusted downward due to the discovery of O_h non-covariance in rotated collision setups on the current lattice scale).

## 2. Strategic Insights & Lessons Learned
*   **Elasticity of Chiral Enantiomer Collisions:** The P-reflected enantiomer of LUT-08 possesses an opposite chiral charge sequence. However, rather than acting as an annihilating "anti-state," it behaves as a robust independent species. Its collisions with the original glider are perfectly elastic (5/5 cases), preserving total bit counts and identity asymptotically.
*   **Broken O_h Covariance at Finite Lattice Scales:** Rotating the collision axis changes the physical outcome from elastic to chaotic scattering. Because the LUT-08 velocity vector ($[0.25, -0.5, 1.0]$) is not aligned with any high-symmetry O_h axis, there is no exact antiparallel rotation partner, forcing lateral glancing angles. Moreover, coordinate-rounding on the discrete layer-stacking grid breaks exact rotational invariance during multi-particle interactions.
*   **C, P, T Equivalence Constraints:** On this binary lattice, the Charge-conjugation (C) operator is equivalent to Parity (P) since chirality is the only defined charge. Consequently, CPT is equivalent to pure Time-reversal (T). True particle-antiparticle annihilation may require reversing the transition rule itself ($f^{-1}$) rather than using spatial reflections under the forward rule ($f$).

## 3. Loop & Bottleneck Detection
*   **Active Bottleneck:** Finite-size toroidal boundary interactions and discrete grid rounding artifacts.
*   **Mitigation Strategy:** To distinguish genuine physical non-covariance from grid resolution limits, future collision sweeps must be conducted on open-boundary (absorbing) grids of size $\ge 64^3$ or $128^3$.

## 4. Alternate Research Paths
*   **Rule-Inversion Annihilation:** Explore explicit $f^{-1}$ backward-in-time propagation to construct true CPT-conjugate states that annihilate under the forward rule, bypassing the geometric limitations of spatial P-reflections.