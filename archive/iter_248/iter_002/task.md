You are working on a digital physics research project studying emergent physics on a 3D FCC lattice cellular automaton. Your task is to execute an ACTIVE TARGETED SEARCH for axis-aligned glider species on the FCC lattice, as mandated by the Research Manager.

## Background

The project has discovered one stable 3D glider: LUT-08, a 4-bit particle with period 2 and velocity [0.5, 0.0, 1.0] in grid coordinates under the LUT-08 rule. However, LUT-08 is NOT axis-aligned — its velocity has fractional components that cause O_h coordinate-rounding artifacts (see iter_246). The iter_241 "taxonomy search" was a smoke test (only 100 seeds under 1 LUT) and found nothing new. We need a thorough, active search.

## What You Must Do

Create `src/experiment_248_axis_aligned_search.py` and run it. The script must:

### Phase A: Single-Cell Seeds (Exhaustive)
For each Hamming weight k = 3..12:
- Enumerate ALL C(12, k) subsets of channels from {0..11}
- Create seed: `[(0, 0, 0, ch) for ch in subset]`
- Simulate 16 steps on L=32 grid under EACH of 4 LUT rules
- Check: bit count conserved AND max bounding extent ≤ 6 at every step AND net displacement > 0
- For any passing candidate: record displacement vector, extend to 64 steps to confirm

### Phase B: Two-Cell Seeds Along FCC Directions (Random Sample)
For each of the 12 FCC NN directions (the SHIFTS from engine_3d.py):
- Place cell1 at (0,0,0) and cell2 at the NN shift
- Randomly sample 300 seeds of total bit count 3-8 (split across both cells) per direction
- Simulate 16 steps under each LUT
- Same stability + displacement criteria

### Phase C: Multi-Cell Random Seeds
- Generate 5000 random seeds of 3-12 bits within a 3×3×3 cell block centered at origin
- Each bit is a random (dl, dr, dc, ch) where dl,dr,dc ∈ {-1,0,1} and ch ∈ {0..11}
- Simulate 16 steps under each LUT
- Same criteria

### Phase D: Verification of Candidates
For any stable, moving candidate from Phases A-C:
1. Extend simulation to 200 steps on L=32
2. Compute Cartesian velocity using the BT matrix from `src/glider_charge_analysis.py` (use `make_BT()` to get BT and BT_inv, then `cumdisp_grid @ BT` for Cartesian displacement)
3. Check axis-alignment: Cartesian velocity components should be integers or half-integers (max |component - round(component*2)/2| < 0.01)
4. Compute O_h canonical form using `src/rigorous_glider_audit.py` functions (`build_oh_transforms`, `oh_canonical`)
5. Compare canonical form with LUT-08 reference canonical form
6. If different O_h orbit AND axis-aligned: this is a NOVEL AXIS-ALIGNED SPECIES
7. For novel species: verify on L=64 grid with 300 steps
8. For novel species: test O_h covariance — rotate by one proper O_h element, simulate 200 steps, check if still stable with transformed velocity

### LUT Rules to Test
1. LUT-08 from `archive/iter_224/results/glider_00_lut08_sub03.json` (load the "lut" field)
2. Three additional O_h-symmetric LUTs generated using `src/search_3d_gliders.py:generate_symmetric_lut()` with seeds 42, 123, 999
   - You must also verify each generated LUT passes `verify_lut()` for bijection, bit-conservation, and O_h symmetry before using it

### Key Implementation Details

- Import from `src/engine_3d.py`: `stream`, `collide`, `SHIFTS`, `pack`, `unpack`
- Import from `src/rigorous_glider_audit.py`: `build_oh_transforms`, `oh_canonical`, `simulate`, `seed_grid`, `compute_com_circular`, `bounding_extent`, `grid_cells`
- Import from `src/search_3d_gliders.py`: `generate_symmetric_lut`, `get_oh_permutations`, `precompute_perm_action`, `compute_orbits`, `compute_all_stabilizers`, `verify_lut`
- Import from `src/glider_charge_analysis.py`: `make_BT`

- Use `seed_grid(L, particle)` to initialize the grid
- Use `compute_com_circular(grid)` for center-of-mass tracking
- For Cartesian velocity: compute cumulative displacement in grid coords, then multiply by BT matrix
- For axis-alignment check: velocity_cart = cumdisp_grid / steps @ BT, check each component is integer or half-integer

- For the O_h canonical form comparison, load the LUT-08 reference particle from the JSON file and compute its canonical form once at startup

### Output Requirements

1. Write `archive/iter_248/results/search_results.json` with:
```json
{
  "phase_a_candidates_tested": N,
  "phase_b_candidates_tested": M,
  "phase_c_candidates_tested": K,
  "luts_tested": 4,
  "stable_moving_candidates": [...],
  "axis_aligned_candidates": [...],
  "novel_species": [...],
  "f1_triggered": true/false,
  "summary": "..."
}
```

2. Write `archive/iter_248/results/search_report.md` with a comprehensive markdown report including:
   - Search parameters and coverage
   - All stable moving candidates found
   - Which are axis-aligned
   - Which are in novel O_h orbits
   - O_h covariance test results for any novel species
   - Final verdict (F1 triggered or novel species confirmed)

3. Write `archive/iter_248/results/species_table.csv` if any novel species found, with columns: species_id, bit_count, period, velocity_grid, velocity_cartesian, axis_aligned, oh_orbit_distinct_from_lut08, oh_covariant

### Performance Guidelines
- Keep the script under 250 lines
- Use vectorized numpy operations where possible
- Print progress every 1000 candidates
- Total runtime should be under 5 minutes

### CRITICAL: Pre-Registration Compliance
Read `src/pre_registration.md` first and ensure your search complies with the declared search space bounds:
- Bit count: 3-12
- Spatial extent: Manhattan distance ≤ 2 from origin
- Period: ≤ 8 steps
- Axis-alignment criterion: Cartesian velocity components are integers or half-integers
- Stability: bit-conserving, extent ≤ 6, at least 2×period steps

If NO novel axis-aligned species are found across ALL phases and ALL LUTs, then F1 is triggered and you must clearly document this as a null result.

Run the script and save all results. The script must exit with code 0.
