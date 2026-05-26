Write and execute the exhaustive non-additive multi-bit glider search on the 3D FCC lattice, leveraging the correct Cartesian mapping and the already-verified 128 non-additive weight-2 configurations.

### Key Bridging of Coordinate Systems
To perfectly align the Cartesian channel indexing used by `src/non_additive_lut_v2.py` and `src/search_3d_gliders.py`'s O_h group with the physical shifts used by `src/engine_3d.py`, we construct the Cartesian shift vectors `CAR_SHIFTS` as follows:
```python
from src.engine_3d import SHIFTS
from src.search_3d_gliders import fcc_neighbor_vectors

def get_car_shifts():
    S = np.array(SHIFTS, dtype=float)
    C = fcc_neighbor_vectors().astype(float)
    # The linear transformation BT maps Cartesian to Grid coordinates: C @ BT = S_permuted
    BT = np.linalg.inv(C[[0, 4, 8]]) @ S[[0, 2, 6]]
    
    CAR_SHIFTS = []
    for i in range(12):
        s_expected = C[i] @ BT
        diff = np.abs(S - s_expected)
        idx = np.argmin(diff.sum(axis=1))
        assert diff[idx].sum() < 1e-5, f"No matching shift for Cartesian vector {C[i]}"
        CAR_SHIFTS.append(SHIFTS[idx])
    return CAR_SHIFTS

CAR_SHIFTS = get_car_shifts()
```

### Goal
1. Build `src/experiment_250_nonadditive_search.py` that:
   - Imports `build_additive_lut`, `build_nonadditive_lut`, `build_randomized_w3plus_lut` from `src/non_additive_lut_v2.py`.
   - Uses `CAR_SHIFTS` in `simulate_unwrapped` so that the simulation perfectly aligns with the Cartesian indexing of the LUT.
   - For speed, abort any simulation early if the bit count deviates from the initial bit count (as we seek stable, perfectly bit-conserving, non-exploding gliders).
   - **Exhaustive Sweep**: Sweep ALL 128 unique weight-2 configurations across ALL 66 weight-2 Cartesian seeds (2 bits in the same cell: all combinations of 2 active channels in `0..11`). This is a mathematically complete search of the entire weight-2 symmetric rule space!
   - **Control Sweep**: Run the same 66 seeds under the ADDITIVE control LUT (expected: 0 moving gliders).
   - **Weight-3 Sweep**: Sweep all 40 randomized weight-3+ LUT variants across all 220 weight-3 single-cell seeds.
   - Log any candidates that have:
     - Perfect bit count preservation (remains exactly 2 or 3).
     - Displacement > 2.0 lattice units over 200 steps.
     - Pattern spread < 4.0 units (localization).
2. If any candidates are found, perform the **Three-Test Coherence Verification** (Decomposition, Stability, and O_h Covariance) as specified in `src/pre_registration.md` and rotate particles using `rotate_particle_list` with `M_g = S_rot.T @ S_pinv.T`.
3. Write a detailed, rigorous scientific markdown report to `archive/iter_250/results/nonadditive_search_report.md` documenting the results (including the counts of candidates, any that passed/failed the tests, and if no gliders were found, a definitive refutation statement of the hypothesis and F2/F3 triggered). Keep language restrained, precise, and scientific. No hype.