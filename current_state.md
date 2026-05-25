# Current Research State
Phase: Phase 7.1 — Glider Taxonomy (F1 TRIGGERED: Monospecific)

## Goal
Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid.

## Confirmed (New in Phase 248)
- **LUT-08 is a non-interacting composite (iter_248, 248.3):** The "4-bit glider" is 4 independent copies of the [5,6] single-bit period-2 particle. Each bit individually achieves velocity [0.5, 0, 1] in isolation. Bits never share a cell during propagation.
- **ALL "novel species" from active search are non-interacting composites (iter_248, 248.2+248.3):** 10 species with distinct O_h canonical forms were found across 50,468 candidates, but all fail 3 coherence tests (single-bit decomposition, collision interaction, bit-removal stability).
- **Fundamental single-bit spectrum under LUT-08 (iter_248, 248.4):** 6 period-2 cycles with velocities: [0,3]→(0,0.5,-0.5), [1,2]→(0,-0.5,0.5), [4,7]→(0.5,1,-0.5), [5,6]→(0.5,0,1), [8,11]→(0,0,0) stationary, [9,10]→(-1,-1,-0.5). All axis-aligned.
- **LUT-08 weight-1 mapping is 6 disjoint period-2 transpositions (iter_248, 248.4):** ch0↔ch3, ch1↔ch2, ch4↔ch7, ch5↔ch6, ch8↔ch11, ch9↔ch10. The [8,11] cycle is antipodal → stationary oscillator.
- **sym_42/sym_123 have identity weight-1 mapping (iter_248, 248.4):** 12 period-1 v=1c single-bit species.
- **sym_999 has same weight-1 mapping as LUT-08 (iter_248, 248.4):** Same 6 period-2 cycles.
- **No genuine multi-bit coherent gliders exist (iter_248, 248.4):** Weight-2 "structures" are paired single-bit particles that stay close but never share a cell. Weight-3 structures: 0 across all LUTs.
- **iter_241 was a smoke test (iter_248, 248.1):** Only 100 seeds tested under 1 LUT, 0 novel survivors. Not a valid taxonomy search.

## Confirmed (Prior, Recontextualized)
- **2D hex v=0.469c sub-light glider (iter_222):** Still valid as a genuine coherent glider on the 2D hex lattice (different lattice, different mechanism).
- **3D FCC CA engine with 12-channel cuboctahedron (iter_224):** Engine is correct; the "4 stable gliders" found are actually composites of single-bit particles.
- **Gravitational time dilation via computational latency (iter_224):** Mechanism still valid (latency coupling), but the "mass packets" are composites.
- **Collision dynamics of LUT-08 composites (iter_245-247):** Real phenomena at the weight-≥2 level during spatial overlap, but not properties of a genuine multi-bit glider.
- **Chirality Z2 enantiomorphism (iter_242):** A property of the [5,6] cycle's channel permutation, not of a genuine multi-bit structure.
- **Phase 7.4 pair production refuted (iter_247):** Confirmed — single-bit fundamental particles cannot produce new species from collisions.

## Refuted
- **LUT-08 as genuine 4-bit coherent glider (iter_248, 248.3):** REFUTED. Non-interacting composite of 4 independent [5,6] single-bit particles.
- **Phase 7.1 hypothesis: particle zoo has genuine diversity (iter_248):** REFUTED (F1 triggered). All species are composites of single-bit streaming particles. Taxonomy is monospecific at the fundamental level.
- **"Novel species" from active search are genuinely new (iter_248, 248.3):** REFUTED. All are non-interacting composites.

## Best Result
- **Complete fundamental single-bit particle spectrum (iter_248, 248.4):** Under LUT-08: 6 period-2 species including 5 moving (different velocities) and 1 stationary oscillator. This is the actual "particle zoo."
- **Comprehensive active search with 50,468 candidates (iter_248, 248.2):** Largest systematic glider search on the FCC lattice to date.
- **Three-test coherence verification protocol (iter_248, 248.3):** Establishes methodological standard for distinguishing genuine gliders from non-interacting composites.

## In Progress / Decision Required
- **LUT construction redesign:** Can non-O_h-symmetric or differently-constructed LUTs produce genuine multi-bit coherent gliders?
- **Phase 8 direction:** Should anchoring to measurable physics proceed with single-bit particles, or wait for genuine multi-bit gliders?
- **2D hex glider status:** The 2D hex v=0.469c glider (iter_222) may or may not suffer the same non-interacting composite issue — needs checking.

## Open Questions
1. Can a non-O_h-symmetric LUT produce genuine multi-bit coherent gliders where bits share cells during propagation?
2. Is the monospecific spectrum a fundamental limitation of O_h-symmetric LGCA, or of the specific orbit-matching strategy in generate_symmetric_lut()?
3. Does the 2D hex v=0.469c glider (iter_222) also decompose into non-interacting single-bit particles?
4. Can the weight-≥2 LUT mappings during composite overlap create genuinely emergent phenomena?
5. Should Phase 8 proceed with single-bit fundamental particles, or redesign the LUT?
6. Is the O_h symmetry requirement too restrictive for emergent particle physics?
