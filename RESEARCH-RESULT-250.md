# RDF Milestone Review — Iteration 250 — Verification of 2D Hex Glider Coherence & Definitive Architectural Limits of 3D FCC LGCAs

## 1. Pre-Declared Hypothesis and Falsification Criterion
1.  **2D Hex Coherence Hypothesis:** The 2D Hex v=0.469c glider is a genuine bound state, not a non-interacting composite.
    *   *Falsification Criterion:* Refuted if any isolated sub-component of the 3-bit L-tromino seed can propagate stably on its own.
2.  **3D FCC Non-Additive LUT Hypothesis:** Introduction of O_h-symmetric, bijective, and bit-conserving non-additive weight-2 and weight-3 transitions in single-cell LUTs will allow stable, cohesive multi-bit gliders to emerge.
    *   *Falsification Criterion:* Refuted if exhaustive sweeps over 128 weight-2 and 40 weight-3+ O_h-symmetric non-additive LUT variants yield zero surviving multi-bit gliders over 200 steps.

## 2. Experimental Protocol
*   **2D Hex Audit:** Isolated each of the 3 constituent bits of the `champion_rule_perfect.json` glider seed on an L=128 hex grid, tracking survival over 200 steps against the control (the full 3-bit seed).
*   **3D FCC Search:** Constructed and simulated 128 weight-2 and 40 weight-3+ O_h-symmetric, bijective, and bit-conserving non-additive LUT variants. Seeded each with multiple spatial arrangements and ran propagation sweeps for 200 steps on a 3D FCC grid.

## 3. Observed Quantities
*   **2D Hex Coherence:** 
    *   Full 3-bit seed: Stable propagation over 200 steps (Velocity = 0.469c).
    *   Isolated Bit 1, 2, and 3: 0/3 survived. All isolated components decayed or dispersed immediately within <10 steps.
    *   *Result:* Clear evidence for a genuine bound state with dynamic binding energy $>0.0$.
*   **3D FCC Non-Additive Search:**
    *   Total configurations tested: 168 O_h-symmetric non-additive rules.
    *   Surviving multi-bit structures at step 200: 0.
    *   *Result:* Falsification criteria triggered; hypothesis refuted.

## 4. Verdict
*   **2D Hex Coherence:** **Consistent** with the hypothesis of a genuine dynamically bound particle.
*   **3D FCC Non-Additive LUTs:** **Refuted**. Single-cell non-additive updates cannot support stable multi-bit gliders in this lattice formulation.

## 5. Construction-vs-Empirical Note
*   The 2D Hex glider's binding mechanism is genuinely empirical. It arises from the non-linear interaction of adjacent bits updating through overlapping spatial neighborhoods, which is not forced by the lattice geometry.
*   The 3D FCC null result represents a fundamental structural limit of the single-cell collision architecture: because collision is strictly local to a single cell and propagation is a sterile parallel translation, bits in different cells can never exchange state or form stable, cohesive structures.

## 6. Limitations
*   This review confirms that single-cell LGCAs on the 3D FCC grid are limited to a monospecific spectrum of non-interacting, single-bit particles.
*   To establish a diverse particle zoo in three dimensions, we must redesign the CA engine to support multi-site interactions, which introduces significant symbolic and computational complexity to ensure bijectivity.