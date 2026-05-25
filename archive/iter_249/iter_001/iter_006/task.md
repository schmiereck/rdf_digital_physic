Implement the LUT construction and coherence testing module.

1. Create 'src/lut_construction_nonadditive.py' to construct three distinct non-additive LUT variants:
   - LUT-INT-EXCHANGE (nonadditive_lut_exchange.npy)
   - LUT-INT-BINDING (nonadditive_lut_binding.npy)
   - LUT-INT-SCATTERING (nonadditive_lut_scattering.npy)
   
   Ensure that:
   - All three variants are constructed by modifying LUT-08 weight-2 entries equivariantly under the 48 O_h permutations to maintain symmetry, and bijectively to maintain reversibility.
   - Specifically:
     - For EXCHANGE: Map O_2 (ch[0,4]) to ch[1,5] and O_3 (ch[2,4]) to ch[3,5].
     - For BINDING: Map O_2 (ch[0,4]) to ch[0,4] (identity) and O_3 (ch[2,4]) to ch[2,4] (identity).
     - For SCATTERING: Map O_2 (ch[0,4]) to ch[2,6] and O_3 (ch[2,4]) to ch[0,6] (default) and O_0 (ch[0,1]) to ch[4,5].
   - Programmatically verify that each variant is a bijection, is bit-conserving, and is fully O_h-symmetric. If any verification fails, debug and fix the mapping.
   - Save the verified LUTs as .npy files in 'src/'.

2. Create 'src/nonadditive_lut_metadata.json' documenting exactly what was modified and why, including:
   - The mathematical proof that a strict BINDING (mapping O_2/O_3 to O_1) or strict SCATTERING (mapping O_2/O_3 to O_1) is impossible because the sizes of the orbits (24 vs 6) make any equivariant map non-injective (violating bijection/reversibility).
   - The physical rationale and choice of same-stabilizer targets for each variant.

3. Create 'src/coherence_testing.py' implementing the three-test protocol:
   - Test A (decomposition): Check if the multi-bit grid at every step is exactly equal to the bitwise OR of independent solo runs of each constituent bit.
   - Test B (bit-removal): Check if removing each bit from the initial condition destabilizes the trajectory of the remaining bits (i.e., their combined grid differs from their independent run).
   - Test C (collision interaction): Check if colliding the candidate with a single-bit test particle results in a non-trivial outcome (change in velocities/energies).

Verify all files are written and run the construction script to generate the .npy files and metadata.