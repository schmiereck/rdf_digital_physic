INTER-PLANE COUPLING: Test whether controlled coupling between the [111] hex plane and inter-plane channels can produce 3D binding (bits spanning 2+ planes) while preserving glider stability.

CRITICAL: Read src/pre_registration.md first. Adhere to all falsification criteria. Per Section 5, this is an ANISOTROPIC 2.5D system — not isotropic 3D. Per Section 6, the coupling hypothesis is REFUTED if F4a, F4b, or F4c hold.

CONTEXT from sub-goal 252.2:
- F3 is TRIGGERED: Pure LGCA embedding is impossible (hex CA violates bit conservation)
- The hybrid engine (src/fcc_engine_embed.py) uses synchronous CA for in-plane channels + LGCA for inter-plane channels
- At alpha=0 (no coupling), the embedded glider survives perfectly on the [111] plane
- All inter-plane channels remain zero at alpha=0

COUPLING DESIGN:

Implement a deterministic coupling mechanism in the hybrid engine:

1. After computing the new center bit via hex rule, apply coupling:
   - For each inter-plane channel i (ch6-ch11), with probability of coupling controlled by alpha:
     If center_bit = 1 AND inter_plane_channel_i = 0 AND (specific condition based on alpha):
       Swap: center → 0, channel_i → 1
     If center_bit = 0 AND inter_plane_channel_i = 1 AND (specific condition based on alpha):
       Swap: center → 1, channel_i → 0

2. For DETERMINISTIC coupling (no floats in physics!), use alpha as an integer parameter controlling HOW MANY channels participate:
   - alpha=0: no channels participate (factorized, already tested)
   - alpha=1: only channel 6/9 pair participates (one pair of antiparallel channels)
   - alpha=2: channels 6/9 and 7/10 participate (two pairs)
   - alpha=3: all three pairs (6/9, 7/10, 8/11) participate

3. The coupling operation should be:
   After hex rule computes new center bit, for each active inter-plane pair:
   - If center=1 and outgoing channel=0: swap (center→0, channel→1) — bit "hops" to inter-plane
   - If center=0 and incoming channel=1: swap (center→1, channel→0) — bit "hops" from inter-plane
   
   Where "outgoing" = channels 6,7,8 (shift toward higher layer) and "incoming" = channels 9,10,11 (shift from lower layer, or equivalently the antiparallel of outgoing).
   
   Actually, since we want bits to potentially cross layer boundaries, the coupling should be:
   - Outgoing: if center=1, swap center↔ch_i for i in {6,7,8}[:alpha]
   - After streaming, incoming bits arrive from other layers in ch_i for i in {9,10,11}
   - Incoming: if ch_i=1 (bit arrived from another layer), swap center↔ch_i

   BUT this creates ambiguity: which channel do we swap with? We need a clear, deterministic rule.

   Simplest approach: SWAP center with the LOWEST-NUMBERED active inter-plane pair.
   - alpha=1: only check pair (ch6, ch9). After hex rule:
     - If center=1 and ch6=0: swap center↔ch6 (bit goes up)
     - Else if center=0 and ch9=1: swap center↔ch9 (bit comes from below)
   - alpha=2: also check pair (ch7, ch10) after pair (ch6, ch9)
   - alpha=3: also check pair (ch8, ch11)

IMPLEMENTATION:

Modify src/fcc_engine_embed.py to add the coupling logic to embed_step():
- Add alpha parameter (integer 0-3)
- Implement deterministic channel-pair swaps after the hex rule is applied
- The swaps must be DETERMINISTIC and INTEGER-BASED (no floats)

Then create src/test_interplane_coupling.py that:
1. Sweeps alpha from 0 to 3 (4 values)
2. For each alpha, runs 10 seed configurations × 300 steps:
   - Config 0: Standard L-tromino at layer 16 (single layer)
   - Config 1-3: L-tromino at layers 15, 17, 14 (offset layers)
   - Config 4-6: Two L-trominos at layers 15+17, 14+18, 16+14 (multi-layer seeds)
   - Config 7-9: L-tromino at layer 16 with 1-3 inter-plane bits set
3. For each run, track:
   - Whether center bits survive on the original layer
   - Whether center bits appear on OTHER layers (3D binding)
   - Bit counts per layer
   - Displacement on the original layer
4. Apply Single-Bit Decomposition Test to any configuration with bits on 2+ layers
5. Apply latency perturbation test (F4b): add a localized latency field and check if the glider remains coherent
6. Save results to archive/iter_252/results/coupling_test.json

FALSIFICATION:
- F4a: If multi-layer configurations are non-interacting composites (each bit independent) → REFUTED
- F4b: If coupled state disperses under latency perturbation → REFUTED  
- F4c: If no stable configuration survives >=300 steps for any alpha > 0 → REFUTED

Use existing code:
- src/fcc_engine_embed.py (modify embed_step to add coupling)
- src/test_embedded_glider.py (reference for patterns)
- src/evolution.py (hex CA utilities)

Keep all files under 250 lines. ASCII only. Run the coupling test and report key findings.