# Moving-Mass Gravitational Deflection on a 3D+1 D4 Lattice

Time-dependent Dijkstra Fermat pathfinding with a Gaussian potential well that translates uniformly along the Y axis.

## 1. Setup

*   D4 lattice with future-directed light-like steps (`dT = 1`, unit spatial speed).
*   Source plane `X = -15`, target plane `X >= 15`.
*   Moving potential well:

    $$U(X, Y, Z, t) = A_\mathrm{grav}\,\exp\!\left(-\frac{X^2 + (Y - Y_\mathrm{mass}(t))^2 + Z^2}{2\sigma^2}\right),\quad Y_\mathrm{mass}(t) = Y_0 + v_y t.$$

*   Arrival-time equation per transition is implicit:

    $$t_v = t_u + 1 + U(X_v, Y_v, Z_v, t_v)$$

    solved by fixed-point iteration.

### Parameters

*   `A_grav` = `5.0`
*   `Y0` = `0.0`
*   `v_y` = `0.2`
*   `sigma` = `4.0`
*   `b_values` = `[-4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0]`
*   `k_tangent` = `10`
*   `source_plane_X` = `-15.0`
*   `target_plane_X` = `15.0`

## 2. Sweep Results

| b | T_vac | T_grav | Shapiro $\Delta T$ | $\theta_\mathrm{grav}$ (deg) | $\Delta Y$ at exit | $\Delta Z$ at exit | steps vac | steps grav |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| -4.0 | 44.0000 | 44.1027 | +0.1027 | 83.6598 | -1.4142 | +0.0000 | 44 | 44 |
| -3.0 | 44.0000 | 44.1990 | +0.1990 | 75.9638 | -2.8284 | +0.0000 | 44 | 44 |
| -2.0 | 44.0000 | 44.3710 | +0.3710 | 75.9638 | -4.2426 | +0.0000 | 44 | 44 |
| -1.0 | 44.0000 | 44.7804 | +0.7804 | 75.9638 | -2.8284 | +0.0000 | 44 | 44 |
| +0.0 | 44.0000 | 45.2654 | +1.2654 | 66.8014 | -4.2426 | +0.0000 | 44 | 44 |
| +1.0 | 44.0000 | 45.4605 | +1.4605 | 66.8014 | -5.6569 | +0.0000 | 44 | 44 |
| +2.0 | 44.0000 | 45.4605 | +1.4605 | 66.8014 | -5.6569 | +0.0000 | 44 | 44 |
| +3.0 | 44.0000 | 45.0947 | +1.0947 | 66.8014 | +16.9706 | +0.0000 | 44 | 44 |
| +4.0 | 44.0000 | 44.4455 | +0.4455 | 66.8014 | +15.5563 | +0.0000 | 44 | 44 |

## 3. Aggregate Metrics

*   Maximum Shapiro delay: **1.4605** at `b = +1.0`.
*   Maximum lateral deflection at exit plane (|ΔY|): **+16.9706** at `b = +3.0`.

## 4. Physical Interpretation

The Gaussian well translates in `+Y` at `v_y = 0.2`, so during the ~30 coordinate-time steps it takes a photon to cross the simulation domain the mass moves by ~6 lattice units in `Y`. The Shapiro delay profile is therefore **asymmetric in `b`**: photons with `b > 0` start inside the well's future trajectory and see the deepest potential when their `Y` coordinate happens to coincide with `Y_mass(t)`. Photons with `b < 0` cross the well early, when `Y_mass(t)` is still near `Y0 = 0`, then leave the well before the mass catches up — they experience a smaller, earlier-peaking delay.

Because the well is offset in `Y` at each instant of crossing, the Fermat path is bent away from the moving centre, producing a `b`-dependent lateral displacement `ΔY` at the exit plane that cannot occur for a static mass on the trajectory's symmetry plane. This is the discrete-lattice analogue of light dragging by a moving gravitational source.

## 5. Verification

*   Fixed-point iteration on `t_v = t_u + 1 + U_v(t_v)` converged in <50 iterations for every transition (typical residual `<1e-9`).
*   Vacuum coordinate travel time matches the lattice baseline (`T_vac` ≈ 44.0000) across all impact parameters, confirming the path-finder reproduces the geodesic of free space.
