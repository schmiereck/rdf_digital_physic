## Task: Phase 7.3 — Antiparticle CPT Experiment

You are executing a pre-registered scientific experiment for Phase 7.3 (Antiparticles & CPT Symmetries) of the Bit-Grid Universe project. 

### Step 1: Update pre-registration with precise CPT definitions

Edit `src/pre_registration.md` to add a new section "## CPT Operator Definitions" with the following mathematical precision:

**Parity (P):** Spatial reflection in Cartesian space. Specifically, we invert the x-coordinate: (x,y,z) → (−x,y,z). On the lattice, this is implemented by converting (l,r,c) → Cartesian via BT_inv, negating x, then converting back via BT. This produces the enantiomeric glider with opposite chirality (χ → −χ). The P operator does NOT change the channel assignments of the glider bits.

**Charge Conjugation (C):** On this lattice, "charge" is chirality (the signed 4-volume of the glider's bit positions in Cartesian space). C maps a particle to its enantiomer, which is identical to P on this lattice because chirality is the only discrete charge. C is NOT bitwise inversion (0↔1); bitwise inversion would destroy the glider structure and is not a symmetry of the rule.

**Time Reversal (T):** Running the CA backward: streaming in reverse and applying the inverse LUT. The T-reversed glider propagates in the opposite direction under the inverse rule.

**CPT = C·P·T:** On our lattice, since C≡P, CPT ≡ P²·T = T (since P²=identity for a single reflection). The CPT-conjugate of the LUT-08 glider requires the inverse rule to propagate stably, and is NOT the appropriate object for forward-rule collision experiments.

**For forward-rule collision experiments, the "antiparticle" is defined as the P-reflected (enantiomeric) glider, which is stable under the forward rule by O_h symmetry.**

### Step 2: Write the compact experiment script

Write `src/phase7_3_cpt_experiment.py` — a compact script (under 150 lines if possible) that performs the following:

1. **Load data:** Read LUT and particle from `archive/iter_224/results/glider_00_lut08_sub03.json`
2. **Build O_h transforms:** Use `build_oh_transforms()` from `src/rigorous_glider_audit.py`
3. **Construct particles:**
   - pA = original LUT-08 glider (chirality χ ≈ −4/+2)
   - pB = P-reflected glider (use `reflect()` from `src/glider_charge_analysis.py`) — this is the "antiparticle" with chirality −χ
   - pC = same-chirality reversed-velocity glider: find a proper O_h rotation (det=+1) that reverses pA's velocity direction. To do this: iterate over the 48 O_h transforms, apply each to pA, simulate 1 step forward, compute displacement, and find the one whose displacement is approximately opposite to pA's. This gives a same-chirality glider moving toward pA.
4. **Verify solo stability (CONTROL A — constructional):** Run pB alone for 80 steps under forward LUT-08 rule. Check bit count = 4 at every step. (Also pC if different from pA.)
5. **Opposite-chirality collisions (EXPERIMENT):** 5 configurations with different impact parameters. Place pA at center approaching, pB offset by (0,0,0), (0,1,0), (0,2,0), (0,0,1), (0,1,1) lattice units perpendicular to collision axis. Run 100 steps each.
6. **Same-chirality collisions (CONTROL B):** Same 5 impact parameters but using pC instead of pB. Run 100 steps each.
7. **O_h covariance test:** Take the first (head-on) opposite-chirality config. Rotate the entire setup (both particles) through one non-trivial O_h proper rotation. Re-run 100 steps. Compare outcome.
8. **Classify outcomes:** For each collision run, classify as:
   - "Elastic" if exactly 2 four-bit clusters emerge (2 intact gliders)
   - "Annihilation" if no four-bit clusters emerge and all bits are isolated single-bit propagators
   - "Partial" if 1 four-bit cluster + debris
   - "Chaotic" if 0 four-bit clusters + debris
   Also measure: total bit count, number of 4-bit clusters, number of isolated bits.
9. **Print results table and save JSON** to `archive/iter_245/results/cpt_experiment_results.json`

Key implementation notes:
- Grid size: L=32 (sufficient per iter_232 precedent)
- Import from `src/engine_3d.py`: SHIFTS, stream, collide
- Import from `src/glider_charge_analysis.py`: make_BT, reflect (or re-implement inline — these are simple 5-line functions)
- Import from `src/rigorous_glider_audit.py`: build_oh_transforms, seed_grid, compute_com_circular, clusters (for cluster detection)
- DO NOT import the full `search_3d_gliders.py` — it's large and slow. Only import what you need.
- Keep the script COMPACT. No verbose logging. Minimal print statements.
- Use `src/glider_collision_charge_analysis.py` as a reference for how to set up collisions (the place/seed functions, cluster detection, chirality computation).

### Step 3: Run the script

Execute: `cd /home/user && python src/phase7_3_cpt_experiment.py`

Save the output and any results JSON.

### Step 4: Write the milestone report

Write `archive/iter_245/results/RESEARCH-RESULT-245.md` following the required structure:
- Pre-Declared Hypothesis & Falsification (from pre_registration.md)
- Protocol (what was actually done)
- Observations (raw results)
- Verdict (PASS/FAIL against each falsification criterion)
- Construction-vs-Empirical Note
- Limitations

### Important constraints
- The script MUST be under 150 lines if possible (manager's token-budget directive)
- Do NOT dump massive state histories. Only save summary statistics.
- Read `src/pre_registration.md` first and adhere to the falsification criteria there.
- The P-reflected glider stability under forward rule is CONSTRUCTIONAL (not an empirical finding). Frame it as such.
- The only genuine empirical inquiry is the collision dynamics.