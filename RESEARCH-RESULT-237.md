# RDF Milestone Review — Iteration 236 — Null Result: N-Body Gravitational Binding

## 1. Pre-Declared Hypothesis and Falsification Criterion
- **Working Hypothesis:** Mass-energy density acting as a dynamic local source of coordinate latency generates mutual gravitational-like attraction sufficient to form stable, hierarchical 3-body or 4-body bound states.
- **Falsification Criterion:** The hypothesis is refuted if, under the declared latency-coupling mechanism, the mutual separation of N gliders over >=160 steps is not smaller than that of the vacuum control ($\eta=0.0$) by at least 2x the lattice resolution (i.e., >=1.0 lattice units), or if the active coupling accelerates dispersion.

## 2. Experimental Protocol
- **Grid:** $32^3$ toroidal lattice.
- **Steps:** 160 steps.
- **Particles:** 3-body and 4-body configurations of LUT-08 sub-light gliders.
- **Parameters:** Coupling strength $\eta = 2.0$, smoothing scale $\sigma = 2.5$, decay rate $\gamma = 0.9$.
- **Control Run:** Identical initial coordinates and glider orientations on an identical grid with active coupling disabled ($\eta = 0.0$, pure vacuum propagation).

## 3. Observed Quantities
- **Bit-conservation:** Exact conservation of $4 \times N$ bits (12 bits for 3-body, 16 bits for 4-body) across all 160 steps.
- **Trajectory Dispersion:**
  - Active coupling runs ($\eta = 2.0$) demonstrated systematic repulsion/dispersion. Mean max pair distances were $+2.67$ to $+6.75$ lattice units larger than matched vacuum controls.
  - In Permutation 10 of the 3-body configuration, the vacuum control ($\eta = 0.0$) exhibited a pseudo-bound state with a mean max pair distance of $7.73 \le L/3$ due to velocity alignment on the torus, while the active coupling run dispersed.

## 4. Verdict
- **Refuted.** The outcome **refutes the hypothesis** that the current coordinate latency field can sustain stable hierarchical N-body bound states. The field is dispersive for $N \ge 3$ at the current envelope. Furthermore, the occurrence of torus capture in the matched vacuum control indicates that the previously observed 2-body orbit (Iteration 235) is an orientation-dependent ballistic alignment effect rather than a field-driven gravitational attraction.

## 5. Construction-vs-Empirical Note
- The bit conservation is exact by construction (enforced by the reversibility and binary rules of the underlying LGCA engine).
- The dispersive nature of the latency field and the presence of ballistic recurrence on the torus are empirical behaviors that represent genuine new information about how the coupled field behaves dynamically.

## 6. Limitations
- This null result is bound to the current localized pheromone-like latency deposition scheme ($\eta=2.0$, $\sigma=2.5$, $\gamma=0.9$) on a $32^3$ toroidal grid.
- It does not rule out other local coupling schemes (e.g., gradient-based direct trapping, anisotropic latency fields, or non-toroidal boundary conditions).