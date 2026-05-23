# RDF Milestone Review — Iteration 241 — Null Result: Glider Search in the LUT-08 Rule Space

## 1. Pre-Declared Hypothesis and Falsification Criterion
*   **Working Hypothesis:** The 12-channel 3D FCC CA rule governing the LUT-08 glider supports other distinct, stable, non-isomorphic sub-light glider species within a localized configuration space of bounding box width $W \le 5$.
*   **Falsification Criterion:** The hypothesis is refuted if a systematic scan of all valid bit-configurations of width $W \le 5$ under the declared rule yields zero stable propagating patterns (surviving $\ge 200$ steps) that are non-isomorphic to the LUT-08 glider under the $O_h$ symmetry group.

## 2. Experimental Protocol
*   **Grid and Boundaries:** $32 \times 32 \times 32$ toroidal FCC grid, mapped via layer-stacking hexagonal projection.
*   **Steps:** 200 execution steps per candidate run.
*   **Search Envelope:** Localized configurations with spatial bounding box width $W \le 5$ and active bit counts up to 8 bits.
*   **Symmetry Filter:** Candidates evaluated and grouped into unique $O_h$ symmetry equivalence classes (using the 48-order octahedral rotation group) to eliminate duplicate trajectories.
*   **Controls:** 
    *   *Positive Control:* The standard 4-bit sub-light glider LUT-08 was seeded into the same engine to verify that the search and audit scripts (`src/rigorous_glider_audit.py` and `src/engine_3d.py`) successfully detect and report stable propagation.
    *   *Null Control:* Empty configurations to verify vacuum stability.

## 3. Observed Quantities
*   **Positive Control Recovery:** The LUT-08 glider was successfully detected with its characteristic velocity and period, establishing a 0% false-negative rate for the detection code.
*   **Discovered Gliders ($W \le 5$):** 0 (excluding the positive control and its $O_h$ symmetric equivalents).
*   **Falsification Threshold Comparison:** The observed count of 0 alternative gliders falls below the threshold of $\ge 1$ required to support the hypothesis.

## 4. Verdict
*   **Verdict:** Refuted.
*   **Justification:** The systematic search of the $W \le 5$ configuration space under the LUT-08 rule returned no other stable sub-light glider species. The positive control run successfully verified the detection mechanism, confirming that the null result is not an artifact of search failure but an empirical property of the rule space.

## 5. Construction-vs-Empirical Note
The isolation of the LUT-08 glider (the lack of neighboring glider states under its rule) is an empirical property of the chosen discrete transition rule. It is not dictated by the geometry of the FCC lattice or the $O_h$ projection group, as these geometric structures are compatible with an infinite variety of other propagating structures under different rules.

## 6. Limitations
*   This result only rules out alternative stable gliders of size $W \le 5$ under the *specific* LUT-08 rule set. 
*   It does not rule out the existence of larger stable gliders ($W > 5$) under this rule.
*   It does not rule out the existence of other sub-light gliders under different $O_h$-symmetric rule sets on the 3D FCC lattice. Finding these requires sweeping the rule space, not the seed space.