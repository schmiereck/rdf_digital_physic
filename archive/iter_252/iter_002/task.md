3D FCC EMBEDDING: Build and test the embedding of the 2D hex glider rule into a [111] hex plane of the 3D FCC lattice.

CRITICAL: Read src/pre_registration.md before starting. This is a CODE-VERIFICATION AND ALIGNMENT TEST per Section 4 of the pre-registration. The factorized embedding at α=0 is GUARANTEED BY CONSTRUCTION if it works. Do NOT use promotional language if the glider survives — classify it as a 2D glider on a 3D coordinate projection.

ARCHITECTURAL ANALYSIS (MANDATORY FIRST STEP):

Before writing any code, analyze the following fundamental incompatibility:

The 2D hex CA (champion_rule_perfect) is a SYNCHRONOUS CA:
- 7-bit neighborhood → 1-bit center output
- NOT bit-conserving at the local level (3→4 bits in the glider)
- NOT a bijective mapping on the 7-bit local state space
- No streaming — each cell reads neighbors directly

The 3D FCC LGCA (fcc_engine_13ch.py) is a LATTICE GAS CA:
- 13-bit local state → 13-bit local state via LUT
- STRICTLY bit-conserving (Hamming weight preserved)
- STRICTLY bijective (reversible)
- Stream + Collide two-phase update

The hex CA's binding mechanism (cooperative survival) requires weight-1→0 and weight-0→1 transitions, which VIOLATE bit conservation. Therefore, a factorized LUT that is simultaneously bijective, bit-conserving, AND compatible with the hex rule may be IMPOSSIBLE. This would trigger falsification criterion F3.

APPROACH:

1. Build src/fcc_engine_embed.py — a HYBRID engine that:
   a. Uses synchronous CA update for in-plane channels (directly reading neighbors' center bits)
   b. Uses standard LGCA stream+collide for inter-plane channels (ch6-11)
   c. The center channel (ch12) is the cell's binary state
   d. The 6 in-plane channels (ch0-5) are VIRTUAL — they're computed as the center bit of the corresponding neighbor (no streaming needed for in-plane communication)
   
   Channel mapping for [111] hex plane (layer l of the FCC lattice):
   - ch12 = center bit (cell state)
   - ch0 (shift (0,1,0)) = hex E direction
   - ch1 (shift (0,-1,0)) = hex W direction  
   - ch2 (shift (0,0,1)) = hex NE direction
   - ch3 (shift (0,0,-1)) = hex SW direction
   - ch4 (shift (0,1,-1)) = hex SE direction
   - ch5 (shift (0,-1,1)) = hex NW direction
   
   After streaming in the LGCA, the in-plane channels at cell X contain:
   - ch0 = bit from X's W neighbor (antiparallel of E)
   - ch1 = bit from X's E neighbor (antiparallel of W)
   - ch2 = bit from X's SW neighbor (antiparallel of NE)
   - ch3 = bit from X's NE neighbor (antiparallel of SW)
   - ch4 = bit from X's NW neighbor (antiparallel of SE)
   - ch5 = bit from X's SE neighbor (antiparallel of NW)
   
   So hex_state = ch12*64 + ch1*32 + ch5*16 + ch2*8 + ch0*4 + ch4*2 + ch3

2. Build src/test_embedded_glider.py that:
   a. Loads champion_rule_perfect.json from archive/iter_222/results/
   b. Creates a 32×32×32 grid with the L-tromino seed at center of layer 16
   c. Runs the hybrid engine for 300 steps
   d. Tracks unwrapped COM and bit count
   e. Runs the Single-Bit Decomposition Test (each seed bit alone for 300 steps)
   f. Runs a positive control (2D hex standalone) and negative control (12-ch O_h LUT-08)
   g. Saves results to archive/iter_252/results/embed_test.json

3. F3 ANALYSIS: Attempt to build a pure LGCA factorized LUT (13-bit bijection, bit-conserving) that is compatible with the hex rule. Document whether this is possible or F3 is triggered.

   To test F3: Try constructing a 13-bit LUT where:
   - For all 128 states with inter-plane channels=0: output ch12 = hex_rule(hex_state), output ch0-5 = ch12_out (broadcast)
   - Check if this is a bijection on {0..8191} → likely NOT because many different 13-bit inputs with the same hex bits map to the same output
   - If not a bijection, try alternative in-plane output mappings
   - Document all attempts and whether F3 is triggered

4. Report format (save to archive/iter_252/results/embed_report.json):
   - f3_triggered: bool (whether a bijective, bit-conserving, hex-compatible LUT is possible)
   - embedded_glider_survives: bool (hybrid engine)
   - embedded_glider_speed: float
   - embedded_glider_bit_counts: list
   - decomposition_test_passed: bool (single bits annihilate in hybrid engine)
   - positive_control_matches: bool (2D standalone matches hybrid)
   - architecture_notes: string (explanation of hybrid vs LGCA)

Use existing code:
- src/evolution.py: rule_dict_to_lut(), step_grid()
- src/fcc_engine_13ch.py: pack_13, unpack_13, stream_13, SHIFTS_13
- src/engine_3d.py: stream, collide, pack, unpack, SHIFTS
- archive/iter_222/results/champion_rule_perfect.json: the hex rule
- archive/iter_252/results/hex_mechanism.json: mechanism analysis

The hybrid engine should be implemented as functions:
- embed_step(grid_3d, hex_lut, alpha=0.0) → grid_3d
  where grid_3d has shape (L, H, W, 13) and hex_lut is the 128-entry hex CA LUT

IMPORTANT: Be precise about language. The embedded glider surviving is "consistent with the construction" (not "emergence" or "discovery"). Use "aligned with" not "confirms".