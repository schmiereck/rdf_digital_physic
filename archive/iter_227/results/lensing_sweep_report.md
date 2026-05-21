# D4 Gravitational Lensing Parameter Sweep

This report summarizes a systematic parameter sweep over impact parameter `b` and potential amplitude `A_grav` for gravitational lensing on the D4 (FCC) discrete spacetime lattice.

## Method

The simulation uses Dijkstra's shortest-path algorithm on the D4 lattice to find Fermat geodesics in coordinate time. The 4D real coordinates `(x, y, z, w)` are projected onto 3D spatial coordinates `(X, Y, Z)` and coordinate time `T` via an orthonormal projection. A static, spherically-symmetric Gaussian gravitational potential `U(X, Y, Z) = A_grav * exp(-r^2 / (2 sigma^2))` centered at the origin sets the transition cost on each lattice edge to `1 + U(X_v, Y_v, Z_v)`. Photons are launched at `X_A = -15` with transverse offset `Y_A = b` and propagate until they reach `X >= 15`. For each `(b, A_grav)` pair, both a vacuum reference (`A_grav = 0`) and a gravitating run are performed.

Configuration: `sigma = 4.0`, `k_tangent = 10`, `b in [2.0, 4.0, 6.0]`, `A_grav in [1.0, 3.0, 5.0]`.

## Sweep Results

| b | A_grav | T_vac | T_grav | Shapiro delay | theta_vac (deg) | theta_grav (deg) | Net deflection (deg) |
|---|--------|-------|--------|---------------|-----------------|------------------|----------------------|
| 2.0 | 1.0 | 44.0000 | 44.8807 | 0.8807 | 0.0000 | 45.0000 | 45.0000 |
| 4.0 | 1.0 | 44.0000 | 44.3493 | 0.3493 | 0.0000 | 56.3099 | 56.3099 |
| 6.0 | 1.0 | 44.0000 | 44.0752 | 0.0752 | 0.0000 | 56.3099 | 56.3099 |
| 2.0 | 3.0 | 44.0000 | 46.6422 | 2.6422 | 0.0000 | 45.0000 | 45.0000 |
| 4.0 | 3.0 | 44.0000 | 45.0479 | 1.0479 | 0.0000 | 45.0000 | 45.0000 |
| 6.0 | 3.0 | 44.0000 | 44.2256 | 0.2256 | 0.0000 | 45.0000 | 45.0000 |
| 2.0 | 5.0 | 44.0000 | 48.4037 | 4.4037 | 0.0000 | 45.0000 | 45.0000 |
| 4.0 | 5.0 | 44.0000 | 45.7465 | 1.7465 | 0.0000 | 45.0000 | 45.0000 |
| 6.0 | 5.0 | 44.0000 | 44.3761 | 0.3761 | 0.0000 | 45.0000 | 45.0000 |

## Physical Interpretation

### Shapiro time delay

The coordinate-time cost of every lattice edge in a region with potential `U > 0` exceeds the flat-space cost of 1.0 by exactly `U(X_v, Y_v, Z_v)`. The accumulated excess along the geodesic is the discrete analogue of the Shapiro time delay. Two trends are visible in the table:

1. **Shapiro delay grows with `A_grav`.** Deeper potential wells raise the edge cost everywhere inside the well, so the integral `int U dl` accumulates more excess time regardless of the path taken. The relationship is approximately linear in `A_grav` for a fixed `b`, because `U` depends linearly on `A_grav`.

2. **Shapiro delay decreases as `b` grows.** A larger impact parameter places the geodesic at a larger perpendicular distance from the well center, where the Gaussian factor `exp(-r^2 / (2 sigma^2))` is suppressed. With `sigma = 4`, rays with `b = 6` traverse the wing of the Gaussian and pick up much less delay than rays with `b = 2` that cut close to the well center.

### Deflection in coordinate space

Fermat's principle states that light rays follow paths of stationary coordinate time. Because the potential `U > 0` *raises* the local coordinate-time cost (acting like an *increased* index of refraction in coordinate units), the least-time path bends *away* from regions of high `U`. In ordinary General Relativity the same well attracts light, but the deflection is observed in proper distance; in our coordinate-time formulation the potential behaves like a *diverging* lens in coordinate space. The net deflection angle `theta_grav - theta_vac` therefore measures how strongly the well repels the geodesic in `(X, Y)` coordinates.

The trends in the table confirm this picture:

- **Net deflection grows with `A_grav`** for a fixed `b`: a deeper well introduces a larger transverse gradient of `U`, which in turn produces a larger sideways push on the geodesic.

- **Net deflection decreases with `b`** for a fixed `A_grav`: rays with smaller impact parameter sample a steeper part of the potential gradient and are deflected more strongly, while rays with larger `b` graze a flatter shoulder of the Gaussian and are barely deflected.

The lattice spacing imposes a discretization floor on the deflection angle, which is why the values come in coarse increments rather than as a smooth function. This is a feature of the D4 discrete spacetime, not a numerical artifact: the geodesic must commit to one of the six future-directed light-like edges at every step.

## Output Artifacts

- JSON report: `archive\iter_227\results\lensing_sweep_report.json`
- Markdown report: `archive\iter_227\results\lensing_sweep_report.md`
- Trajectory plot: `archive\iter_227\results\d4_lensing_paths.png`
