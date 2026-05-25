Update src/pre_registration.md to:
1. Fix the falsification logic from AND-gate to OR-gate:
   Change "The hypothesis is refuted if ALL of the following hold simultaneously: F1, F2, F3" to:
   "The hypothesis is refuted if ANY of the following hold: F1 OR F2 OR F3 OR F4"
2. Define the falsification criteria exactly as:
   - F1: Across all non-additive LUT variants tested (>=3 distinct interaction types) and all O_h-distinct two-bit collision geometries (>=6 initial configurations per variant), no two-bit bound state survives >=200 steps post-collision.
   - F2: Any two-bit candidate that survives 200 steps passes the single-bit decomposition test (i.e., running each bit independently reproduces the multi-bit trajectory), proving it is still a non-interacting composite.
   - F3: Any bound state exists only along one lattice axis and disappears when initial conditions are rotated through O_h symmetry elements.
   - F4: The constructed non-additive LUTs violate reversibility (not a bijection) or bit conservation.
3. Update the confirmation criterion exactly as:
   "If ANY genuine multi-bit glider is found that: (a) survives >=200 steps, (b) fails the decomposition test, (c) is destabilized by single-bit removal, and (d) transforms covariantly under O_h rotations, then the hypothesis is confirmed."

Verify that the changes are written successfully to src/pre_registration.md.