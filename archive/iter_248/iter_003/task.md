You are working on a digital physics research project. A previous search (src/experiment_248_axis_aligned_search.py) claimed to find 10 "novel species" of gliders on the 3D FCC lattice. However, ALL of these species have canonical forms where every bit is in the SAME channel (channel 0), and most have period 1 with v=1c velocity. This is extremely suspicious — these are likely NON-INTERACTING COMPOSITES of single-bit streaming particles, not genuine coherent gliders.

Your task is to rigorously verify or refute these "novel species" by implementing and running three critical tests:

## Test 1: Single-Bit Decomposition Test
For each "novel species" particle definition:
- Simulate EACH individual bit separately (1 bit at a time, in isolation) under the same LUT
- If every individual bit moves with the same velocity as the composite, the "species" is a NON-INTERACTING COMPOSITE, not a genuine glider
- A genuine glider must have at least one bit whose solo behavior differs from its behavior in the composite

## Test 2: Collision Interaction Test  
For each "novel species" particle:
- During a 32-step simulation, at each step check: are there any spatial cells that contain MORE THAN ONE bit?
- Count the number of multi-bit cells across all steps
- A genuine glider must have bits that collide (occupy the same cell) at least once per period
- If multi_bit_cell_count == 0 for the entire simulation, the "species" is a NON-INTERACTING COMPOSITE

## Test 3: Bit-Removal Stability Test
For each "novel species" particle:
- Remove each bit one at a time (create k-1 bit sub-particles)
- Simulate each sub-particle for 32 steps
- For a genuine glider, removing ANY bit should destabilize the remaining pattern (change velocity, break bit conservation, or expand beyond extent 6)
- If removing any bit leaves the remaining pattern still moving with the same velocity, the original was a non-interacting composite

## Implementation Details

Create `src/experiment_248_verification.py`. Use the same infrastructure:
- `src/engine_3d.py` for stream, collide, SHIFTS
- `src/rigorous_glider_audit.py` for build_oh_transforms, oh_canonical, seed_grid, compute_com_circular, bounding_extent
- `src/search_3d_gliders.py` for generate_symmetric_lut, get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers, verify_lut
- `src/glider_charge_analysis.py` for make_BT

Load the LUTs:
1. LUT-08 from `archive/iter_224/results/glider_00_lut08_sub03.json`
2. Generate sym_42, sym_123, sym_999 using generate_symmetric_lut with the same setup as the search script

Use the particle definitions from the search_results.json:
- Load `archive/iter_248/results/search_results.json`
- The novel_species list has "canon" field (canonical particle form) and "lut" field
- Also load the "stable_moving_candidates" list — for each, you'll need to re-derive the original particle from the search. Since the search only saved cd16 and bits, you should re-run the search script or load particle definitions from a separate file.

Actually, there's a problem: the search_results.json only has canonical forms for novel species but not the original particles for all 32 stable_moving candidates. You need to reconstruct the particles. 

The simplest approach: load the novel_species list from search_results.json. Each novel species has a "canon" field which IS the particle definition (the O_h canonical form). Test each of these canonical particles under the appropriate LUT.

Also include the LUT-08 reference particle as a positive control — it should pass all three tests (genuine coherent glider).

## Output

Write `archive/iter_248/results/verification_results.json` with:
```json
{
  "species_tested": N,
  "non_interacting_composites": M,
  "genuine_gliders": K,
  "results_per_species": [
    {
      "species_id": i,
      "lut": "lut_name",
      "test1_single_bit_velocity_matches": true/false,
      "test2_multi_bit_cell_count": N,
      "test3_bit_removal_destabilizes": true/false,
      "verdict": "GENUINE" / "NON_INTERACTING_COMPOSITE"
    }
  ],
  "lut08_reference_passes_all_tests": true
}
```

Write `archive/iter_248/results/verification_report.md` summarizing findings.

## Critical Methodological Notes
- A "glider" whose bits never occupy the same cell during the simulation is NOT a glider — it's a set of independent streaming particles
- The LUT-08 reference glider (4-bit, period 2, velocity [0.5, 0, 1]) MUST pass all tests as a positive control. If it doesn't, your tests are wrong.
- A period-1 "glider" with v=1c is almost certainly just a single bit streaming. The LUT's identity (or equivariant permutation) mapping on weight-1 states means individual bits just propagate. Test this explicitly.
- Be skeptical. This project has a history of false positives from coordinate artifacts and non-interacting composites.

Keep the script under 200 lines. Run it and save results.
