# Phase 7.3 — Antiparticle CPT Experiment (Iter 245)

## Pre-Declared Hypothesis & Falsification

**Hypothesis:** The P-reflected (enantiomeric) LUT-08 glider — designated the "antiparticle" — is stable under the forward rule. When a LUT-08 particle and its antiparticle undergo head-on collision, they annihilate cleanly (≤2 residual non-propagating bits, total bit count conserved at 8), producing exclusively v=1c single-bit propagating states. This outcome was expected to differ qualitatively from same-chirality particle-particle collisions, which were hypothesized to scatter elastically.

**Falsification Criteria (from pre_registration.md):**
1. CPT-conjugate glider not bit-conserving over ≥80 solo steps.
2. In ≥3/5 opposite-chirality collision configs, residual non-propagating bits exceed 2.
3. Opposite-chirality collisions show the same elastic outcome as same-chirality collisions (no qualitative distinction).
4. Collision outcome is not O_h-covariant: rotating the setup through an O_h element changes the outcome qualitatively, indicating a lattice artifact.

## Protocol

1. **Loaded** LUT-08 rule and reference glider from `archive/iter_224/results/glider_00_lut08_sub03.json`.
2. **Constructed particles:**
   - `pA` — original LUT-08 glider (χ = −4).
   - `pB` — P-reflected glider (χ = +4), the "antiparticle".
   - `pC` — same-chirality reversed-velocity glider found by scanning the 24 proper O_h rotations and selecting the one whose 1-step displacement best approximates `−v_A` (achieved score −0.011, displacement [−0.259, +0.496, −1.0] vs pA [+0.248, −0.496, +1.0]).
3. **CONTROL A (constructional):** Ran `pB` and `pC` solo for 80 steps on a 32³ grid. Verified bit count = 4 at every step.
4. **EXPERIMENT:** Ran 5 opposite-chirality collision configurations (`pA` vs `pB`) with impact-parameter offsets `(0,0,0), (0,1,0), (0,2,0), (0,0,1), (0,1,1)` perpendicular to the collision axis. Each run: 100 steps.
5. **CONTROL B:** Ran 5 same-chirality collision configurations (`pA` vs `pC`) with identical impact parameters. Each run: 100 steps.
6. **O_h covariance test:** Took the head-on opposite-chirality config, rotated both particles and their center positions through the first non-identity proper O_h element (det = +1), and re-ran 100 steps.
7. **Classification:**
   - *Elastic* — exactly 2 four-bit clusters, 8 bits total.
   - *Annihilation* — 0 four-bit clusters, all bits isolated (1-bit clusters).
   - *Partial* — exactly 1 four-bit cluster + debris.
   - *Chaotic* — 0 four-bit clusters + debris.

## Observations

### Solo Stability (CONTROL A)
| Particle | Chirality | 80-step solo stable? |
|----------|-----------|----------------------|
| pA (original) | −4 | Yes (constructional) |
| pB (P-reflected "antiparticle") | +4 | **Yes** |
| pC (same-chirality, reversed velocity) | −4 | **Yes** |

### Opposite-Chirality Collisions (EXPERIMENT: pA vs pB)
| # | Offset | Outcome | Bits | 4-bit clusters | Isolated bits |
|---|--------|---------|------|----------------|---------------|
| 0 | (0,0,0) | **Elastic** | 8 | 2 | 0 |
| 1 | (0,1,0) | **Elastic** | 8 | 2 | 0 |
| 2 | (0,2,0) | **Elastic** | 8 | 2 | 0 |
| 3 | (0,0,1) | **Elastic** | 8 | 2 | 0 |
| 4 | (0,1,1) | **Elastic** | 8 | 2 | 0 |

**Result:** 5/5 elastic. **0/5 annihilation.** Both gliders emerge intact in every configuration.

### Same-Chirality Collisions (CONTROL B: pA vs pC)
| # | Offset | Outcome | Bits | 4-bit clusters | Isolated bits |
|---|--------|---------|------|----------------|---------------|
| 0 | (0,0,0) | **Partial** | 8 | 1 | 1 |
| 1 | (0,1,0) | **Partial** | 8 | 1 | 1 |
| 2 | (0,2,0) | **Chaotic** | 8 | 0 | 0 |
| 3 | (0,0,1) | **Partial** | 8 | 1 | 1 |
| 4 | (0,1,1) | **Chaotic** | 8 | 0 | 0 |

**Result:** 0/5 elastic. Collisions are destructive (partial or chaotic).

### O_h Covariance Test
| Configuration | Outcome | Bits | 4-bit clusters | Isolated bits |
|---------------|---------|------|----------------|---------------|
| Unrotated head-on (pA vs pB) | Elastic | 8 | 2 | 0 |
| Rotated head-on (proper O_h) | **Chaotic** | 8 | 0 | 5 |

**Result:** Rotating the collision setup changes the outcome from **Elastic → Chaotic**.

## Verdict

| Criterion | Status | Reason |
|-----------|--------|--------|
| **F1** — Solo instability of antiparticle | **PASS** | pB conserved 4 bits for all 80 steps. |
| **F2** — ≥3/5 messy annihilations (residual bits > 2) | **PASS** | 0/5 messy; all 5 were elastic with 0 residual bits. |
| **F3** — No qualitative distinction (both elastic) | **PASS** | Outcomes are qualitatively **different**: opposite-chirality = elastic, same-chirality = destructive. |
| **F4** — O_h non-covariance indicates lattice artifact | **FAIL** | Unrotated elastic → rotated chaotic. The outcome is **not O_h-covariant**, indicating the result is a lattice-axis artifact rather than genuine physics. |
| **Central prediction** — Opposite-chirality annihilation | **FAIL** | The hypothesis predicted annihilation; the observed outcome is elastic scattering in all cases. |

**Overall verdict: HYPOTHESIS REFUTED.**

The data falsifies the central claim that opposite-chirality collisions annihilate. Instead, particle-antiparticle collisions are perfectly elastic under the tested impact parameters. The same-chirality control is destructive, which is the opposite of the pre-registered expectation. Furthermore, the O_h covariance test fails, demonstrating that even the elastic outcome is not a robust physical effect but is sensitive to lattice orientation.

## Construction-vs-Empirical Note

- **pB solo stability:** This is a **constructional** result, not an empirical finding. The P-reflected glider is stable under the forward LUT-08 rule by virtue of O_h symmetry: the rule is invariant under the full octahedral group, so any spatial reflection of a stable glider is also stable.
- **pC solo stability:** Similarly constructional. pC is obtained by a proper O_h rotation (det = +1) of pA, and the rule's O_h invariance guarantees stability.
- **Collision dynamics:** These are the **only genuine empirical results** in this experiment. The observation that opposite-chirality collisions scatter elastically, that same-chirality collisions are destructive, and that outcomes are not O_h-covariant are all empirical findings about the LUT-08 rule's many-body dynamics.

## Limitations

1. **Impact-parameter sampling:** Only 5 offsets were tested (0, 1, 2 in one perpendicular direction and 0, 1 in another). A denser sweep might reveal narrow windows of annihilation.
2. **Integration time:** 100 steps may be insufficient to capture very late-time recombination or escape of debris. Extending to 200+ steps would strengthen the null result.
3. **Single O_h rotation:** Only one non-trivial proper rotation was used for the covariance test. Testing additional rotations would better characterize the degree of anisotropy.
4. **Coarse classification:** The four-class scheme (Elastic / Annihilation / Partial / Chaotic) does not distinguish between different debris topologies (e.g., 2-bit dimers vs 3-bit trimers vs isolated single-bit states with different velocities).
5. **Grid size:** L = 32 is sufficient for short runs but may introduce toroidal wrap-around artifacts for gliders with long mean free paths.
6. **Phase alignment:** The experiment used the canonical phase of each glider. A phase-offset sweep (as in iter_242-style collision scans) was not performed.
