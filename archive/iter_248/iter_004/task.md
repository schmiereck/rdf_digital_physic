You are working on a digital physics research project on the 3D FCC lattice cellular automaton. A critical finding emerged: ALL "gliders" on the FCC lattice (including LUT-08) are NON-INTERACTING COMPOSITES of single-bit streaming particles. The bits never share a cell — each bit is independently streamed and collision-mapped.

Your task is to characterize the FUNDAMENTAL single-bit particle spectrum and determine whether any genuine multi-bit coherent gliders exist. Create and run `src/experiment_248_fundamental_spectrum.py`.

## Task 1: Weight-1 State Mapping Analysis

For the LUT-08 rule (from `archive/iter_224/results/glider_00_lut08_sub03.json`):
- Extract the LUT (4096-entry array)
- For each of the 12 channels (0..11), compute what the LUT maps the weight-1 state (1 << ch) to
- This gives the single-bit channel permutation: ch → lut[1 << ch] (then find which bit is set in the result)
- Build the permutation graph and find all cycles
- For each cycle, compute the velocity: average of SHIFTS[ch] for channels in the cycle, divided by cycle length gives the per-step velocity
- Report: each cycle's length (period), channels in the cycle, per-step velocity in grid coordinates, and Cartesian velocity (using BT matrix from src/glider_charge_analysis.py:make_BT())
- Also check: which cycles produce axis-aligned velocities (Cartesian velocity components are integers or half-integers)?

Also do the same analysis for the 3 additional O_h-symmetric LUTs (seeds 42, 123, 999), generated using the same infrastructure as in `src/experiment_248_axis_aligned_search.py`.

## Task 2: Weight-2 State Interaction Search

Check if any PAIR of bits at the SAME cell can form a genuine 2-bit coherent structure:
- For each weight-2 state (C(12,2) = 66 states):
  - Place this 2-bit state at the center of an L=32 grid
  - Simulate 32 steps
  - Track whether the 2 bits remain at the same cell (or within 1 cell of each other) at every step
  - If yes and bit count is conserved and extent ≤ 4: this is a genuine 2-bit coherent structure
- Do this for ALL 4 LUT rules
- Report any genuine 2-bit structures found

## Task 3: Weight-3 Single-Cell Interaction Search

For weight-3 states at a single cell (C(12,3) = 220 states):
- Same protocol as Task 2
- Check if 3 bits remain within 2 cells of each other
- Report any genuine 3-bit coherent structures

## Task 4: Cross-LUT Species Comparison

For each LUT, count the number of distinct single-bit species (distinct cycles in the weight-1 permutation). Compare across LUTs. Also check: do any weight-2 or weight-3 coherent structures exist that are NOT just composites of single-bit particles?

## Implementation Details

- Import from `src/engine_3d.py`: stream, collide, SHIFTS
- Import from `src/search_3d_gliders.py`: generate_symmetric_lut, get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, verify_lut
- Import from `src/glider_charge_analysis.py`: make_BT
- Import from `src/rigorous_glider_audit.py`: seed_grid, compute_com_circular, bounding_extent

For the weight-1 mapping: `lut[1 << ch]` gives the mapped state. To find which channel the bit moved to: `(lut[1 << ch] & (1 << k)) != 0` for each k, or use `bit_length() - 1` on the result (since it's weight-1 → weight-1 for a bit-conserving LUT).

For Tasks 2 and 3, use the sparse simulation approach (list of (l,r,c,ch) tuples) for efficiency, as in the search script.

## Output

Write `archive/iter_248/results/fundamental_spectrum.json` with:
```json
{
  "lut08_weight1_cycles": [
    {"cycle": [ch_list], "period": P, "velocity_grid": [...], "velocity_cart": [...], "axis_aligned": true/false}
  ],
  "sym_42_weight1_cycles": [...],
  "sym_123_weight1_cycles": [...],
  "sym_999_weight1_cycles": [...],
  "weight2_coherent_structures": [...],
  "weight3_coherent_structures": [...],
  "genuine_multibit_gliders_found": true/false,
  "f1_triggered": true/false,
  "verdict": "..."
}
```

Write `archive/iter_248/results/fundamental_spectrum_report.md` with comprehensive analysis.

## Critical Context

The Phase 7.1 falsification criterion states: "Refuted as 'taxonomy' if all discovered species are O_h-orbit-equivalent to one or two underlying patterns."

Since O_h acts transitively on the 12 NN channels, ALL single-bit particles are in the SAME O_h orbit. If the only genuine species are single-bit streaming particles, then the taxonomy is MONOSPECIFIC — F1 is triggered.

However, if genuine multi-bit coherent structures exist (where bits share cells and interact), they could represent genuinely new species.

Be rigorous and skeptical. Check everything. The previous "novel species" were all false positives.

Keep the script under 250 lines. Run it and save all results.
