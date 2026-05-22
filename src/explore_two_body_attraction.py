#!/usr/bin/env python3
"""explore_two_body_attraction.py — Two-Body Cavendish Parameter Sweep.

Closed-loop dynamic latching test: two co-moving 4-bit LUT-08 sub-light gliders
are seeded on a 32x32x32 toroidal grid at (cx=16, cy=13, cz=16) and
(cx=16, cy=19, cz=16). Each glider deposits latency charge that diffuses
according to the local heat-like equation in the ClosedLoopLatchingEngine. We
sweep alpha, threshold, gamma, kappa, eta (cutoff_radius=4 fixed) and look for
the configuration that maximises mutual attraction (defl_Y1 - defl_Y2) while
maintaining perfect (8 bits, 4+4 split) structural stability over 80 steps.

The best configuration is then re-run for 120 steps to verify that the
deflection continues to grow without structural breakdown.
"""

from __future__ import annotations

import os
import sys
import json
import itertools
import time
import gc
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from engine_d4_closed_loop import ClosedLoopLatchingEngine

# Force line-buffered stdout for live progress.
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

_CACHED_LUT: np.ndarray | None = None

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
L = 32
STEPS = 80
LONG_STEPS = 120
CX, CZ = 16, 16
CY1, CY2 = 13, 19
CUTOFF_RADIUS = 4
EXPECTED_TOTAL_BITS = 8
EXPECTED_BITS_PER_GLIDER = 4


def seed_glider(engine: ClosedLoopLatchingEngine,
                cx: int, cy: int, cz: int, particle) -> None:
    for dl, dr, dc, ch in particle:
        engine.temporal_grid[(cx + dl) % engine.L,
                             (cy + dr) % engine.L,
                             (cz + dc) % engine.L,
                             ch] = 1


def total_bits(engine: ClosedLoopLatchingEngine) -> int:
    return int(engine.temporal_grid.sum() + engine.latched_grid.sum())


def partition_split(engine: ClosedLoopLatchingEngine,
                    cy1: int, cy2: int):
    """Return (n1, n2, idx1, idx2) where idx_k is an (n_k, 4) array of active
    (x, y, z, ch) entries assigned to glider k by closest toroidal Y-distance.
    A tie is broken towards glider 1.
    """
    active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
    idx = np.argwhere(active_mask)
    if idx.size == 0:
        return 0, 0, np.empty((0, 4), dtype=int), np.empty((0, 4), dtype=int)
    Ll = engine.L
    ys = idx[:, 1]
    d1 = np.minimum(np.mod(ys - cy1, Ll), np.mod(cy1 - ys, Ll))
    d2 = np.minimum(np.mod(ys - cy2, Ll), np.mod(cy2 - ys, Ll))
    mask1 = d1 <= d2
    return int(mask1.sum()), int((~mask1).sum()), idx[mask1], idx[~mask1]


def unwrap_y_centroid(ys: np.ndarray, cy: int, Ll: int) -> float:
    if ys.size == 0:
        return float("nan")
    unwrapped = cy + np.mod(ys.astype(np.float64) - cy + Ll // 2, Ll) - Ll // 2
    return float(np.mean(unwrapped))


def run_one(particle, lut_seed: int,
            alpha: float, threshold: float, gamma: float,
            kappa: float, eta: float,
            steps: int, record_trajectories: bool = False):
    """Run the two-body simulation; stop immediately on any structural violation."""
    global _CACHED_LUT
    engine = ClosedLoopLatchingEngine(
        L=L,
        gamma=gamma,
        kappa=kappa,
        eta=eta,
        threshold=threshold,
        alpha=alpha,
        cutoff_radius=CUTOFF_RADIUS,
        exponent=1.0,
        lut_seed=lut_seed,
        use_12_channels=True,
    )
    # Reuse cached LUT — the LUT depends only on lut_seed and is otherwise
    # expensive to regenerate (O_h orbit decomposition allocates large helper
    # tables). Generating it once and assigning saves ~hundreds of MB per run.
    if _CACHED_LUT is None:
        _CACHED_LUT = engine.lut
    else:
        engine.lut = _CACHED_LUT
    seed_glider(engine, cx=CX, cy=CY1, cz=CZ, particle=particle)
    seed_glider(engine, cx=CX, cy=CY2, cz=CZ, particle=particle)

    initial = total_bits(engine)
    if initial != EXPECTED_TOTAL_BITS:
        return _failed_result(f"bad initial bits: {initial}")

    n1_0, n2_0, idx1_0, idx2_0 = partition_split(engine, CY1, CY2)
    if n1_0 != EXPECTED_BITS_PER_GLIDER or n2_0 != EXPECTED_BITS_PER_GLIDER:
        return _failed_result(f"bad initial split {n1_0}|{n2_0}")

    traj_Y1, traj_Y2, bits_log, split_log = [], [], [], []

    Y1 = unwrap_y_centroid(idx1_0[:, 1], CY1, L)
    Y2 = unwrap_y_centroid(idx2_0[:, 1], CY2, L)
    if record_trajectories:
        traj_Y1.append(Y1)
        traj_Y2.append(Y2)
        bits_log.append(EXPECTED_TOTAL_BITS)
        split_log.append([n1_0, n2_0])

    stable = True
    fail_reason = ""
    final_Y1, final_Y2 = Y1, Y2
    n_completed = 0

    for t in range(1, steps + 1):
        engine.step()
        b = total_bits(engine)
        if b != EXPECTED_TOTAL_BITS:
            stable = False
            fail_reason = f"bit violation at step {t}: {b}"
            break
        n1, n2, idx1, idx2 = partition_split(engine, CY1, CY2)
        if n1 != EXPECTED_BITS_PER_GLIDER or n2 != EXPECTED_BITS_PER_GLIDER:
            stable = False
            fail_reason = f"split violation at step {t}: {n1}|{n2}"
            break
        Y1 = unwrap_y_centroid(idx1[:, 1], CY1, L)
        Y2 = unwrap_y_centroid(idx2[:, 1], CY2, L)
        final_Y1, final_Y2 = Y1, Y2
        n_completed = t
        if record_trajectories:
            traj_Y1.append(Y1)
            traj_Y2.append(Y2)
            bits_log.append(b)
            split_log.append([n1, n2])

    defl_Y1 = final_Y1 - float(CY1)
    defl_Y2 = final_Y2 - float(CY2)
    mutual = defl_Y1 - defl_Y2

    return {
        "stable": bool(stable),
        "n_steps_completed": n_completed,
        "fail_reason": fail_reason,
        "Y1_final": final_Y1,
        "Y2_final": final_Y2,
        "defl_Y1": defl_Y1,
        "defl_Y2": defl_Y2,
        "mutual_attraction": mutual,
        "trajectory_Y1": traj_Y1,
        "trajectory_Y2": traj_Y2,
        "bits_log": bits_log,
        "split_log": split_log,
    }


def _failed_result(reason: str):
    return {
        "stable": False, "n_steps_completed": 0, "fail_reason": reason,
        "Y1_final": float("nan"), "Y2_final": float("nan"),
        "defl_Y1": float("nan"), "defl_Y2": float("nan"),
        "mutual_attraction": float("nan"),
        "trajectory_Y1": [], "trajectory_Y2": [],
        "bits_log": [], "split_log": [],
    }


def main():
    print("=" * 96)
    print("TWO-BODY CAVENDISH PARAMETER SWEEP — closed-loop mutual gravitational attraction")
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
    print(f"  Glider 1 seed: cx={CX} cy={CY1} cz={CZ}")
    print(f"  Glider 2 seed: cx={CX} cy={CY2} cz={CZ}")
    print(f"  Grid L={L}, steps={STEPS}, cutoff_radius={CUTOFF_RADIUS}")

    alphas = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    thresholds = [0.4, 0.6, 0.8, 1.0, 1.2]
    gammas = [0.05, 0.1, 0.15]
    kappas = [0.02, 0.05, 0.08]
    etas = [0.5, 1.0, 1.5, 2.0]

    total_cfgs = len(alphas) * len(thresholds) * len(gammas) * len(kappas) * len(etas)
    print(f"\nTotal parameter combinations: {total_cfgs}")
    print("-" * 96)

    sweep_results = []
    stable_results = []
    cfg_idx = 0
    t_start = time.time()

    for alpha, threshold, gamma, kappa, eta in itertools.product(
            alphas, thresholds, gammas, kappas, etas):
        cfg_idx += 1
        result = run_one(particle, lut_seed,
                         alpha=alpha, threshold=threshold,
                         gamma=gamma, kappa=kappa, eta=eta,
                         steps=STEPS, record_trajectories=False)
        entry = {
            "alpha": alpha, "threshold": threshold, "gamma": gamma,
            "kappa": kappa, "eta": eta,
            "stable": result["stable"],
            "n_steps_completed": result["n_steps_completed"],
            "fail_reason": result["fail_reason"],
            "Y1_final": result["Y1_final"],
            "Y2_final": result["Y2_final"],
            "defl_Y1": result["defl_Y1"],
            "defl_Y2": result["defl_Y2"],
            "mutual_attraction": result["mutual_attraction"],
        }
        sweep_results.append(entry)
        if result["stable"]:
            stable_results.append(entry)

        if cfg_idx % 30 == 0 or cfg_idx == total_cfgs:
            gc.collect()
            elapsed = time.time() - t_start
            rate = cfg_idx / max(elapsed, 1e-6)
            print(f"  [{cfg_idx:>4d}/{total_cfgs}] elapsed={elapsed:6.1f}s "
                  f"({rate:5.2f} cfg/s)  stable so far: {len(stable_results)}",
                  flush=True)

    print("-" * 96)
    n_stable = len(stable_results)
    print(f"Sweep complete. {n_stable} / {total_cfgs} configurations passed structural stability.")

    best = None
    long_run = None
    if n_stable == 0:
        print("\n[FAILURE] No stable configurations were found in the sweep.")
    else:
        sorted_stable = sorted(stable_results,
                               key=lambda e: e["mutual_attraction"], reverse=True)
        best = sorted_stable[0]
        print("\nBEST CONFIGURATION (maximum mutual_attraction over 80 steps):")
        print(f"  alpha={best['alpha']}, threshold={best['threshold']}, "
              f"gamma={best['gamma']}, kappa={best['kappa']}, eta={best['eta']}")
        print(f"  defl_Y1={best['defl_Y1']:+.4f}  defl_Y2={best['defl_Y2']:+.4f}  "
              f"mutual={best['mutual_attraction']:+.4f}")

        print("\n" + "=" * 100)
        print("TOP 10 STABLE CONFIGURATIONS  (sorted by mutual_attraction, descending)")
        print("=" * 100)
        header = (f"{'rank':>4} | {'alpha':>5} | {'thr':>4} | {'gamma':>5} | "
                  f"{'kappa':>5} | {'eta':>4} || "
                  f"{'Y1_fin':>8} | {'Y2_fin':>8} | "
                  f"{'defl_Y1':>9} | {'defl_Y2':>9} | {'mutual':>9}")
        print(header)
        print("-" * len(header))
        for rank, e in enumerate(sorted_stable[:10], start=1):
            print(f"{rank:>4d} | {e['alpha']:>5.2f} | {e['threshold']:>4.2f} | "
                  f"{e['gamma']:>5.3f} | {e['kappa']:>5.3f} | {e['eta']:>4.2f} || "
                  f"{e['Y1_final']:>8.4f} | {e['Y2_final']:>8.4f} | "
                  f"{e['defl_Y1']:>+9.4f} | {e['defl_Y2']:>+9.4f} | "
                  f"{e['mutual_attraction']:>+9.4f}")
        print("-" * len(header))

        # ----------------------- Long run -----------------------
        print("\n" + "=" * 96)
        print(f"LONG RUN with best config for {LONG_STEPS} steps — sustained-stability check")
        print("=" * 96)
        long_run_raw = run_one(particle, lut_seed,
                               alpha=best["alpha"], threshold=best["threshold"],
                               gamma=best["gamma"], kappa=best["kappa"],
                               eta=best["eta"], steps=LONG_STEPS,
                               record_trajectories=True)
        long_run = {
            "params": {
                "alpha": best["alpha"], "threshold": best["threshold"],
                "gamma": best["gamma"], "kappa": best["kappa"], "eta": best["eta"],
                "cutoff_radius": CUTOFF_RADIUS, "L": L,
                "steps": LONG_STEPS, "cx": CX, "cy1": CY1, "cy2": CY2, "cz": CZ,
            },
            "stable": long_run_raw["stable"],
            "n_steps_completed": long_run_raw["n_steps_completed"],
            "fail_reason": long_run_raw["fail_reason"],
            "Y1_final": long_run_raw["Y1_final"],
            "Y2_final": long_run_raw["Y2_final"],
            "defl_Y1": long_run_raw["defl_Y1"],
            "defl_Y2": long_run_raw["defl_Y2"],
            "mutual_attraction": long_run_raw["mutual_attraction"],
            "trajectory_Y1": long_run_raw["trajectory_Y1"],
            "trajectory_Y2": long_run_raw["trajectory_Y2"],
            "bits_log": long_run_raw["bits_log"],
            "split_log": long_run_raw["split_log"],
        }
        print(f"  stable: {long_run['stable']}  n_steps_completed: {long_run['n_steps_completed']}")
        if long_run["fail_reason"]:
            print(f"  fail_reason: {long_run['fail_reason']}")
        print(f"  Y1_final={long_run['Y1_final']:+.4f}  Y2_final={long_run['Y2_final']:+.4f}")
        print(f"  defl_Y1={long_run['defl_Y1']:+.4f}  defl_Y2={long_run['defl_Y2']:+.4f}")
        print(f"  mutual_attraction (final) = {long_run['mutual_attraction']:+.4f}")

        traj_Y1 = long_run["trajectory_Y1"]
        traj_Y2 = long_run["trajectory_Y2"]
        n_pts = len(traj_Y1)
        if n_pts > 0:
            step_size = max(1, n_pts // 12)
            sample_steps = sorted(set(list(range(0, n_pts, step_size)) + [n_pts - 1]))
            print("\n  Trajectory samples:")
            print(f"  {'step':>5} | {'Y1':>9} | {'Y2':>9} | {'defl_Y1':>9} | {'defl_Y2':>9} | {'mutual':>9}")
            print("  " + "-" * 70)
            for t in sample_steps:
                y1 = traj_Y1[t]
                y2 = traj_Y2[t]
                d1 = y1 - CY1
                d2 = y2 - CY2
                print(f"  {t:>5d} | {y1:>9.4f} | {y2:>9.4f} | "
                      f"{d1:>+9.4f} | {d2:>+9.4f} | {d1 - d2:>+9.4f}")

    # --------------------------- Save summary ---------------------------
    out_dir = os.path.join(parent_dir, "archive", "iter_233", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "closed_loop_attraction.json")

    summary = {
        "meta": {
            "L": L,
            "steps": STEPS,
            "long_steps": LONG_STEPS,
            "cx": CX, "cz": CZ, "cy1": CY1, "cy2": CY2,
            "cutoff_radius": CUTOFF_RADIUS,
            "exponent": 1.0,
            "lut_seed": lut_seed,
            "sub_seed": sub_seed,
            "particle": particle,
            "expected_total_bits": EXPECTED_TOTAL_BITS,
            "expected_bits_per_glider": EXPECTED_BITS_PER_GLIDER,
        },
        "param_grid": {
            "alpha": alphas,
            "threshold": thresholds,
            "gamma": gammas,
            "kappa": kappas,
            "eta": etas,
        },
        "sweep_summary": {
            "total_configurations": total_cfgs,
            "stable_count": n_stable,
        },
        "all_results": sweep_results,
        "stable_results": stable_results,
        "best_configuration": best,
        "long_run": long_run,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary to {out_path}")

    print("\n" + "=" * 96)
    if best is None:
        print("[FAILURE] No stable configuration found in sweep.")
    else:
        verdict_ok = (long_run["stable"] and
                      long_run["mutual_attraction"] > best["mutual_attraction"] - 1e-9 and
                      long_run["mutual_attraction"] > 0.0)
        if verdict_ok:
            print("[SUCCESS] Two-body mutual gravitational attraction demonstrated.")
            print(f"  Stable 80-step config: alpha={best['alpha']}, threshold={best['threshold']}, "
                  f"gamma={best['gamma']}, kappa={best['kappa']}, eta={best['eta']}")
            print(f"  Mutual attraction at 80 steps: {best['mutual_attraction']:+.4f}")
            print(f"  Mutual attraction at {LONG_STEPS} steps: {long_run['mutual_attraction']:+.4f}")
            print("  Both gliders retain perfect 4|4 bit conservation throughout the run.")
        else:
            print("[PARTIAL] Best 80-step config found, but the longer run did not improve.")
            print(f"  80-step mutual attraction: {best['mutual_attraction']:+.4f}")
            print(f"  {LONG_STEPS}-step mutual attraction: {long_run['mutual_attraction']:+.4f}")
            print(f"  long-run stable: {long_run['stable']}  "
                  f"n_steps_completed: {long_run['n_steps_completed']}")
    print("=" * 96)


if __name__ == "__main__":
    main()
