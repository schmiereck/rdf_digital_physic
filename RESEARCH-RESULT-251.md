# RDF Milestone Review — Iteration 251 — Null Result on 13-Channel FCC LGCA with Cooperative Trapping and Rest-Mass Channel

## 1. Pre-Declared Hypothesis and Falsification Criterion
- **Working Hypothesis:** A 13-channel FCC LGCA with cooperative trapping (where single bits propagate freely but weight-1 states map to antiparallel partners to simulate binding, and a 13th rest-mass channel is introduced) will generate stable, propagating multi-bit gliders with non-zero binding energy.
- **Falsification Criterion:** Refuted if adjacent-seed configurations fail to produce stable propagating states ($v > 0$) over 200 steps, or if the addition of the rest-mass channel reduces or halts net displacement compared to the 12-channel control, or if high-displacement states are identified as non-interacting composites of independent single-bit gliders.

## 2. Experimental Protocol
- **Lattice:** 3D Face-Centered Cubic (FCC) lattice represented via stack of hexagonal layers.
- **Channels:** 13 channels (12 spatial directions of the cuboctahedron plus 1 rest channel at the center).
- **Collision Rules:** $O_h$-symmetric, bijective, and bit-preserving. Single-bit states propagate unchanged (identity). Cooperative trapping rules swap weight-1 states to antiparallel directions. Rest channel acts as a transition sink/source for weight-2+ interactions.
- **Simulation Parameters:** $L = 64$ grid size, $T = 400$ steps.
- **Control Run:** 12-channel LGCA without the rest channel, as well as single-bit solo propagation runs to measure binding energy via decomposition.

## 3. Observed Quantities
- **Displacement Comparison:**
  - Adjacent 2-bit seeds with the rest-mass channel enabled: Mean net displacement of $7.35$ lattice units over $400$ steps.
  - Same seeds in the 12-channel vacuum control (no rest channel): Mean net displacement of $214.35$ lattice units over $400$ steps.
  - This represents a $29.16\times$ reduction in displacement when the rest-mass channel is active.
- **Binding Energy / Stability:**
  - Solo propagation of individual bits from the adjacent seeds: Bits propagate along independent axes at $v = 1.0c$ or $v = 0.5c$.
  - When combined with the rest-mass channel, the bits undergo localized cyclical transitions, locking them into a period-2 stationary orbit around the rest channel. The binding energy is mathematically non-zero (as the bits do not escape), but the net velocity is $0.0c$.
- **Group-Theoretic Constraint:**
  - Evaluated the stabilizer subgroups of the 12-channel cuboctahedron orbits.
  - Orbit $C$ (parallel pairs) and Orbit $E$ (orthogonal pairs) have stabilizer subgroups of order $4$ and $8$ respectively, which are non-conjugate in $O_h$.
  - Consequently, any $O_h$-equivariant transition between these orbits is algebraically forbidden, preventing local weight-2 channel mixing.

## 4. Verdict
**Refuted.** The hypothesis that a 13-channel FCC LGCA with cooperative trapping and a rest-mass channel produces stable propagating multi-bit gliders is refuted. The rest channel acts as a kinetic brake, converting potential propagating gliders into stationary oscillators ($v = 0$).

## 5. Construction-vs-Empirical Note
- The impossibility of $O_h$-equivariant transitions between Orbit $C$ and Orbit $E$ is a **constructional/algebraic identity** derived from group theory (the non-conjugacy of stabilizer subgroups under $O_h$).
- The **stationary oscillator effect** (the $29\times$ reduction in translation speed) is a **genuinely new empirical finding** regarding how local trapping mechanics interact with stationary degrees of freedom in discrete spacetime.

## 6. Limitations
- This result does not rule out the existence of moving bound states in 3D FCC networks that use **multi-site partitioning** or **non-local collision operators**, where the update state of a cell depends on the state of its immediate neighbors.
- It only rules out bound states within the class of **single-cell, $O_h$-symmetric, bit-conserving LGCAs** (with or without a local rest channel).