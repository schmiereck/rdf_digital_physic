# Research Manager Journal & Strategic State

## 1. High-Level Strategy & Trajectory
*   **Current Phase:** Phase 4.4 (Coupled 3D+1 D4 Lattice Gas Cellular Automaton).
*   **Active Direction:** Formulating and simulating a fully coupled 3D+1 LGCA on the D4 lattice with localized rest-mass channels, building directly on the geometric spacetime foundations established in Phase 4.3.
*   **Confidence Score:** 85% (Strong theoretical backing from D4 geometry; challenge lies in the high-dimensional rule space and simulation complexity).

## 2. Strategic Insights & Lessons Learned
*   **Dimension Scaling & Symmetries:** Successive dimension scaling (1D -> 2D Hex -> 3D FCC -> 4D D4) works exceptionally well when leveraging lattice-specific symmetries (e.g., $O_h$ symmetry for 3D FCC, and D4 root system symmetries).
*   **Fitness Function Exploits:** Evolutionary searches in CA are highly susceptible to "exploits" (Settler, Annihilator, Transient Puffer, Explosive Bloomer, and Breeder-Oscillators). Robust, multi-checkpoint, velocity-gated metrics (like `DisplacementConsistencyFitness`) are mandatory to isolate true coherent structures.
*   **Geometric Spacetime Projection:** Projecting the 4D FCC (D4) lattice perpendicular to the $[1, 1, 1, 1]$ axis naturally yields a 3D+1 discrete spacetime. Relativistic effects (Lorentz factor, time dilation, and Zitterbewegung) emerge analytically from the discrete Minkowski metric $ds^2 = dT^2 - dX^2$.
*   **Discrete Gravity & Fermat's Principle:** Gravitational potential is successfully modeled as a local coordinate speed reduction ($c(r) < 1$). Applying Fermat's principle of least coordinate time on the D4 graph yields observable Shapiro time delay ($\Delta T > 0$) and quantized coordinate light deflection (45° or 56.3° angles due to D4 light cone constraints).

## 3. Loop & Bottleneck Detection
*   **Token & Context Limits:** Phase 228 encountered a hard execution / token limit crash. 3D+1 CA rules on the D4 lattice have massive state spaces (24 nearest neighbors in 4D). We must enforce strict context pruning, use compact symbolic representation of rules, and avoid loading excessive historical logs into sub-agent contexts.
*   **Flat Fitness Landscapes:** Random searches in high dimensions flatline instantly. Future evolutionary runs on D4 must use "warm-starts" (e.g., seeding with projection-mapped 2D/3D champion gliders) and "leaky" fitness metrics that reward partial conservation.

## 4. Alternate Research Paths
*   **Pure Spacetime Geodesics vs. LGCA:** If constructing a fully coupled 3D+1 LGCA with stable 3D gliders proves too computationally expensive, pivot to studying multi-particle worldlines as static topological linkages in the 4D D4 lattice (spacetime-first approach).
*   **Local Latching for Space Curvature:** Investigate "latching" rules where local cells temporarily store and delay incoming bits, effectively generating a dynamic gravitational potential field $U(r)$ out of local mass-energy density, closing the loop toward discrete General Relativity.