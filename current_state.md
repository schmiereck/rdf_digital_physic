# Current Research State
Phase: Phase 5.3 — Orbital Dynamics completed.

## Goal
Demonstrate a sustained bound state (closed or quasi-closed orbit) of two mass packets on the lattice, verifying O_h covariance and characterizing discretization and resolution limits.

## Confirmed
- **Lattice-Level Symmetry Breaking:** Demonstrated that the 48 permutations of the octahedral group ($O_h$) are broken at the discrete lattice level (reconstruction errors up to 1.75 cells) due to the non-orthogonal projected coordinate system of the layers stacking grid (`check_oh_transform.py`, iter_235.4).
- **Discretization and Drift Noise:** In the Vacuum Control runs, rotated parallel gliders naturally drift apart (disperse by up to 19.69 cells in 80 steps) because rounding rotated coordinates to integers perturbs their relative launch alignment (`test_oh_covariance.py`, iter_235.6).
- **Long-Term Sustained Bound State:** Under active coupling ($\eta=2.0$), the dynamic latency field creates a self-consistent potential well that acts as a strong attractive binding force, completely countering the massive vacuum dispersion. In a 160-step run of Permutation 10, the active coupling successfully kept the two gliders bound, exhibiting **five distinct periapsis returns** where the gliders start to separate but are repeatedly pulled back into tight binding (~2.75 to 2.89 cells separation), while the vacuum control run dispersed early and repeatedly (`test_bound_state_long.py`, iter_235.8).
- **Perfect Bit and Structural Conservation:** The LUT-08 gliders proved exceptionally robust to integer rounding and dynamic latches, maintaining perfect structure and bit conservation (exactly 8 bits) throughout the 160-step bound state (iter_235.8).

## Refuted
- The assumption that $O_h$ symmetry is exactly preserved as a linear coordinate transformation on a discrete hexagonal layer-stacking grid; it is broken by non-orthogonal basis vectors, resulting in a baseline discretization noise of up to 1.75 grid units (iter_235.4).

## Best Result
- Permutation 10 active 160-step run maintains a tightly bound state with five complete periapsis returns at stable separation (~2.79 cells) under baseline parameters ($\sigma=2.5$, $\eta=2.0$, $\gamma=0.9$, $\text{threshold}=0.045$), whereas the vacuum control disperses completely (iter_235.8).

## In Progress
- Exploring three-body and many-body gravitational configurations (Phase 5.4).

## Open Questions
- Does the bound state lifetime scale with increased grid resolution (e.g. on a $64^3$ grid)?
- Can we form a stable, dynamic three-body cluster or bound state (Phase 5.4)?
- What is the escape velocity bound for a two-body bound state under our discrete potential field?
