Implement and execute the O_h-symmetric non-additive LUT construction and exhaustive multi-bit glider search for the 3D FCC lattice.

### Background & Discoveries from 250.2.1
- The 4 weight-2 orbits have stabilizers of size 4, 8, 2, 2. Their stabilizer conjugacy classes are distinct, so they cannot map to each other.
- Orbit O_0 has 4 valid same-stabilizer targets.
- Orbit O_1 has 2 valid same-stabilizer targets.
- Orbit O_2 has 4 valid same-stabilizer targets.
- Orbit O_3 has 4 valid same-stabilizer targets.
- This results in exactly 4 * 2 * 4 * 4 = 128 unique O_h-symmetric weight-2 configurations in the entire universe of rules!
- The antipodal transposition weight-1 sub-table (ch0<->ch1, ch2<->ch3, ch4<->ch5, ch6<->ch9, ch7<->ch10, ch8<->ch11) is 100% O_h-symmetric.

### Goal
1. Build `src/non_additive_lut_v2.py` that constructs:
   - The ADDITIVE control LUT (with the antipodal transposition weight-1 sub-table, and additive extension for all other weights).
   - Any of the 128 unique O_h-symmetric weight-2 sub-table configurations (with weight-1 as the transposition, and all weight-3+ as additive extensions).
2. Build `src/experiment_250_nonadditive_search.py` that:
   - Uses a high-speed sparse simulator (using coordinates and channels, similar to `src/experiment_248_fundamental_spectrum.py`) to run seeds for 200 steps on an L=32 FCC grid.
   - For speed, abort any simulation early if the bit count deviates from the initial bit count (as we seek stable, perfectly bit-conserving, non-exploding gliders).
   - **Exhaustive Sweep**: Sweep ALL 128 unique weight-2 configurations across ALL 66 weight-2 seeds (2 bits in the same cell). This is a mathematically complete search of the entire weight-2 symmetric rule space!
   - **Control Sweep**: Run the same 66 seeds under the ADDITIVE control LUT (expected: 0 moving gliders, only stationary oscillators).
   - Log any candidates that have:
     - Perfect bit count preservation (remains exactly 2).
     - Displacement > 2.0 lattice units over 200 steps.
     - Pattern spread < 4.0 units (localization).
3. If any candidates are found, perform the **Three-Test Coherence Verification** (Decomposition, Stability, and O_h Covariance) as specified in `src/pre_registration.md`.
4. Write a detailed, rigorous markdown report to `archive/iter_250/results/nonadditive_search_report.md` documenting the results (including the counts of candidates, any that passed/failed the tests, and if no gliders were found, a definitive refutation statement of the hypothesis and F2/F3 triggered). Keep language restrained, precise, and scientific. No hype.