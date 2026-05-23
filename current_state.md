# Current Research State
Phase: Phase 5.2 — Self-Consistent Mutual Two-Body Attraction completed (refuted).

## Goal
Establish whether two LUT-08 sub-light gliders, each acting as a local source of dynamic coordinate latency, bias each other's trajectories beyond what is reproducible by the vacuum control or by free parameter tuning.

## Confirmed
- **Non-periodic isolation:** Implemented margin=2 absorbing boundaries on an L=64 grid coupled with a zero-padded 3D FFT potential solver (NonPeriodicClosedLoopLatchingEngine), completely isolating the system from periodic wrap-around or self-potential bleed-through (iter_238.4).
- **Pre-registered Null Result:** Under the pre-registered parameters (sigma=1.5, gamma=0.9, eta=2.0, R=1.1), the parallel gliders showed exactly 0.0000 cells of mutual deflection over 50 steps (iter_238.4).
- **Sub-pixel deflection:** The best configuration from the 192-config sweep (sigma=2.0, gamma=0.95, eta=2.0, R=1.1) yielded a tiny, sub-pixel mutual deflection of exactly 0.2500 cells (iter_238.4).
- **Symmetry breaking:** Rotating the initial state of the best configuration by 90 degrees (rotation g=10 around the Z-axis) introduced severe rounding errors in the discrete coordinate projections, causing massive non-physical ballistic drift in the vacuum control (final separation = nan cells) and making the final active deflection nan (iter_238.4).
- **Perfect bit conservation:** Total bit count (8 bits) and structural stability were perfectly maintained across all unrotated simulation runs (iter_238.4).

## Refuted
- **Hypothesis of Emergent Two-Body Mutual Gravity:** The dynamic latency potential is refuted as a viable mechanism for isotropic, physically significant emergent mutual attraction on this CA grid. Any observed deflection is either non-existent (0.0 cells) or a discrete lattice-alignment artifact, failing to satisfy O_h covariance and falling far below the 2.0-cell physical significance threshold.

## Best Result
- Net mutual deflection of exactly 0.2500 cells under sigma=2.0, gamma=0.95, eta=2.0, R=1.1; however, this deflection fails rotational covariance testing, confirming it as an anisotropy artifact of the discrete grid axes.

## In Progress
- Pivot to Phase 6: Quantum Emergence.

## Open Questions
- Can we design a non-FFT based coordinate latency field (such as an anisotropic, direct bit-contact latching or gradient-based trapping) that is fundamentally robust against lattice-axis alignment?
- Is the discrete breakdown of coordinate covariance an insuperable barrier for emergent GR on highly symmetric grids?
- Should we pivot to Phase 6 (Quantum Emergence) or Phase 7 (Particle Zoo) now that Phase 5's GR-like mutual dynamics are shown to be algebraic and lattice-discretization artifacts?
