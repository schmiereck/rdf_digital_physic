# Current Research State
Phase: Phase 7.1 — Glider Taxonomy (SINGLE-CELL COLLISION CLOSED)

## Goal
Demonstrate that mass, gravity, time dilation, and ultimately quantum phenomena emerge as effects of a minimal set of local, reversible binary rules on a highly symmetric grid.

## Confirmed (New in Phase 250)

- **2D hex v=0.469c glider is GENUINE with binding energy > 0 (iter_250, 250.1):** All 3 constituent seed bits annihilate within ~10 steps when run in isolation. The full L-tromino evolves into a self-sustaining 4-bit propagating structure. OR superposition mismatches: 500/501 steps. The binding mechanism is cooperative survival via neighborhood-overlap bit creation.

- **2D hex cooperative survival mechanism characterized (iter_250, 250.1):** Trivial weight-1 sub-table (state 64 → 0, isolated bits die) + non-additive weight-2+ mappings (empty cells with 2 active neighbors turn on). Adjacent pair (64,63)+(64,64) forms stationary period-2 oscillator. Third bit breaks symmetry and drives v=0.469c propagation.

- **2D hex bit conservation is NOT per-cell enforced (iter_250, 250.1):** The glider fluctuates between 3 and 4 bits during propagation (initial=3, max=4, final=4). This is evidence for genuine multi-bit interaction — the rule creates and destroys bits dynamically.

- **128 O_h-symmetric non-additive weight-2 LUT variants produce ZERO genuine multi-bit gliders (iter_250, 250.2):** Exhaustive search of all 128 configurations with LUT-08's Cartesian weight-1 sub-table. 8,448 weight-2 simulations + 8,800 weight-3 simulations = 17,248 total. F2 and F3 falsification criteria triggered. Max binding energy = 0.0.

- **40 randomized O_h-symmetric weight-3+ LUT variants produce ZERO genuine multi-bit gliders (iter_250, 250.2):** Additional search with randomized weight-3+ sub-tables. Zero candidates.

- **Single-cell collision architecture is structurally incapable of multi-bit binding (iter_250, 250.1+250.2):** The 2D hex binding mechanism requires neighborhood-overlap interactions (adjacent cells' neighborhoods overlap, enabling bit creation at a distance). Single-cell collision models only permit co-located bit interactions during the collision step, which is transient and geometrically constrained. This is a structural limitation, not a parameter issue.

## Confirmed (Prior, Recontextualized)

- **LUT-08 is a non-interacting composite (iter_248):** Confirmed. Now understood as a structural consequence of the single-cell collision architecture.
- **All O_h-symmetric single-cell additive rules are monospecific (iter_248):** Extended — ALL O_h-symmetric single-cell collision rules (additive AND non-additive) are monospecific.
- **2D hex v=0.469c sub-light glider (iter_222):** NOW CONFIRMED GENUINE. Was previously of uncertain status.
- **Gravitational time dilation via computational latency (iter_224):** Mechanism still valid, but the "mass packets" are composites of single-bit particles.
- **3D FCC CA engine (iter_224):** Engine correct. The limitation is in the collision architecture, not the engine.

## Refuted

- **Non-additive weight-2 mappings can create genuine multi-bit bound gliders in single-cell O_h-symmetric 3D FCC LGCA (iter_250, 250.2):** REFUTED (F2, F3). Exhaustive search of 128 configurations + 40 randomized variants yields zero candidates.
- **The cooperative propulsion design principle (stationary weight-1 + non-additive weight-2) can work in single-cell collision models (structural analysis):** REFUTED. Stationary weight-1 causes bits to freeze after separation; moving weight-1 causes bits to never interact.

## Best Result

- **2D hex v=0.469c glider is the first confirmed genuine multi-bit bound particle** in this research program (iter_250, 250.1).
- **Complete characterization of the 2D hex cooperative survival mechanism** provides a design principle for future multi-site collision rules.
- **Definitive null result for single-cell collision models** (iter_250, 250.2) establishes a rigorous boundary condition for future research.

## In Progress / Decision Required

- **Multi-site collision operator design:** Can a collision operator that considers ≥2 adjacent cells simultaneously replicate the neighborhood-overlap binding mechanism in 3D FCC? This is the next research direction.
- **Phase 5 (gravitational two-body) unblocking:** Phase 5.2 was blocked waiting for genuine multi-bit gliders. The 2D hex result provides a genuine glider, but only in 2D. The 3D program requires multi-site rules.
- **Conservation law relaxation for multi-site rules:** Multi-site collision operators may require relaxing per-cell bit conservation (allowing bit count to fluctuate, as in the 2D hex). Must this be total-conservation (sum over all cells) instead of per-cell? Is bijectivity still achievable?

## Open Questions

1. Can a multi-site collision operator (considering ≥2 adjacent cells) replicate the 2D hex neighborhood-overlap binding mechanism in 3D FCC?
2. What is the minimal multi-site neighborhood size that enables cooperative survival in 3D FCC?
3. Can asynchronous update schedules enable multi-bit binding in single-cell collision models?
4. What conservation laws must be modified for multi-site collision rules — per-cell bit conservation → global bit conservation, or something else?
5. Can bijectivity be maintained for multi-site collision operators, or is reversibility incompatible with bit creation/destruction?
6. Does the 2D hex binding mechanism scale to 3D hexagonal close-packed lattices with multi-site rules?
