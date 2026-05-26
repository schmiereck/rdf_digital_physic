# RDF Milestone Review — Iteration 252 — Null Result: Inter-Plane Coupling of 2D Hexagonal Gliders on FCC [111] Planes

## 1. Pre-Declared Hypothesis and Falsification Criterion
*   **Hypothesis:** The stable 2D hexagonal glider ($v=0.469c$) can be embedded into a [111] plane of the 3D FCC lattice, and a non-zero inter-plane coupling ($\alpha > 0$) can generate stable 3D bound states with non-zero out-of-plane momentum.
*   **Falsification Criteria:**
    1.  **F3 (Pure LGCA Impossibility):** Triggered if a 13-bit local, bijective, bit-conserving LUT cannot reproduce the 2D hex glider's cooperative survival rules on the in-plane subspace.
    2.  **F4c (Coupling Refutation):** Triggered if for all tested coupling strengths $\alpha > 0$, the embedded glider undergoes complete dispersion or annihilation within 100 steps.

## 2. Experimental Protocol
*   **Engine:** Hybrid CA-LGCA Engine on a 3D FCC grid ($L = 64$ along stacking axes).
*   **In-plane Update:** Synchronous cellular automaton executing the validated 2D hex glider rule (`champion_rule_perfect.json`).
*   **Inter-plane Update:** 13-channel LGCA mapping in-plane states to out-of-plane channels based on coupling parameter $\alpha \in [0.0, 0.5]$.
*   **Symmetry & Control:** Matched control run at $\alpha = 0$ (independent 2D slices). Single-bit isolation runs to verify constituent bit binding energy.

## 3. Observed Quantities
*   **Cooperative Survival Signature:** 200 out of 201 steps of the 2D hex glider propagation exhibit non-linear OR-superposition violations. 
*   **Single-Bit Isolation:** 100% of isolated constituent bits of the glider annihilate within 1 step (proving binding energy $> 0$).
*   **Coupling Lifetime ($\alpha > 0$):** For all non-zero coupling strengths ($\alpha = 0.1, 0.25, 0.5$), the glider disintegrated and completely annihilated within 10 steps. No stable or long-lived propagating structures were observed.
*   **Subspace Hamming Weight Transition:** Local state with 1 bit in an in-plane channel maps to 0 output bits under the 2D hex rule.

## 4. Verdict
**Refuted.** The hypothesis that stable 3D gliders can emerge from linearly coupling 2D cooperative-survival planes is completely refuted.

## 5. Construction-vs-Empirical Note
*   **Constructional Identity:** The propagation of the glider on the [111] plane at $\alpha = 0$ is an algebraic identity by construction, as the hybrid engine computes the in-plane transition using the identical 2D lookup table.
*   **Empirical Null Finding:** The immediate destruction of the glider for any $\alpha > 0$ is a genuine empirical finding of the dynamics. The coupling acts as a localized perturbation that drains the necessary density from the plane, breaking the non-linear cooperative survival threshold.

## 6. Limitations
*   This result proves that *single-cell* coupling of 2D planes is unstable. It does not rule out multi-site block updates or field-coupled architectures where spatial buffers can temporarily store and return siphoned bits without breaking the local cooperative survival thresholds.