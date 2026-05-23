# RDF Scientific Pre-Registration

*   **Iteration:** 240
*   **Pre-Registration File:** src/pre_registration.md

## 1. Hypothesis
The 3D FCC CA rule supporting LUT-08 admits at least one other distinct stable, bit-conserving, propagating glider species (with non-zero coordinate velocity) of Hamming weight W <= 12 that belongs to an O_h symmetry orbit distinct from that of LUT-08, with its coordinate speed strictly less than the diagonal speed of light limit c = sqrt(2).

## 2. Falsification Criterion
The hypothesis will be refuted if:
1. The systematic search of all initial configurations with Hamming weight W <= 12 within a 4x4x4 bounding box simulated for 200 steps yields zero stable, propagating gliders (non-zero velocity, period-stable) that belong to an O_h orbit distinct from LUT-08.
2. Any newly discovered glider species exhibits a normalized speed |v|/c >= 1.0.
3. The O_h orbit equivalence classification fails to group known symmetry-related configurations of LUT-08 into a single orbit of size 48 (or appropriate subgroup divisor).

## 3. Proposed Method
1. Implement a 3D FCC CA search engine in `src/fcc_search.py` that utilizes the established LUT-08 CA rule.
2. Implement an initial condition generator to sweep configurations of Hamming weights W = 4 to 12 within a 4x4x4 bounding box.
3. Simulate each candidate for 200 steps. Filter out candidates that die (W=0), blow up (W > 24), or remain stationary (displacement of CoM is 0).
4. Verify stability of surviving gliders by confirming that the velocity and bit pattern are periodic over the final 100 steps.
5. Implement an O_h symmetry checker in `src/fcc_symmetry.py` that applies the 48 elements of the octahedral group to group the discovered gliders into unique orbit equivalence classes.
6. Analyze and document the discovered species, computing their normalized velocity vector and confirming |v| < sqrt(2).

---
*Created automatically by the RDF Orchestrator prior to iteration execution.*
