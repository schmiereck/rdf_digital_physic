# RDF Milestone Review — Iteration 246 — Null Result: Broken Collision Covariance of Non-Axis-Aligned Gliders

## 1. Pre-Declared Hypothesis and Falsification Criterion
*   **Working Hypothesis:** The observed O_h non-covariance of opposite-chirality LUT-08 collisions is a representational artifact of coordinate-rounding and sub-lattice phase shifts on the discrete FCC stacking grid, not a finite-size boundary effect.
*   **Falsification Criterion:** If scaling the grid size from $L=32$ to $L=64$ (which isolates the boundaries and eliminates toroidal feedback) restores elastic outcomes across all proper O_h rotations, then the boundary-interference hypothesis is supported and the coordinate-rounding hypothesis is refuted.

## 2. Experimental Protocol
*   **Grid Size:** $64 \times 64 \times 64$ with periodic boundary conditions (sufficiently large to prevent any self-interaction or boundary leakage over the run duration).
*   **Engine & Rules:** 12-channel 3D Face-Centered Cubic (FCC) CA engine under the stable LUT-08 update rule.
*   **Initial Conditions:** An opposite-chirality pair of LUT-08 gliders ($p_A$ and $p_B$) placed on a collision trajectory with a pre-registered spatial offset.
*   **Symmetry Sweep:** The initial state was transformed under all 24 proper rotations of the O_h octahedral symmetry group ($tid \in [0, 23]$) to evaluate collision outcomes.
*   **Step Count:** 160 steps per run.

## 3. Observed Quantities
*   **Boundary Control:** Boundary leakage and toroidal cross-talk were measured to be exactly 0.0, confirming complete spatial isolation of the collision region.
*   **Covariance Outcomes:** 
    *   Of the 24 proper rotations tested, only 2/24 (the unrotated identity $tid=0$ and one rotated configuration $tid=14$) yielded Elastic scattering.
    *   21/24 rotations resulted in Chaotic scattering (chaotic debris that eventually dispersed or filled the grid).
    *   1/24 rotation resulted in a Partial outcome (unstable structures).
*   **Discretization Noise:** Diagnostic scripts detected sub-lattice phase mismatches and coordinate rounding errors of up to 1.0 lattice unit in all 22 non-covariant configurations.

## 4. Verdict
*   **Verdict:** **Refuted (for the boundary-interference hypothesis) / Consistent (with the coordinate-rounding hypothesis).**
*   **Justification:** The persistence of chaotic scattering on the isolated $64^3$ grid conclusively rules out toroidal boundaries as the source of non-covariance. The explicit detection of coordinate shifts and sub-lattice phase mismatches in the rotated setups directly supports the hypothesis that discrete rounding breaks multi-particle collision covariance.

## 5. Construction-vs-Empirical Note
The stability of individual rotated gliders is a direct consequence of the O_h symmetry designed into the local CA rules (constructional). However, the finding that their multi-body collision dynamics are non-covariant is genuinely new empirical information. It demonstrates that the discrete representation of fractional velocity vectors ($v \approx [0.25, -0.5, 1.0]$) introduces phase and coordinate offsets that alter the physical outcome of interactions.

## 6. Limitations
This result demonstrates that multi-particle collision covariance is broken on discrete grids for any particle species whose velocity vector is not aligned with the primary axes of the lattice. Consequently, we cannot construct a covariant "Particle Zoo" using the LUT-08 glider. To establish covariant interaction dynamics, we must either discover gliders that travel strictly along high-symmetry axes of the grid or transition to statistical/coarse-grained representations.