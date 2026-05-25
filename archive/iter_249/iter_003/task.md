# Phase 249 Sub-Goal C: Check 2D Hex Glider Coherence

## Context
In iter_248, we proved that ALL 3D FCC "gliders" are non-interacting composites of single-bit particles. The root cause was that the O_h-symmetric LUT maps weight-2 states as independent superposition of weight-1 transpositions.

The 2D hex lattice has a celebrated v=0.469c sub-light glider (discovered in iter_222, rule in `champion_rule_perfect.json`). We need to check whether this glider is also a non-interacting composite, or whether it is a genuine multi-bit coherent particle.

This test is HIGH PRIORITY per the Research Manager: if the hex glider also decomposes, the monospecific spectrum is a general feature of additive LGCA constructions. If it does NOT decompose, the 2D hex lattice has a fundamental advantage that should be understood.

## Task: Apply Single-Bit Decomposition Test to 2D Hex Glider

### Step 1: Load the hex glider rule and structure
Read `champion_rule_perfect.json` (search for it in the project: `src/champion_rule_perfect.json` or `archive/iter_222/`). The 2D hex engine is in `src/simulate_hex.py` or similar files. Also check `src/run_evolution_exp_221_perfect.py` or `src/run_evolution_exp_222.py` for the hex simulation code.

### Step 2: Identify the hex glider's bit structure
The v=0.469c glider has multiple bits on the hex grid. Determine:
- How many bits does it have?
- What is its spatial extent?
- What is its period?

### Step 3: Run each bit independently
For each bit position in the glider:
1. Create a simulation with ONLY that single bit set (all others = 0)
2. Run for the glider's period (or 100 steps)
3. Track the trajectory of that single bit

### Step 4: Compare single-bit trajectories to full glider trajectory
If the full glider's trajectory is the superposition of all individual bit trajectories (bits move independently and never interact), then the glider is a NON-INTERACTING COMPOSITE — the same verdict as LUT-08 in 3D.

If the bits interact (their combined trajectory differs from the superposition of individual trajectories, or bits co-locate at cells during propagation), then the hex glider is GENUINE.

### Step 5: Check for multi-bit cells
During the full glider propagation, check if any cell ever has more than one bit. If yes, the rule is processing multi-bit states non-trivially — this is a necessary (but not sufficient) condition for genuine coherence.

### Step 6: Save results
Save to `archive/iter_249/results/hex_coherence_result.json`:
- Number of bits in glider
- Period of glider
- Each single-bit trajectory
- Full glider trajectory
- Verdict: GENUINE_GLIDER or NON_INTERACTING_COMPOSITE
- Evidence: multi-bit cell count, trajectory comparison

## Key Considerations
- The 2D hex rule operates differently from the 3D FCC LGCA. In the hex CA, the rule is a synchronous cellular automaton (not a streaming-collision LGCA). Each cell looks at its 7-cell neighborhood (center + 6 neighbors) and updates its state.
- The "single-bit decomposition test" for a synchronous CA means: run the full glider for N steps, then run each individual bit of the initial glider configuration independently (with the rest of the grid empty) for N steps, and compare.
- If running a single bit produces a stable propagating pattern (like a single-bit glider), the multi-bit glider is a composite.
- If running a single bit produces chaos or annihilation (the bit needs its neighbors to survive), the glider is genuine.

## Search Path for Hex Code
The hex simulation code might be in any of these files:
- `src/simulate_hex.py`
- `src/run_evolution_exp_222.py`
- `src/run_evolution_exp_221_perfect.py`
- `src/run_evolution_exp_221.py`

The champion rule might be in:
- `src/champion_rule_perfect.json`
- `archive/iter_222/results/`

Use `grep -r "champion_rule_perfect" src/` or similar to find the exact path.

## Success Criterion
A definitive verdict on whether the 2D hex v=0.469c glider is genuine or a non-interacting composite, with supporting evidence.
