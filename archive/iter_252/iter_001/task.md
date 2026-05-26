MECHANISM EXTRACTION: Analyze the 2D hex v=0.469c glider to understand its cooperative survival binding mechanism.

CRITICAL: Read src/pre_registration.md before starting. Adhere to all pre-registered criteria and falsification mandates.

TASK:
1. Load champion_rule_perfect.json from archive/iter_222/results/ (the proven v=0.469c glider rule)
2. Trace the glider for 500 steps from the L-tromino seed [(63,63), (64,63), (64,64)] on a 128×128 grid
3. Identify and document:
   a. The glider period (how many steps for one full cycle)
   b. The spatial extent (bounding box over one period)
   c. The channel/state transition sequence: at each step, what are the neighborhood states encountered by active cells?
   d. The COOPERATIVE SURVIVAL SIGNATURE: which LUT entries are responsible for binding?
      - Run the OR-superposition test (compare full glider with OR of 3 single-bit runs) and list ALL steps where mismatches occur
      - For each mismatching step, identify which neighborhood state(s) in the full glider have different LUT output than the superposition
   e. Which specific rule mappings enable weight-1→0 transitions (cooperative annihilation of isolated bits)?
   f. Which specific rule mappings enable weight-0→1 transitions (cooperative creation from multi-bit interaction)?

4. DOCUMENT the mechanism as a "survival recipe" — the minimal set of LUT entries that must be preserved for the glider to work when embedded into 3D.

Create src/analyze_hex_mechanism.py that performs this analysis and saves results to archive/iter_252/results/hex_mechanism.json.

Key existing code to use:
- src/evolution.py: rule_dict_to_lut(), step_grid(), LTROMINO_CELLS, GRID_SIZE=128
- src/experiment_250_hex_decomposition.py: simulate() function with unwrapped COM tracking
- src/hex_coherence_test.py: superposition comparison code

The 2D hex CA is a synchronous cellular automaton on a hexagonal grid where:
- Each cell state is binary (0 or 1)
- The 7-bit neighborhood is: center(1), E(1), SE(1), SW(1), W(1), NW(1), NE(1)
- State encoding: state = center*64 + E*32 + SE*16 + SW*8 + W*4 + NW*2 + NE
- The LUT maps 128 states → center bit of output (0 or 1)

This is NOT an LGCA (no channels/streaming). It's a standard synchronous CA on a hex grid.

The binding mechanism is "cooperative survival" — bits survive only when their neighbors overlap, creating/destroying bits in a way that individual bits cannot do alone.

IMPORTANT: Do NOT use promotional language. Report findings as "consistent with" or "evidence for", not "proves" or "demonstrates".