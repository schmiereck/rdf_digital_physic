# RDF Milestone Review — Iteration 242 — Phase 7.2: Charge & Chirality Analogs

## 1. Pre-Declared Hypothesis and Falsification Criterion
The working hypothesis is that the stable LUT-08 sub-light glider on the 3D FCC lattice possesses internal discrete charges (chirality and sub-lattice parities) that are conserved under vacuum propagation and asymptotically conserved across multi-particle interactions.

Falsification Criterion:
- Refuted if the total asymptotic charge (sum of chiralities and sub-lattice distributions) is not conserved across at least 10 independent, non-trivial collision configurations.
- Refuted if the gliders disintegrate into unclassified debris or non-propagating structures during the interactions.

## 2. Experimental Protocol
- **Lattice and Grid Size:** 3D FCC grid mapped to a stack-of-hexagonal-layers coordinate system, simulated on a $64 \times 64 \times 64$ grid.
- **Rule:** The native O_h-symmetric, bit-conserving LUT-08 rule.
- **Configurations:**
  1. Vacuum propagation of an isolated single glider and its spatially reflected counterpart ($x \to -x$).
  2. 10 distinct, non-trivial collision configurations of two gliders, covering head-on, off-center, and glancing impact parameters.
- **Measurements:** Tracked total active bits (system-wide and localized), center-of-mass trajectories, sub-lattice occupancy vector $\mathbf{q}(t)$ across the 4 fcc simple cubic sub-lattices ($L_0, L_1, L_2, L_3$), and the chirality charge $\chi(t)$ computed via the signed volume of the tetrahedra formed by active cell offsets relative to the center of mass.
- **Control Run:** Matched vacuum propagation of isolated single gliders to establish baseline kinematics and charge periodicity.

## 3. Observed Quantities
- **Vacuum Kinematics:** The chirality charge $\chi(t)$ alternates periodically between $-4.0$ (even steps) and $+2.0$ (odd steps) with a temporal period of 2 steps. The sub-lattice occupancy vector $\mathbf{q}(t)$ alternates between $(0, 1, 1, 2)$ and $(2, 1, 1, 0)$ via an involutive cyclic permutation vector $(3, 2, 1, 0)$.
- **Mirror Symmetry:** The spatial reflection ($x \to -x$) of the glider is stable and propagates at the same velocity magnitude ($v \approx 0.5c$ along the temporal projection), with its chirality charge exactly negated ($+4.0$ on even steps, $-2.0$ on odd steps).
- **Collision Elasticity:** In 10 out of 10 collision runs, the gliders emerged intact as stable propagating entities after localized interaction.
- **Charge Conservation:**
  - Total bit count remained at $8$ bits ($4$ bits per glider) across all runs, which is exact by construction due to the strict bit-conserving nature of the transition rule.
  - The sum of asymptotic chiralities ($\chi_{\text{in}} = \chi_{\text{out}}$) was conserved across all 10 runs when evaluated at matching temporal phases.
  - Asymptotic sub-lattice parities ($\mathbf{Q}_0 = \mathbf{Q}_f$) were conserved across all 10 runs.

## 4. Verdict
The observed quantities are **consistent with the hypothesis** that the LUT-08 glider carries robust, additively conserved discrete charges. The pre-declared falsification threshold (perfect conservation across 10 configurations) was successfully satisfied, and the hypothesis is not refuted.

## 5. Construction-vs-Empirical Note
- **Definitional/Constructional:** The periodic alternation of the sub-lattice occupancy $\mathbf{q}(t)$ and chirality $\chi(t)$ in vacuum is a mathematical consequence of the chosen grid projection and the glider's period-2 trajectory. The existence and stability of the enantiomer under spatial reflection is guaranteed by the $O_h$-symmetry of the transition rule.
- **Genuinely Empirical:** The 100% elasticity of all 10 tested collision configurations is a non-trivial dynamical property. In general discrete systems, collisions under non-linear rules lead to chaotic scattering, fusion, or fragmentation. The survival of the gliders and the asymptotic restoration of their charges represent a physical stability reminiscent of solitons.

## 6. Limitations
This result does not show that *all* possible collision configurations are elastic; there may exist highly fine-tuned impact parameters or multi-particle states that result in annihilation or fusion. Furthermore, the conservation of charge is demonstrated here only for a homogeneous system of LUT-08 gliders and their enantiomers. It remains to be seen whether these conservation laws hold when interacting with other hypothetical particle species on the 3D FCC lattice.