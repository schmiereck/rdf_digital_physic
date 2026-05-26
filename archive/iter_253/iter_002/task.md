You are executing Step 2-5 of the pre-registered experiment for iteration 253. READ src/pre_registration.md FIRST and strictly adhere to all falsification criteria F1-F6.

## Context
The 3D synchronous CA engine on FCC lattice has been built and validated at src/synchronous_ca_fcc.py. It provides:
- `step_ca(grid, B, S)` — one synchronous totalistic B/S update step
- `simulate(grid, B, S, steps)` — full simulation with COM, bit_count, bounding_box tracking
- `trig_com(grid, L)` — toroidal center-of-mass
- `unwrap_com(prev, raw, L)` — unwrapped COM for displacement tracking
- `bounding_extent(grid, L)` — bounding box size
- `format_rule(B, S)` — rule string
- `lambda_param(B, S)` — Langton's lambda for 13-neighbor system
- `validate_engine()` — validation (already passed all tests)

The 12 FCC neighbor offsets are: (0,1,0), (0,-1,0), (0,0,1), (0,0,-1), (0,1,-1), (0,-1,1), (1,1,1), (1,1,0), (1,0,1), (-1,-1,-1), (-1,-1,0), (-1,0,-1)

## Task: Execute Full Search Pipeline

### Step 2 — Designed Rule Sweep
Create src/totalistic_rule_search.py. Generate and test B/S rules on the FCC lattice:

**Rule Generation Strategy:**
- Target the phase boundary between order and chaos (Langton's lambda ≈ 0.25-0.45 for 13-neighbor system)
- Key constraint from SRM: 0 ∉ B (no vacuum fluctuations) and 0 ∉ S (cooperative survival — isolated bits die)
- B ⊆ {1,...,11}, S ⊆ {1,...,12} (NOT containing 0)
- Generate ~200 rules:
  - 100 sparse rules (|B| ≤ 2, |S| ≤ 3) at various lambda values
  - 50 medium rules (|B| = 2-3, |S| = 3-5)  
  - 50 rules guided by lambda targeting (pick B,S giving lambda in [0.25, 0.45])

**Seed Design:**
- Single bits at center: (20,20,20) — test for cooperative survival
- Bit pairs: 2 adjacent bits (6 axis-aligned pairs + 6 diagonal pairs = 12)
- L-tromino analogs: 3 adjacent bits forming an L-shape (8 variants along different axes)
- Small random clusters: 3-6 bits in a compact arrangement (20 variants)
- Total: ~46 seeds per rule

**Simulation Parameters:**
- Grid: 40×40×40 (large enough for glider travel without boundary effects)
- Steps: 500 per rule×seed
- Track: bit_count, unwrapped_com, bounding_extent at each step

**Filtering (apply ALL falsification criteria):**
- Survival: bit_count > 0 at step 300
- Displacement: net_displacement ≥ 5 lattice units over 300+ steps
- Bounding box: bounding_extent ≤ 10 cells after step 100 (F6: debris cloud)
- Bloom check: bit_count ≤ 4× initial_seed_weight after step 100 (F5: bloomer)
- Cooperative survival: single-bit seeds must die within ≤50 steps (F2)

### Step 3 — Evolutionary GA (if Step 2 yields < 5 candidates)
Create src/totalistic_ga.py. If the designed sweep doesn't find candidates:

**GA Parameters:**
- Genome: 26-bit (bits 0-10 = B set for counts 1-11, bits 11-23 = S set for counts 1-12, bits 24-25 unused)
  - ENFORCE: 0 ∉ B and 0 ∉ S by construction
- Population: 200 rules
- Generations: 30
- Fitness function (multi-objective, exploit-resistant):
  - survival_score = min(survival_steps / 300, 1.0)  (survive at least 300 steps)
  - displacement_score = min(net_displacement / 10, 1.0)  (need real motion)
  - compact_score = 1.0 if max_bounding_box ≤ 10 else 0.0  (F6)
  - no_bloom_score = 1.0 if max_bit_ratio ≤ 4.0 else 0.0  (F5)
  - fitness = survival_score * displacement_score * compact_score * no_bloom_score
- Evaluation: 5 seeds per rule (L-tromino analogs, bit pairs, small clusters)
- Take mean fitness across seeds
- Selection: tournament (size 3)
- Crossover: uniform crossover on 26-bit genome, then enforce constraints
- Mutation: bit-flip with p=0.1 per bit
- Elitism: top 5 survive unchanged
- Track total rules evaluated to hit ≥10,000 total (sweep + GA)

### Step 4 — Coherence Testing (for any candidates passing the sweep/GA filters)
Create src/glider_coherence_test.py. For each candidate rule+seed passing filters:

1. **Single-Bit Decomposition Test (F2):** Run each constituent bit of the seed in isolation. If ANY single bit survives ≥50 steps, the candidate is a non-interacting composite → FAIL.
2. **O_h Covariance Test (F3):** Apply all 48 O_h rotations to the seed. The O_h group on the FCC lattice permutes the 12 neighbor channels. Use the transforms from src/rigorous_glider_audit.py (build_oh_transforms()). Rotate each bit's coordinates by the O_h rotation matrix M_g, and verify the rotated seed also produces a surviving, propagating pattern. If ANY rotation kills the pattern → FAIL.
   - For totalistic rules, the RULE is O_h-equivariant by construction. The test is whether the SEED survives under rotation (i.e., the glider isn't exploiting a specific axis).
3. **Bloom Re-check (F5):** Verify bit_count never exceeds 4× initial at step 100+.
4. **Debris Re-check (F6):** Verify bounding_extent ≤ 10 at step 100+.
5. **Full 300-step run:** Verify survival ≥ 300 steps with displacement ≥ 5.

### Step 5 — Documentation
Write results to archive/iter_253/results/:
- `sweep_results.csv`: columns = rule_str, seed_id, survival, displacement, max_bit_ratio, max_bounding_box, verdict
- `ga_results.csv` (if GA ran): columns = gen, rule_str, mean_fitness, best_fitness
- `coherence_results.csv`: columns = rule_str, seed_id, decomposition_pass, oh_covariance_pass, bloom_pass, debris_pass, full_pass
- `phase_diagram.csv`: aggregate statistics per rule lambda value — fraction of seeds surviving, mean displacement, etc.
- `summary.json`: overall verdict, total rules tested, candidates found, candidates passing coherence

If NO candidates pass all coherence tests, this is a FIRST-CLASS NULL RESULT. Document the totalistic phase diagram on the FCC lattice — what lambda ranges produce survival, what produce explosion, what produce immediate death. This characterization is scientifically valuable regardless of outcome.

CRITICAL: Read src/pre_registration.md and strictly follow F1-F6. Every candidate must pass ALL criteria. Report negative results honestly.