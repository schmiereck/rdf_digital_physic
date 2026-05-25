## Task: Build and Run L=64 O_h Covariance Experiment with Coordinate-Rounding Diagnostics

### Context
In iter_245, the O_h covariance test showed that rotating an opposite-chirality head-on collision setup through a proper O_h element changed the outcome from Elastic to Chaotic on an L=32 grid. This phase tests whether this is a boundary artifact or genuine physics, with critical attention to coordinate-rounding artifacts.

### Pre-Registration (MANDATORY — read and follow)
First, read `src/pre_registration.md` for the current pre-registered hypothesis and falsification criteria. Then UPDATE `src/pre_registration.md` with the following ADDITIONAL falsification criteria (append to section 2):

```
F4-enhanced (Grid-Rounding Diagnostic): If the O_h-rotated collision produces a different outcome than the unrotated collision on L=64, AND the coordinate-rounding diagnostic shows that the rotated configuration has a different relative sub-lattice phase or different minimum spatial separation than the unrotated configuration, the non-covariance is classified as a DEFINITIONAL ALIGNMENT MISMATCH (coordinate-rounding artifact), NOT a failure of dynamic O_h covariance in the CA rule. In this case, the non-covariance is attributed to the discrete lattice's inability to represent the rotated configuration with sufficient geometric fidelity.

F5 (Multi-rotation consistency): If F4-enhanced identifies a coordinate-rounding mismatch, but at least one OTHER proper O_h rotation produces the same Elastic outcome as the unrotated configuration (with matching sub-lattice phases), then O_h covariance is partially confirmed for axis-aligned rotations, with the limitation documented.
```

### Experiment Script: `src/experiment_246_oh_covariance_64.py`

Create a Python script that:

**1. Load LUT-08 and construct particles:**
- Load from `archive/iter_224/results/glider_00_lut08_sub03.json`
- Construct pA (original LUT-08), pB (P-reflected via `reflect()` from `glider_charge_analysis.py`), pC (same-chirality reversed-velocity via O_h rotation scan as in iter_245)

**2. L=64 Grid Configuration:**
- Grid size L=64 (not 32)
- Toroidal boundaries
- Collision center at (32, 32, 32)
- Initial separation: pA at (22, 32, 22), pB at (42, 32, 42) — this gives ~20-cell separation along the diagonal approach axis, well within the 64³ grid
- 80 simulation steps

**3. Coordinate-Rounding Diagnostic (CRITICAL — mandated by Strategic Manager):**
Before running any collision, for BOTH the unrotated and rotated configurations, compute and print:
- The exact floating-point Cartesian positions of each bit of both gliders (using BT_inv from `make_BT()`)
- The sub-lattice index (0,1,2,3) of each bit using the parity formula: SUB = {(0,0,0):0, (1,1,0):1, (1,0,1):2, (0,1,1):3}, where the key is (l%2, r%2, c%2)
- The relative sub-lattice phase between the two gliders (difference in sub-lattice occupancy patterns)
- The minimum Euclidean distance (in lattice units, toroidal-corrected) between any bit of glider A and any bit of glider B at t=0
- The coordinate-rounding error for each bit of the rotated glider: |float_position - rounded_position| for the (l,r,c) coordinates after applying M_g
- A summary flag: "ALIGNMENT_MISMATCH=True" if either (a) the rounding errors exceed 1e-10 for any bit, OR (b) the relative sub-lattice phases differ between rotated and unrotated configurations

**4. Collision Runs on L=64:**

Run these collision configurations:

(a) **Unrotated opposite-chirality** (pA vs pB): expected Elastic (reproduces iter_245)

(b) **O_h-rotated opposite-chirality**: Apply the SAME O_h rotation used in iter_245 (first non-identity proper rotation from `build_oh_transforms()` with det=+1). Rotate both particles' bit patterns AND their placement positions.

(c) **Second O_h rotation**: A different proper O_h rotation (e.g., swap axes y↔z, which is another proper rotation). This tests whether non-covariance is specific to one rotation or general.

For each: run the collision for 80 steps, classify the outcome using the same taxonomy as iter_245 (Elastic/Partial/Chaotic/Annihilation).

**5. Solo Stability Controls:**
Run solo propagation for 80 steps on L=64 for: pA, pB, rotated-pA, rotated-pB, second-rotated-pA, second-rotated-pB. Verify bit count = 4 at every step.

**6. Same-chirality collisions on L=64:**
Run pA vs pC head-on collision on L=64 for 80 steps. Classify outcome. This is a control and data for debris analysis.

**7. Classification function:**
Use the same classification as iter_245:
- Elastic: exactly 2 four-bit clusters, 8 bits total
- Annihilation: 0 four-bit clusters, all bits isolated (1-bit clusters)
- Partial: exactly 1 four-bit cluster + debris
- Chaotic: 0 four-bit clusters + debris

**8. Output:**
- Print all diagnostic information to stdout
- Save results to `archive/iter_246/results/oh_covariance_64_results.json`
- Write `archive/iter_246/results/RESEARCH-RESULT-246.md` with:
  - Pre-Declared Hypothesis & Falsification (from updated pre_registration.md)
  - Protocol
  - Observations (table of outcomes + coordinate-rounding diagnostics)
  - Verdict (evaluate each falsification criterion)
  - Construction-vs-Empirical Note
  - Limitations

### Key Source Files to Reference
- `src/engine_3d.py` — stream(), collide(), SHIFTS
- `src/glider_charge_analysis.py` — make_BT(), reflect()
- `src/rigorous_glider_audit.py` — build_oh_transforms(), seed_grid(), compute_com_circular()
- `src/phase7_3_cpt_experiment.py` — the iter_245 experiment (reference for classification, clustering)

### IMPORTANT CONSTRAINTS
- The script must read and print `src/pre_registration.md` at startup before running any simulation
- Do NOT attempt post-hoc parameter tuning if non-covariance persists
- If coordinate-rounding alters the impact parameter, report it honestly as a definitional alignment mismatch
- Keep the script under 200 lines
- Use the `clusters()` and `classify()` functions from iter_245's approach
- The L=64 grid with center at (32,32,32) ensures debris cannot wrap around within 80 steps