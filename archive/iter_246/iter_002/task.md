## Task: Sweep All 24 Proper O_h Rotations on L=64 Grid

### Context
In iter_245 and sub-goal 246.1, we found that O_h-rotated opposite-chirality collisions produce Chaotic outcomes on both L=32 and L=64, while the unrotated collision is Elastic. The coordinate-rounding diagnostic revealed sub-lattice phase mismatches as the cause. However, only 2 proper O_h rotations were tested out of 24. This sub-goal sweeps ALL 24 proper O_h rotations to create a complete anisotropy map.

### What to Create: `src/experiment_246_multi_rotation.py`

Create a Python script that:

**1. Setup:**
- Load LUT-08 from `archive/iter_224/results/glider_00_lut08_sub03.json`
- Build all 48 O_h transforms using `build_oh_transforms()` from `src/rigorous_glider_audit.py`
- Filter to the 24 proper rotations (det=+1)
- Construct pA (original), pB (P-reflected via `reflect()` from `src/glider_charge_analysis.py`)
- Grid: L=64, 80 steps per collision

**2. For each of the 24 proper rotations (indexed 0-23):**
- Apply the rotation to both pA and pB bit patterns (same as iter_245's `rot()` function)
- Apply the rotation to the placement origins
- Compute coordinate-rounding diagnostic:
  - Max rounding error: max(|float_pos - rounded_pos|) across all 8 bits
  - Sub-lattice phase pattern: compute (l%2, r%2, c%2) for each bit, look up SUB dictionary
  - Flag: alignment_mismatch = True if any bit has invalid sub-lattice (-1) OR rounding error > 1e-10
- Run the collision on L=64 for 80 steps
- Classify outcome (Elastic/Partial/Chaotic/Annihilation) using same taxonomy

**3. Special case — Identity rotation:**
- The identity rotation (M=I, perm=identity) should be among the 24 proper rotations
- This serves as a built-in control: it should reproduce the unrotated Elastic result
- If it doesn't, there's a bug in the rotation implementation

**4. Output:**
- Print a table: index | det | outcome | bits | n4 | n1 | max_round_err | alignment_mismatch | sub_pat_Ar | sub_pat_Br
- Count: how many rotations produce Elastic? How many Chaotic? How many Partial?
- Among those with alignment_mismatch=False, how many produce Elastic?
- Save complete results to `archive/iter_246/results/multi_rotation_sweep.json`
- Print a summary at the end

**5. Analysis question:**
After the sweep, identify any proper O_h rotations that produce Elastic outcomes WITHOUT alignment mismatch. These would confirm that O_h covariance holds when the rotation preserves sub-lattice fidelity. If NONE of the 24 rotations (besides identity) produce Elastic, this is evidence that the LUT-08 glider's velocity vector [0.25, -0.5, 1.0] is inherently non-axis-aligned, making it impossible for ANY rotation (other than identity) to preserve sub-lattice fidelity.

### Key Source Files
- `src/engine_3d.py` — stream(), collide()
- `src/glider_charge_analysis.py` — make_BT(), reflect()
- `src/rigorous_glider_audit.py` — build_oh_transforms(), seed_grid(), compute_com_circular()
- `src/experiment_246_oh_covariance_64.py` — the sub-goal 1 script (reference for diagnostic approach)

### Implementation Notes
- Use the same `clusters()`, `classify()`, `place()` functions from iter_245's approach
- The placement origin for unrotated: pA at (22, 32, 22), pB at (42, 32, 42)
- For rotated: transform both origins by M and round to int, then mod L
- SUB dictionary: {(0,0,0): 0, (1,1,0): 1, (1,0,1): 2, (0,1,1): 3} — if (l%2, r%2, c%2) is not in SUB, assign -1
- Keep script under 150 lines
- The script should NOT read pre_registration.md (it's a computational sweep, not a hypothesis test)