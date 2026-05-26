You are executing Sub-Goal 250.1 of Phase 250: **2D Hex Decomposition Check** — the ABSOLUTE PRIORITY for this iteration.

## Context
In Phase 248, we discovered that the 3D FCC "4-bit glider" LUT-08 is actually a non-interacting composite of 4 independent single-bit particles. The Research Manager mandates that BEFORE building complex 3D non-additive LUT infrastructure, we must determine whether the 2D hex v=0.469c sub-light glider from iter_222 (`champion_rule_perfect.json`) suffers from the same problem.

## Task
1. **First, update `src/pre_registration.md`** to reflect the Research Manager's directive: **Remove the clause about relaxing O_h symmetry** (the line "If O_h-symmetric variants cannot be constructed, relax O_h symmetry and construct arbitrary non-additive weight-2 permutations" must be removed and replaced with a statement that O_h symmetry is a non-negotiable physical constraint). The pre-registration must also state that the 2D hex check is the top priority.

2. **Build and run the 2D hex decomposition test.** There is already a skeleton in `src/hex_coherence_test.py` but it may have issues. Create a clean, rigorous version at `src/experiment_250_hex_decomposition.py` that:

   a. Loads the champion rule from `archive/iter_222/results/champion_rule_perfect.json` using `src/evolution.py`'s `rule_dict_to_lut` and `step_grid` functions.

   b. Runs the FULL L-tromino glider (3-bit seed at cells [(63,63), (64,63), (64,64)]) for 500 steps on a 128×128 grid, tracking:
      - Bit count at each step (bit conservation check)
      - Unwrapped center-of-mass trajectory
      - Active cell positions at each step

   c. For EACH of the 3 seed bits individually: run each single bit ALONE for 500 steps. Record:
      - Does the single bit survive? (final bit count > 0)
      - If it survives, what is its velocity?
      - If it annihilates, at what step?

   d. For EACH of the 3 possible 2-bit subsets: run each pair for 500 steps. Record:
      - Does the pair survive?
      - If it behaves differently from the two individual bits combined, that's evidence of interaction.

   e. **Critical Test — Superposition Comparison**: For each timestep, compare the full 3-bit glider grid with the logical OR of the three individual 1-bit grids. If they differ at any step, that means bits in the full glider interact via their neighborhoods (they are close enough to influence each other's rule application). Count the number of mismatching timesteps.

   f. **Binding Energy Verdict**: 
      - If any individual bit ANNILIHATES when run alone but survives in the full glider → binding energy > 0, GENUINE GLIDER
      - If all individual bits survive alone with the same velocity as the full glider AND the full glider matches the OR superposition → non-interacting composite, binding energy = 0
      - If bits survive alone but with DIFFERENT velocity/trajectory than in the full glider → binding energy > 0, genuine coherence
      - If the full glider differs from OR superposition at some steps → interaction exists (need to determine if it's constructive binding or transient perturbation)

3. **Run the experiment** and report all findings. Save results to `archive/iter_250/results/hex_decomposition.json`.

4. **If the 2D hex glider IS genuine**: Analyze the precise mathematical mechanism that allows 2D hexagonal single-cell collisions to support binding where the 3D FCC single-cell collisions failed. What structural property of the 7-neighborhood hex rule enables multi-bit coherence?

5. **If the 2D hex glider is ALSO a non-interacting composite**: Document this as a foundational null result. This would confirm monospecificity is a general LGCA/synchronous-CA property, not just an FCC artifact.

## Pre-Registration Compliance
Read `src/pre_registration.md` (after you update it) and strictly adhere to the falsification criteria. Use restrained, falsifiable language in all reports. Do NOT use promotional vocabulary ("breakthrough", "proves", "perfectly"). Required terms: "consistent with", "evidence for", "does not refute", "refuted by".

## Key Files
- `src/evolution.py`: Contains `rule_dict_to_lut()`, `step_grid()`, `make_ltromino_grid()`, `LTROMINO_CELLS`
- `archive/iter_222/results/champion_rule_perfect.json`: The champion rule
- `src/hex_coherence_test.py`: Reference (existing skeleton, may have bugs)
- `src/pre_registration.md`: Must be updated first

## Success Criterion
The sub-goal succeeds when a definitive verdict is reached: the 2D hex glider is either (a) genuinely bound with binding energy > 0, or (b) a non-interacting composite, with quantitative evidence supporting the verdict.