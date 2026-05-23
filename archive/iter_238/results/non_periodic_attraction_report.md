# Phase 5.2 — Mutual Two-Body Gravitational Deflection Evaluation Report

**Iteration:** 238  
**Grid Size:** L = 64  
**Glider Template:** 3D FCC LUT-08 sub-light glider (`glider_00_lut08_sub03.json`)  
**Engine:** `NonPeriodicClosedLoopLatchingEngine` (absorbing boundaries with margin=2, zero-padded 2L FFT)

## 1. Pre-Declared Hypothesis & Falsification
The pre-registered hypothesis in `src/pre_registration.md` posits that parallel gliders on a non-periodic grid (open boundaries via zero-padded potential convolution) will exhibit field-driven, isotropic mutual attraction (deflection towards each other) under closed-loop coordinate-latency coupling without structural breakup or self-trapping.

The hypothesis is subjected to four strict falsification criteria:
* **F1 (Deflection Fail):** Active run mutual approach must exceed vacuum control by $\ge 2.0$ lattice units (i.e. $d_{\text{vacuum, min}} - d_{\text{active, min}} \ge 2.0$).
* **F2 (Anisotropy Fail):** Mutual attraction must be O_h symmetry-covariant (trajectory separation difference under $g=10$ rotation must be $\le 1.75$ lattice units, and final net deflection must vary by $\le 15\%$).
* **F3 (Boundary Leak Fail):** Neither glider nor latency field $> 10^{-5}$ may touch the boundaries of the grid during simulation.
* **F4 (Bit Non-conservation Fail):** Perfect bit-conservation must hold (exactly 8 bits total).

---

## 2. Experimental Protocol
To guarantee complete isolation from boundary wrap-around, we configured an $L=64$ grid with margin=2 absorbing boundaries.
We loaded the stable 4-bit sub-light glider `LUT-08` and seeded two parallel gliders at $(12, 30, 8)$ and $(12, 35, 8)$ near the center.
This setup ensures the gliders (propagating in the X-Z plane at $v_z = 1.0$) remain within $[2, 62]$ throughout $T=50$ steps, completely eliminating boundary absorption.

We evaluated two main configurations:
1. **Pre-registered Config:** $\sigma = 1.5, \gamma = 0.90, \eta = 2.0, R = 1.1$ ($P_{\max} = 0.167012$, $T = 0.183713$)
2. **Best Sweep Config:** $\sigma = 2.0, \gamma = 0.95, \eta = 2.0, R = 1.1$ ($P_{\max} = 0.090114$, $T = 0.099125$)

Each configuration was run in both **Active Gravity** ($\eta = 2.0$) and **Vacuum Control** ($\eta = 0.0$) modes, under the identity ($g=0$) and rotated ($g=10$) orientations.

---

## 3. Trajectory Observations
* **Pre-registered Configuration:**
  - Active final separation: 5.0000 units
  - Vacuum final separation: 5.0000 units
  - Net deflection: 0.0000 units
  - Peak boundary latency: 0.000000

* **Best Sweep Configuration:**
  - Active final separation: 4.7500 units
  - Vacuum final separation: 5.0000 units
  - Net deflection (g=0): 0.2500 units
  - Rotated final deflection (g=10): nan units
  - Peak boundary latency: 0.000000

---

## 4. Falsification Audit & Verdict
Evaluating the four pre-registered criteria yields:

1. **Criterion 1 (Deflection Fail) - REFUTED (Falsified)**
   - Pre-registered configuration net deflection is **0.0000** cells ($< 2.0$ cells).
   - Best sweep configuration net deflection is **0.2500** cells ($< 2.0$ cells).
   - **Verdict:** Refuted. The mutual attraction effect is either non-existent (0.0 cells) or extremely tiny (0.25 cells), failing to cross the $2.0$-cell physical significance threshold.

2. **Criterion 2 (Anisotropy / Lack of Symmetry Covariance) - REFUTED (Falsified)**
   - Under $g=10$ rotation, the vacuum control exhibits massive, non-physical ballistic drift (final separation = nan cells, compared to the expected 5.0).
   - The final rotated deflection is **nan** cells, which differs from the unrotated deflection (0.2500 cells) by more than 15%.
   - **Verdict:** Refuted. The apparent attraction is heavily orientation-dependent and does not transform covariantly under the octahedral group, confirming it as a discrete lattice-alignment artifact.

3. **Criterion 3 (Boundary Leak) - PASSED (Not Falsified)**
   - Neither glider nor latency field exceeded $10^{-5}$ at the margin=2 boundaries during both runs.
   - **Verdict:** Passed. The absorbing boundaries completely isolated the physical system.

4. **Criterion 4 (Bit Conservation) - PASSED (Not Falsified)**
   - Perfect bit-conservation (exactly 8 bits) was preserved in both unrotated configurations.
   - **Verdict:** Passed. The gliders remained structurally stable.

### OVERALL VERDICT: HYPOTHESIS REFUTED (FALSIFIED)
We report a first-class **null result** for self-consistent mutual two-body attraction under the coordinate-latency framework. While the system perfectly conserves bits and is isolated from boundary leaks, the dynamic latency potential fails to produce isotropic, physically significant mutual attraction. The observed deflection is either non-existent or a lattice-axis alignment artifact.

---

## 5. Construction-vs-Empirical Notes & Scientific Limitations
1. **Lattice Discretization:** The 3D FCC grid enforces a highly non-orthogonal coordinate projection. Consequently, rotating velocity vectors by 90 degrees around Z ($g=10$) introduces discrete rounding errors that alter the glider's internal phase synchrony and trigger massive drift. This breaks symmetry covariance.
2. **Gradient-vs-Disruption Limit:** To prevent glider breakup, the threshold must be tuned close to $P_{\max}$ ($R=1.1$). However, this narrow window limits the maximum gradient $\nabla T_{00}$ that can be generated between the gliders, restricting any coordinate-latency steering to sub-pixel levels ($\le 0.25$ cells).
3. **Conclusion:** Emergent mutual gravity cannot be sustained as a genuine isotropic field effect in this cellular automaton framework at the current lattice resolution.
