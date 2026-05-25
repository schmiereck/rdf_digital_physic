# Iteration 246: O_h Covariance on L=64

## Pre-Declared Hypothesis & Falsification Criteria
See `src/pre_registration.md` for the full pre-registration.

## Protocol
- Grid: L=64 FCC toroidal
- Collision center: (32, 32, 32)
- Origins: pA at (22, 32, 22), pB at (42, 32, 42)
- Steps: 80
- O_h rotations: first=[[-1.0000000000000002, -2.7755575615628914e-16, -2.1514659057761885e-16], [-1.9999999999999996, 0.9999999999999994, 0.9999999999999996], [-6.661338147750939e-16, -5.551115123125783e-17, -0.9999999999999998]], second=[[0.9999999999999991, -0.9999999999999999, -0.9999999999999998], [-3.3306690738754696e-16, -1.0, -2.3592239273284576e-16], [-6.661338147750939e-16, -5.551115123125783e-17, -0.9999999999999998]]

## Observations

### Coordinate-Rounding Diagnostic (Rotation 1)
- max_rounding_error: 1.0
- phase_mismatch: True
- alignment_mismatch: True
- min_sep_unrot: 25.45584412271571
- min_sep_rot: 31.176914536239792
- sub_pat_A: (1, 2, 3, 3)
- sub_pat_B: (-1, -1, 3, 3)
- sub_pat_Ar: (-1, -1, -1, 1)
- sub_pat_Br: (-1, -1, -1, 3)

### Coordinate-Rounding Diagnostic (Rotation 2)
- max_rounding_error: 0.0
- phase_mismatch: True
- alignment_mismatch: True
- min_sep_unrot: 25.45584412271571
- min_sep_rot: 18.0
- sub_pat_A: (1, 2, 3, 3)
- sub_pat_B: (-1, -1, 3, 3)
- sub_pat_Ar: (-1, -1, 3, 3)
- sub_pat_Br: (1, 2, 3, 3)

### Solo Stability
- pA: STABLE
- pB: STABLE
- pAr: STABLE
- pBr: STABLE
- pA2: STABLE
- pB2: STABLE

### Collision Outcomes
| Config | Outcome | Bits | n4 | n1 |
|--------|---------|------|----|----|
| unrotated_opposite | Elastic | 8 | 2 | 0 |
| oh_rotated_1 | Chaotic | 8 | 0 | 5 |
| oh_rotated_2 | Chaotic | 8 | 0 | 2 |
| same_chirality | Partial | 8 | 1 | 1 |

## Verdict

**F1** (Rotated differs from unrotated): REFUTED
  - Unrotated: Elastic, Rotated-1: Chaotic

**F2** (Unrotated not Elastic): NOT REFUTED

**F3** (Solo stability failed): NOT REFUTED

**F4-enhanced**: ALIGNMENT MISMATCH identified.
  Outcome difference attributed to coordinate-rounding artifact.

**F5**: Not applicable or not confirmed.

## Construction-vs-Empirical Note
All glider structures were constructed algorithmically from the LUT-08 seed. No post-hoc parameter tuning was performed.

## Limitations
- Only two O_h rotations tested; full 48-element group coverage not attempted.
- Classification taxonomy is coarse (Elastic/Partial/Chaotic/Annihilation).
- Debris dynamics not analysed beyond bit counting.
- L=64 grid may still exhibit wrap-around effects for very long runs (>80 steps).