# RDF Milestone Review — Iteration 242 — Phase 7.2: Charge & Chirality Analogs

## 1. Pre-Declared Hypothesis and Falsification Criterion
*   **Hypothesis:** The stable 4-bit sub-light glider (LUT-08) on the 3D FCC lattice carries discrete, conserved physical charges—specifically Cartesian chirality ($\chi$) and simple-cubic sub-lattice parity distributions ($\mathbf{q}$)—which are asymptotically conserved across multi-particle interactions (collisions), protecting them from decay and acting as robust quantum-number analogs.
*   **Falsification Criterion:** Refuted if the total chirality sum ($\chi_{\text{in}} \neq \chi_{\text{out}}$) or asymptotic sub-lattice parities ($\mathbf{Q}_0 \neq \mathbf{Q}_f$) are not additively conserved across $\ge 10$ independent, non-trivial collision configurations, or if the charges are unstable during vacuum propagation.

## 2. Experimental Protocol
*   **Grid and Parameters:** 3D FCC grid of size $32 \times 32 \times 32$ with periodic boundaries, evolved under the $O_h$-symmetric, bit-conserving, reversible LUT-08 rule.
*   **Test Cases:** 
    1. *Vacuum Case:* Evolution of a single LUT-08 glider and its mirror reflection ($x \to -x$) over 100 steps.
    2. *Collision Cases:* 10 independent dual-glider collision runs with varying initial spatial offsets, relative phases, and impact parameters (including head-on and glancing angles).
*   **Control Run:** Dual gliders launched in parallel trajectories with no collision contact (vacuum control) to establish non-interacting charge baselines.

## 3. Observed Quantities
*   **Vacuum Chirality Oscillation:** The single glider's Cartesian chirality $\chi(t)$ oscillates with a period of 2 steps, taking values of $-4.0$ on even steps and $+2.0$ on odd steps. The mirror-reflected glider exhibits perfectly negated chirality ($\chi_m(t) = -\chi(t)$), taking $+4.0$ on even steps and $-2.0$ on odd steps.
*   **Vacuum Sub-lattice Occupancy:** The sub-lattice occupancy vector $\mathbf{q}(t)$ oscillates periodically between $(0, 1, 1, 2)$ and $(2, 1, 1, 0)$, governed by a cyclic permutation matrix representing a discrete subgroup of the Klein 4-group.
*   **Collision Outcomes:** 10 out of 10 collision runs resulted in 100% elastic scattering. The gliders entered a localized, chaotic interaction zone, but emerged intact as stable LUT-08 gliders.
*   **Asymptotic Conservation:** 
    *   Total bit count was conserved at exactly 8 bits.
    *   The asymptotic sum of chirality was perfectly conserved ($\chi_{\text{in}} = \chi_{\text{out}}$) for all 10 runs.
    *   The asymptotic sub-lattice occupancy parities were perfectly preserved ($\mathbf{Q}_i = \mathbf{Q}_f$).
    *   Falsification threshold (any violation in $\ge 10$ runs): **0 violations observed.**

## 4. Verdict
**Consistent.** The experimental evidence is fully consistent with the hypothesis that the LUT-08 glider possesses stable, discrete, and additively conserved chirality and sub-lattice charges that protect its structural integrity during collisions.

## 5. Construction-vs-Empirical Note
The decomposition of the 12-channel FCC lattice into four simple cubic sub-lattices is an algebraic consequence of the chosen grid geometry (constructional). Similarly, the definition of Cartesian chirality from coordinate offsets is geometric. However, the *stability* of the LUT-08 glider under evolution, its periodic period-2 internal charge oscillation, and the fact that these charges are *asymptotically and additively conserved* during complex local contact in 10 distinct collision configurations (rather than dispersing into background radiation or mutating into other states) are genuine empirical discoveries of the LUT-08 rule.

## 6. Limitations
*   This milestone does not show whether these charges remain conserved in inelastic processes (e.g., particle production or annihilation), which is the subject of downstream Phase 7.3 and 7.4.
*   The collision sweep was limited to 10 discrete configurations; a continuous scattering matrix has not been mapped.
*   The lattice scale is small, meaning macroscopic continuum limits of charge conservation have not yet been evaluated.