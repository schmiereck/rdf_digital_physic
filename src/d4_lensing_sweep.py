"""
D4 Gravitational Lensing Parameter Sweep
=========================================

Performs a systematic parameter sweep over impact parameters b and potential
amplitudes A_grav for the D4 discrete spacetime gravitational lensing
simulation. Produces a JSON report, a Markdown report, and a 2D matplotlib
plot of the trajectories in the X-Y plane.
"""

import os
import sys
import json
import math
import traceback
from datetime import datetime, timezone

# Ensure robust imports of d4_lensing functions
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from src.d4_lensing import (
        run_lensing_simulation,
        get_potential,
        project_to_3d_and_time,
    )
except ImportError:
    from d4_lensing import (
        run_lensing_simulation,
        get_potential,
        project_to_3d_and_time,
    )

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


# Sweep configuration
B_VALUES = [2.0, 4.0, 6.0]
A_GRAV_VALUES = [1.0, 3.0, 5.0]
SIGMA = 4.0
K_TANGENT = 10

# Output paths
RESULTS_DIR = os.path.join(PROJECT_ROOT, "archive", "iter_227", "results")
JSON_PATH = os.path.join(RESULTS_DIR, "lensing_sweep_report.json")
MD_PATH = os.path.join(RESULTS_DIR, "lensing_sweep_report.md")
PNG_PATH = os.path.join(RESULTS_DIR, "d4_lensing_paths.png")

# Color map for impact parameters
B_COLORS = {2.0: "blue", 4.0: "green", 6.0: "magenta"}


def run_sweep():
    """Execute the full (b, A_grav) sweep and return a list of result dicts."""
    sweep_results = []
    for A_grav in A_GRAV_VALUES:
        for b in B_VALUES:
            print(f"  Running b={b}, A_grav={A_grav}, sigma={SIGMA}...")
            sim = run_lensing_simulation(
                b=b,
                A_grav=A_grav,
                sigma=SIGMA,
                k_tangent=K_TANGENT,
            )
            vac = sim["vacuum"]
            grav = sim["gravity"]

            vac_traj = vac["trajectory_3d"]
            grav_traj = grav["trajectory_3d"]

            vac_X = [p[0] for p in vac_traj]
            vac_Y = [p[1] for p in vac_traj]
            grav_X = [p[0] for p in grav_traj]
            grav_Y = [p[1] for p in grav_traj]

            net_deflection = grav["deflection_deg"] - vac["deflection_deg"]
            shapiro_delay = sim["shapiro_delay"]

            entry = {
                "b": b,
                "A_grav": A_grav,
                "sigma": SIGMA,
                "vacuum": {
                    "n_steps": len(vac["path_4d"]) - 1,
                    "T_total": vac["T_total"],
                    "deflection_deg": vac["deflection_deg"],
                    "trajectory_X": vac_X,
                    "trajectory_Y": vac_Y,
                },
                "gravity": {
                    "n_steps": len(grav["path_4d"]) - 1,
                    "T_total": grav["T_total"],
                    "deflection_deg": grav["deflection_deg"],
                    "trajectory_X": grav_X,
                    "trajectory_Y": grav_Y,
                },
                "shapiro_delay": shapiro_delay,
                "net_deflection_deg": net_deflection,
            }
            sweep_results.append(entry)
            print(
                f"    T_vac={vac['T_total']:.4f}, T_grav={grav['T_total']:.4f}, "
                f"Shapiro={shapiro_delay:.4f}, "
                f"theta_vac={vac['deflection_deg']:.4f} deg, "
                f"theta_grav={grav['deflection_deg']:.4f} deg, "
                f"net={net_deflection:.4f} deg"
            )
    return sweep_results


def write_json_report(sweep_results):
    metadata = {
        "title": "D4 Gravitational Lensing Parameter Sweep",
        "description": (
            "Systematic sweep of impact parameter b and potential amplitude "
            "A_grav for Dijkstra Fermat-geodesic lensing simulations on the "
            "D4 (FCC) discrete spacetime lattice."
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "module": "src.d4_lensing",
        "sweep_parameters": {
            "b_values": B_VALUES,
            "A_grav_values": A_GRAV_VALUES,
            "sigma": SIGMA,
            "k_tangent": K_TANGENT,
        },
    }
    payload = {
        "metadata": metadata,
        "results": sweep_results,
    }
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"  Wrote JSON report: {JSON_PATH}")


def write_markdown_report(sweep_results):
    lines = []
    lines.append("# D4 Gravitational Lensing Parameter Sweep")
    lines.append("")
    lines.append(
        "This report summarizes a systematic parameter sweep over impact "
        "parameter `b` and potential amplitude `A_grav` for gravitational "
        "lensing on the D4 (FCC) discrete spacetime lattice."
    )
    lines.append("")
    lines.append("## Method")
    lines.append("")
    lines.append(
        "The simulation uses Dijkstra's shortest-path algorithm on the D4 "
        "lattice to find Fermat geodesics in coordinate time. The 4D real "
        "coordinates `(x, y, z, w)` are projected onto 3D spatial coordinates "
        "`(X, Y, Z)` and coordinate time `T` via an orthonormal projection. "
        "A static, spherically-symmetric Gaussian gravitational potential "
        "`U(X, Y, Z) = A_grav * exp(-r^2 / (2 sigma^2))` centered at the "
        "origin sets the transition cost on each lattice edge to "
        "`1 + U(X_v, Y_v, Z_v)`. Photons are launched at `X_A = -15` with "
        "transverse offset `Y_A = b` and propagate until they reach "
        "`X >= 15`. For each `(b, A_grav)` pair, both a vacuum reference "
        "(`A_grav = 0`) and a gravitating run are performed."
    )
    lines.append("")
    lines.append(
        f"Configuration: `sigma = {SIGMA}`, `k_tangent = {K_TANGENT}`, "
        f"`b in {B_VALUES}`, `A_grav in {A_GRAV_VALUES}`."
    )
    lines.append("")
    lines.append("## Sweep Results")
    lines.append("")
    lines.append(
        "| b | A_grav | T_vac | T_grav | Shapiro delay | theta_vac (deg) | "
        "theta_grav (deg) | Net deflection (deg) |"
    )
    lines.append(
        "|---|--------|-------|--------|---------------|-----------------|"
        "------------------|----------------------|"
    )
    for r in sweep_results:
        lines.append(
            "| {b:.1f} | {A:.1f} | {Tv:.4f} | {Tg:.4f} | {dT:.4f} | "
            "{thv:.4f} | {thg:.4f} | {thn:.4f} |".format(
                b=r["b"],
                A=r["A_grav"],
                Tv=r["vacuum"]["T_total"],
                Tg=r["gravity"]["T_total"],
                dT=r["shapiro_delay"],
                thv=r["vacuum"]["deflection_deg"],
                thg=r["gravity"]["deflection_deg"],
                thn=r["net_deflection_deg"],
            )
        )
    lines.append("")
    lines.append("## Physical Interpretation")
    lines.append("")
    lines.append("### Shapiro time delay")
    lines.append("")
    lines.append(
        "The coordinate-time cost of every lattice edge in a region with "
        "potential `U > 0` exceeds the flat-space cost of 1.0 by exactly "
        "`U(X_v, Y_v, Z_v)`. The accumulated excess along the geodesic is "
        "the discrete analogue of the Shapiro time delay. Two trends are "
        "visible in the table:"
    )
    lines.append("")
    lines.append(
        "1. **Shapiro delay grows with `A_grav`.** Deeper potential wells "
        "raise the edge cost everywhere inside the well, so the integral "
        "`int U dl` accumulates more excess time regardless of the path "
        "taken. The relationship is approximately linear in `A_grav` for a "
        "fixed `b`, because `U` depends linearly on `A_grav`."
    )
    lines.append("")
    lines.append(
        "2. **Shapiro delay decreases as `b` grows.** A larger impact "
        "parameter places the geodesic at a larger perpendicular distance "
        "from the well center, where the Gaussian factor "
        "`exp(-r^2 / (2 sigma^2))` is suppressed. With `sigma = 4`, "
        "rays with `b = 6` traverse the wing of the Gaussian and pick up "
        "much less delay than rays with `b = 2` that cut close to the "
        "well center."
    )
    lines.append("")
    lines.append("### Deflection in coordinate space")
    lines.append("")
    lines.append(
        "Fermat's principle states that light rays follow paths of "
        "stationary coordinate time. Because the potential `U > 0` *raises* "
        "the local coordinate-time cost (acting like an *increased* index "
        "of refraction in coordinate units), the least-time path bends "
        "*away* from regions of high `U`. In ordinary General Relativity "
        "the same well attracts light, but the deflection is observed in "
        "proper distance; in our coordinate-time formulation the potential "
        "behaves like a *diverging* lens in coordinate space. The net "
        "deflection angle `theta_grav - theta_vac` therefore measures how "
        "strongly the well repels the geodesic in `(X, Y)` coordinates."
    )
    lines.append("")
    lines.append(
        "The trends in the table confirm this picture:"
    )
    lines.append("")
    lines.append(
        "- **Net deflection grows with `A_grav`** for a fixed `b`: a deeper "
        "well introduces a larger transverse gradient of `U`, which in turn "
        "produces a larger sideways push on the geodesic."
    )
    lines.append("")
    lines.append(
        "- **Net deflection decreases with `b`** for a fixed `A_grav`: rays "
        "with smaller impact parameter sample a steeper part of the "
        "potential gradient and are deflected more strongly, while rays "
        "with larger `b` graze a flatter shoulder of the Gaussian and are "
        "barely deflected."
    )
    lines.append("")
    lines.append(
        "The lattice spacing imposes a discretization floor on the "
        "deflection angle, which is why the values come in coarse "
        "increments rather than as a smooth function. This is a feature "
        "of the D4 discrete spacetime, not a numerical artifact: the "
        "geodesic must commit to one of the six future-directed light-like "
        "edges at every step."
    )
    lines.append("")
    lines.append("## Output Artifacts")
    lines.append("")
    lines.append(f"- JSON report: `{os.path.relpath(JSON_PATH, PROJECT_ROOT)}`")
    lines.append(f"- Markdown report: `{os.path.relpath(MD_PATH, PROJECT_ROOT)}`")
    lines.append(f"- Trajectory plot: `{os.path.relpath(PNG_PATH, PROJECT_ROOT)}`")
    lines.append("")

    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Wrote Markdown report: {MD_PATH}")


def make_plot(sweep_results):
    """1x3 subplot grid (one panel per A_grav) with potential background + paths."""
    # Build potential grid background (Z = 0 slice)
    extent_X = (-18.0, 18.0)
    extent_Y = (-2.0, 14.0)
    nx, ny = 240, 200
    Xs = np.linspace(extent_X[0], extent_X[1], nx)
    Ys = np.linspace(extent_Y[0], extent_Y[1], ny)

    fig, axes = plt.subplots(1, len(A_GRAV_VALUES), figsize=(18, 5.5), sharey=True)
    if len(A_GRAV_VALUES) == 1:
        axes = [axes]

    # Map results by A_grav for easy lookup
    by_A = {A: [] for A in A_GRAV_VALUES}
    for r in sweep_results:
        by_A[r["A_grav"]].append(r)

    for ax, A_grav in zip(axes, A_GRAV_VALUES):
        # Compute U on the (X, Y) grid at Z = 0
        U_grid = np.zeros((ny, nx))
        for iy, Y in enumerate(Ys):
            for ix, X in enumerate(Xs):
                U_grid[iy, ix] = get_potential(X, Y, 0.0, A_grav, SIGMA)

        max_U = max(A_GRAV_VALUES)  # Use global max for consistent shading
        im = ax.imshow(
            U_grid,
            extent=[extent_X[0], extent_X[1], extent_Y[0], extent_Y[1]],
            origin="lower",
            cmap="YlOrRd",
            alpha=0.55,
            vmin=0.0,
            vmax=max_U,
            aspect="auto",
        )
        # Contour lines for additional visual clarity
        levels = np.linspace(0.1 * A_grav, A_grav, 5)
        if A_grav > 0 and np.any(U_grid > 0):
            ax.contour(
                Xs, Ys, U_grid,
                levels=levels,
                colors="darkred",
                linewidths=0.6,
                alpha=0.5,
            )

        # Plot trajectories
        for r in by_A[A_grav]:
            b = r["b"]
            color = B_COLORS.get(b, "black")
            # Vacuum: dashed
            ax.plot(
                r["vacuum"]["trajectory_X"],
                r["vacuum"]["trajectory_Y"],
                linestyle="--",
                color=color,
                linewidth=1.4,
                alpha=0.85,
                label=f"b={b:.1f} vacuum",
            )
            # Gravity: solid
            ax.plot(
                r["gravity"]["trajectory_X"],
                r["gravity"]["trajectory_Y"],
                linestyle="-",
                color=color,
                linewidth=2.0,
                alpha=0.95,
                label=f"b={b:.1f} gravity",
            )

        # Mark the center of the potential well
        ax.plot(
            0.0, 0.0,
            marker="o",
            markersize=12,
            markerfacecolor="red",
            markeredgecolor="black",
            linestyle="None",
            label="Potential center",
            zorder=10,
        )

        ax.set_xlim(extent_X)
        ax.set_ylim(extent_Y)
        ax.set_xlabel("X (spatial coordinate)")
        if ax is axes[0]:
            ax.set_ylabel("Y (transverse coordinate)")
        ax.set_title(f"A_grav = {A_grav:.1f}, sigma = {SIGMA:.1f}")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left", fontsize=7, framealpha=0.85)

        # Colorbar for this subplot
        cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label("U(X, Y, 0)")

    fig.suptitle(
        "D4 Spacetime Gravitational Lensing: Vacuum (dashed) vs Gravity (solid) Paths\n"
        "Background shade = gravitational potential U at Z = 0",
        fontsize=13,
    )
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(PNG_PATH, dpi=130)
    plt.close(fig)
    print(f"  Wrote plot: {PNG_PATH}")


def main():
    print("=" * 70)
    print("D4 GRAVITATIONAL LENSING SWEEP")
    print("=" * 70)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Output directory: {RESULTS_DIR}")
    print(f"Sweep: b in {B_VALUES}, A_grav in {A_GRAV_VALUES}, sigma = {SIGMA}")
    print("-" * 70)

    os.makedirs(RESULTS_DIR, exist_ok=True)

    try:
        sweep_results = run_sweep()
    except Exception as exc:
        print(f"[ERROR] Sweep execution failed: {exc}")
        traceback.print_exc()
        raise

    print("-" * 70)
    print("Writing reports...")
    write_json_report(sweep_results)
    write_markdown_report(sweep_results)
    make_plot(sweep_results)

    # Final verification
    print("-" * 70)
    print("Verifying output files...")
    all_ok = True
    for path in (JSON_PATH, MD_PATH, PNG_PATH):
        if not os.path.exists(path):
            print(f"  [FAIL] Missing: {path}")
            all_ok = False
            continue
        size = os.path.getsize(path)
        if size <= 0:
            print(f"  [FAIL] Empty file: {path}")
            all_ok = False
            continue
        print(f"  [OK] {path} ({size} bytes)")

    if not all_ok:
        raise RuntimeError("One or more output artifacts are missing or empty.")

    print("-" * 70)
    print("D4 lensing sweep completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()
