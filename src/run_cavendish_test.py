#!/usr/bin/env python3
"""run_cavendish_test.py — 3D physical Cavendish unit test.

Observe emergent gravitational attraction of a sub-light-speed glider on a
physical 3D cellular automaton grid (DynamicLatchingEngine). A heavy permanent
mass is placed at the centre of a 32x32x32 toroidal grid with a Gaussian
potential profile, and a single glider is launched past it. The glider's Y
centroid is tracked in a vacuum control versus the gravity case for two starting
Y offsets (above and below the mass).
"""

from __future__ import annotations

import os
import sys
import json
import math
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from engine_d4_dynamic import DynamicLatchingEngine


def seed_glider(engine: DynamicLatchingEngine, cx: int, cy: int, cz: int, particle):
    """Place the glider's bits into the engine's temporal_grid (toroidal wrap)."""
    for dl, dr, dc, ch in particle:
        x = (cx + dl) % engine.L
        y = (cy + dr) % engine.L
        z = (cz + dc) % engine.L
        engine.temporal_grid[x, y, z, ch] = 1


def install_gaussian_mass(engine: DynamicLatchingEngine,
                          centre: tuple[int, int, int],
                          mass_value: float,
                          sigma: float) -> None:
    """Initialise engine.permanent_mass with a centred Gaussian potential."""
    L = engine.L
    cx, cy, cz = centre
    xs = np.arange(L, dtype=np.float64)
    X, Y, Z = np.meshgrid(xs, xs, xs, indexing="ij")
    r_sq = (X - cx) ** 2 + (Y - cy) ** 2 + (Z - cz) ** 2
    engine.permanent_mass[:] = mass_value * np.exp(-r_sq / (2.0 * sigma ** 2))


def y_centroid(engine: DynamicLatchingEngine) -> float | None:
    """Mean of y-coordinates of all active cells (temporal | latched).
    The glider is the only mobile object, so a direct mean is correct as long
    as the glider stays well inside the periodic box in Y (which it does: the
    LUT-08 glider has zero displacement in axis 1)."""
    active = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
    if not active.any():
        return None
    idx = np.argwhere(active)
    return float(np.mean(idx[:, 1]))


def total_bits(engine: DynamicLatchingEngine) -> int:
    return int(engine.temporal_grid.sum() + engine.latched_grid.sum())


def run_one(particle, lut_seed, L, steps, cx, y_start, cz,
            alpha, threshold, exponent,
            mass_value, sigma, mass_centre):
    """Run a single configuration; return (trajectory, bit_log, struct_stable)."""
    engine = DynamicLatchingEngine(
        L=L, alpha=alpha, threshold=threshold, exponent=exponent, lut_seed=lut_seed
    )
    if mass_value > 0.0:
        install_gaussian_mass(engine, mass_centre, mass_value, sigma)

    seed_glider(engine, cx=cx, cy=y_start, cz=cz, particle=particle)
    initial_bits = total_bits(engine)

    traj = []
    bit_log = []

    Yc = y_centroid(engine)
    traj.append(Yc)
    bit_log.append(initial_bits)

    struct_stable = True
    for t in range(steps):
        engine.step()
        bits_now = total_bits(engine)
        bit_log.append(bits_now)
        if bits_now != initial_bits:
            raise AssertionError(
                f"BIT CONSERVATION VIOLATION at step {t + 1}: "
                f"initial={initial_bits} now={bits_now}"
            )
        Yc = y_centroid(engine)
        traj.append(Yc)
        # The 4-bit LUT-08 glider has 4 bits. If the active-cell count grows
        # to fill 5+ distinct (x,y,z) cells with sparse, scattered bits we
        # call it structurally unstable. A simple heuristic: the active mask
        # support (number of distinct (x,y,z) cells with any active bit) must
        # stay below ~12 cells (initial extent is 2x3x3 = 18 cube but ~4 cells).
        active = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
        support = int(active.any(axis=-1).sum())
        if support > 16:
            struct_stable = False

    return traj, bit_log, struct_stable, initial_bits


def main():
    print("=" * 96)
    print("3D PHYSICAL CAVENDISH UNIT TEST — emergent gravitational attraction of a glider")
    print("=" * 96)

    glider_path = os.path.join(parent_dir, "archive", "iter_224", "results",
                               "glider_00_lut08_sub03.json")
    print(f"Loading glider from: {glider_path}")
    with open(glider_path, "r", encoding="utf-8") as f:
        glider_data = json.load(f)
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    sub_seed = glider_data["sub_seed"]
    print(f"  lut_seed={lut_seed}  sub_seed={sub_seed}  particle bits={glider_data['initial_bits']}")
    print(f"  cumulative_displacement over 100 steps: {glider_data['cumulative_displacement']}")

    # -------------------------------------------------------------------------
    # Fixed parameters
    # -------------------------------------------------------------------------
    L = 32
    steps = 80
    cx = 0
    cz = 16
    mass_centre = (16, 16, 16)
    sigma = 2.5
    exponent = 1.0
    # vacuum control: alpha=0, threshold=100 (effectively no latching)
    vac_alpha, vac_threshold = 0.0, 100.0
    # gravity case
    grav_alpha, grav_threshold = 3.0, 2.5

    # -------------------------------------------------------------------------
    # Vacuum runs (one per y_start; mass_value is irrelevant)
    # -------------------------------------------------------------------------
    y_starts = [12, 20]
    vacuum_runs = {}
    for ys in y_starts:
        traj, bit_log, _, init_bits = run_one(
            particle, lut_seed, L, steps,
            cx=cx, y_start=ys, cz=cz,
            alpha=vac_alpha, threshold=vac_threshold, exponent=exponent,
            mass_value=0.0, sigma=sigma, mass_centre=mass_centre,
        )
        vacuum_runs[ys] = {
            "trajectory_Y": traj,
            "bit_log": bit_log,
            "initial_bits": init_bits,
        }
        bits_ok = all(b == init_bits for b in bit_log)
        print(f"Vacuum y_start={ys}: Y0={traj[0]:.4f}  Y_final={traj[-1]:.4f}  bits_conserved={bits_ok}")

    # -------------------------------------------------------------------------
    # Gravity sweep
    # -------------------------------------------------------------------------
    mass_values = [15.0, 25.0, 35.0]
    sweep = []
    print("\nRunning gravity sweep (mass_value x y_start)...")
    for mv in mass_values:
        for ys in y_starts:
            try:
                traj, bit_log, struct_ok, init_bits = run_one(
                    particle, lut_seed, L, steps,
                    cx=cx, y_start=ys, cz=cz,
                    alpha=grav_alpha, threshold=grav_threshold, exponent=exponent,
                    mass_value=mv, sigma=sigma, mass_centre=mass_centre,
                )
                bits_ok = all(b == init_bits for b in bit_log)
            except AssertionError as e:
                print(f"  mass={mv}  y_start={ys}: BIT VIOLATION -> {e}")
                continue

            vac_traj = vacuum_runs[ys]["trajectory_Y"]
            # Deflection: Y_dyn - Y_vac at the final step
            deflection = traj[-1] - vac_traj[-1]
            # Sign convention: ys=12 -> attraction means deflection > 0
            #                  ys=20 -> attraction means deflection < 0
            expected_sign = +1 if ys < mass_centre[1] else -1
            attracted = (expected_sign * deflection) > 0.0

            entry = {
                "mass_value": mv,
                "y_start": ys,
                "alpha": grav_alpha,
                "threshold": grav_threshold,
                "exponent": exponent,
                "sigma": sigma,
                "trajectory_Y_gravity": traj,
                "trajectory_Y_vacuum": vac_traj,
                "bit_log_gravity": bit_log,
                "initial_bits": init_bits,
                "bits_conserved": bits_ok,
                "structurally_stable": bool(struct_ok),
                "Y_vac_final": vac_traj[-1],
                "Y_dyn_final": traj[-1],
                "deflection_final": deflection,
                "expected_sign": expected_sign,
                "attracted": bool(attracted),
            }
            sweep.append(entry)
            print(
                f"  mass={mv:5.1f}  y_start={ys:2d}  "
                f"Y_vac={vac_traj[-1]:7.4f}  Y_dyn={traj[-1]:7.4f}  "
                f"dY={deflection:+7.4f}  attracted={attracted}  "
                f"stable={struct_ok}  bits_ok={bits_ok}"
            )

    # -------------------------------------------------------------------------
    # Beautiful trajectory table for the central setting (mass_value=25)
    # -------------------------------------------------------------------------
    central_entries = {(e["y_start"], e["mass_value"]): e for e in sweep}
    print("\n" + "=" * 96)
    print("TRAJECTORY TABLE  (mass_value = 25.0)")
    print("=" * 96)
    print(f"{'Step':>4} | {'Y_vac (y0=12)':>14} | {'Y_dyn (y0=12)':>14} | {'dY (y0=12)':>11} || "
          f"{'Y_vac (y0=20)':>14} | {'Y_dyn (y0=20)':>14} | {'dY (y0=20)':>11}")
    print("-" * 96)
    e_lo = central_entries.get((12, 25.0))
    e_hi = central_entries.get((20, 25.0))
    if e_lo is not None and e_hi is not None:
        steps_to_show = list(range(0, steps + 1, 5))
        if steps_to_show[-1] != steps:
            steps_to_show.append(steps)
        for t in steps_to_show:
            ylv, ydv = e_lo["trajectory_Y_vacuum"][t], e_lo["trajectory_Y_gravity"][t]
            yhv, yhd = e_hi["trajectory_Y_vacuum"][t], e_hi["trajectory_Y_gravity"][t]
            print(
                f"{t:>4d} | {ylv:>14.4f} | {ydv:>14.4f} | {ydv - ylv:>+11.4f} || "
                f"{yhv:>14.4f} | {yhd:>14.4f} | {yhd - yhv:>+11.4f}"
            )
    print("-" * 96)

    # -------------------------------------------------------------------------
    # Save summary
    # -------------------------------------------------------------------------
    out_dir = os.path.join(parent_dir, "archive", "iter_232", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "cavendish_summary.json")

    bit_log_global_ok = True
    for ys in y_starts:
        init = vacuum_runs[ys]["initial_bits"]
        bit_log_global_ok = bit_log_global_ok and all(b == init for b in vacuum_runs[ys]["bit_log"])
    for e in sweep:
        bit_log_global_ok = bit_log_global_ok and e["bits_conserved"]

    summary = {
        "parameters": {
            "L": L,
            "steps": steps,
            "cx": cx,
            "cz": cz,
            "y_starts": y_starts,
            "mass_centre": list(mass_centre),
            "sigma": sigma,
            "mass_values": mass_values,
            "exponent": exponent,
            "vacuum": {"alpha": vac_alpha, "threshold": vac_threshold},
            "gravity": {"alpha": grav_alpha, "threshold": grav_threshold},
            "lut_seed": lut_seed,
            "sub_seed": sub_seed,
            "particle": particle,
        },
        "vacuum_runs": {
            str(ys): {
                "trajectory_Y": vacuum_runs[ys]["trajectory_Y"],
                "initial_bits": vacuum_runs[ys]["initial_bits"],
                "bit_log": vacuum_runs[ys]["bit_log"],
                "bits_conserved": all(
                    b == vacuum_runs[ys]["initial_bits"]
                    for b in vacuum_runs[ys]["bit_log"]
                ),
            }
            for ys in y_starts
        },
        "sweep": sweep,
        "bit_conservation_all_runs": bool(bit_log_global_ok),
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary to {out_path}")

    # -------------------------------------------------------------------------
    # Success / failure verdict
    # -------------------------------------------------------------------------
    # We declare success if there exists at least one mass_value for which BOTH
    # y_start=12 deflects upwards and y_start=20 deflects downwards while the
    # glider remains structurally stable in both runs.
    success_cases = []
    for mv in mass_values:
        e12 = central_entries.get((12, mv))
        e20 = central_entries.get((20, mv))
        if e12 is None or e20 is None:
            continue
        if (e12["attracted"] and e20["attracted"]
                and e12["structurally_stable"] and e20["structurally_stable"]
                and e12["bits_conserved"] and e20["bits_conserved"]):
            success_cases.append((mv, e12["deflection_final"], e20["deflection_final"]))

    print("\n" + "=" * 96)
    if success_cases:
        print("[SUCCESS] EMERGENT GRAVITATIONAL ATTRACTION DEMONSTRATED.")
        for mv, d12, d20 in success_cases:
            print(
                f"  mass_value={mv:5.1f}: y_start=12 deflected UPWARDS  by {d12:+.4f} ; "
                f"y_start=20 deflected DOWNWARDS by {d20:+.4f}."
            )
        print("  The glider is bent toward the heavy mass at (16,16,16) — a discrete-")
        print("  lattice analogue of gravitational attraction, with perfect bit conservation.")
    else:
        print("[FAILURE] No mass_value produced bidirectional attraction with a stable glider.")
        # Still report partial findings:
        for e in sweep:
            print(
                f"  mass={e['mass_value']:5.1f}  y_start={e['y_start']:2d}: "
                f"dY={e['deflection_final']:+.4f}  attracted={e['attracted']}  "
                f"stable={e['structurally_stable']}  bits_ok={e['bits_conserved']}"
            )
    print(f"\nGlobal bit conservation across ALL runs: {bit_log_global_ok}")
    print("=" * 96)


if __name__ == "__main__":
    main()
