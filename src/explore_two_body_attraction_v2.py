#!/usr/bin/env python3
"""explore_two_body_attraction_v2.py — Refined Two-Body Cavendish Parameter Sweep.

Refined and extended closed-loop dynamic latching test. Two co-moving 4-bit LUT-08
sub-light gliders are seeded on a 32x32x32 toroidal grid at (cx=16, cy=13, cz=16)
and (cx=16, cy=18, cz=16) — initial Y-separation = 5 cells. Each glider deposits
latency charge that diffuses according to the local heat-like equation in the
ClosedLoopLatchingEngine.

For every (alpha, threshold, gamma, kappa, eta) on the 5x4x5x4x5 = 2000-point grid
we run 160 steps and, if the system stays exactly conservative (8 total bits and a
perfect 4|4 Y-partition), compute mutual deflection at step 160:
    deflection = 5.0 - (Y2 - Y1)_final
The best configuration is then re-run for 240 steps and compared against an
eta=0.0 vacuum baseline (no latency deposition) at the same other parameters.
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

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

_CACHED_LUT: np.ndarray | None = None

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
L = 32
STEPS = 160
LONG_STEPS = 240
CX, CZ = 16, 16
CY1, CY2 = 13, 18
INITIAL_SEPARATION = float(CY2 - CY1)  # 5.0
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

    sep_final = final_Y2 - final_Y1
    defl_Y1 = final_Y1 - float(CY1)
    defl_Y2 = final_Y2 - float(CY2)
    deflection = INITIAL_SEPARATION - sep_final  # >0 means net attraction

    return {
        "stable": bool(stable),
        "n_steps_completed": n_completed,
        "fail_reason": fail_reason,
        "Y1_final": final_Y1,
        "Y2_final": final_Y2,
        "separation_final": sep_final,
        "defl_Y1": defl_Y1,
        "defl_Y2": defl_Y2,
        "deflection": deflection,
        "trajectory_Y1": traj_Y1,
        "trajectory_Y2": traj_Y2,
        "bits_log": bits_log,
        "split_log": split_log,
    }


def _failed_result(reason: str):
    return {
        "stable": False, "n_steps_completed": 0, "fail_reason": reason,
        "Y1_final": float("nan"), "Y2_final": float("nan"),
        "separation_final": float("nan"),
        "defl_Y1": float("nan"), "defl_Y2": float("nan"),
        "deflection": float("nan"),
        "trajectory_Y1": [], "trajectory_Y2": [],
        "bits_log": [], "split_log": [],
    }


def main():
    print("=" * 100)
    print("TWO-BODY CAVENDISH PARAMETER SWEEP V2 — refined closed-loop mutual attraction")
    print("=" * 100)

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
    print(f"  Glider 2 seed: cx={CX} cy={CY2} cz={CZ}  (initial separation = {INITIAL_SEPARATION:.1f})")
    print(f"  Grid L={L}, sweep steps={STEPS}, long-run steps={LONG_STEPS}, cutoff_radius={CUTOFF_RADIUS}")

    alphas     = [1.5, 2.0, 2.5, 3.0, 3.5]
    thresholds = [0.3, 0.5, 0.7, 0.9]
    gammas     = [0.01, 0.02, 0.03, 0.05, 0.08]
    kappas     = [0.05, 0.08, 0.12, 0.16]
    etas       = [1.0, 1.5, 2.0, 2.5, 3.0]

    total_cfgs = len(alphas) * len(thresholds) * len(gammas) * len(kappas) * len(etas)
    print(f"\nParameter grid sizes: alpha={len(alphas)} threshold={len(thresholds)} "
          f"gamma={len(gammas)} kappa={len(kappas)} eta={len(etas)}")
    print(f"Total parameter combinations: {total_cfgs}")
    print("-" * 100)

    partial_path = os.path.join(parent_dir, "archive", "iter_233", "results",
                                "closed_loop_attraction_v2.partial.json")
    sweep_results: list = []
    stable_results: list = []
    if os.path.exists(partial_path):
        try:
            with open(partial_path, "r", encoding="utf-8") as f:
                partial = json.load(f)
            if (partial.get("sweep_summary", {}).get("total_configurations") == total_cfgs
                and len(partial.get("all_results", [])) == total_cfgs):
                sweep_results = partial["all_results"]
                stable_results = partial["stable_results"]
                print(f"[RESUME] Loaded sweep from checkpoint: {partial_path}")
                print(f"[RESUME]   {len(stable_results)} / {total_cfgs} stable")
        except Exception as ex:
            print(f"[WARN] Could not load partial checkpoint ({ex}); rerunning sweep.")
            sweep_results, stable_results = [], []

    cfg_idx = 0
    t_start = time.time()

    if not sweep_results:
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
                "separation_final": result["separation_final"],
                "defl_Y1": result["defl_Y1"],
                "defl_Y2": result["defl_Y2"],
                "deflection": result["deflection"],
            }
            sweep_results.append(entry)
            if result["stable"]:
                stable_results.append(entry)

            if cfg_idx % 50 == 0 or cfg_idx == total_cfgs:
                gc.collect()
                elapsed = time.time() - t_start
                rate = cfg_idx / max(elapsed, 1e-6)
                eta_s = (total_cfgs - cfg_idx) / max(rate, 1e-6)
                print(f"  [{cfg_idx:>4d}/{total_cfgs}] elapsed={elapsed:7.1f}s "
                      f"({rate:5.2f} cfg/s)  stable so far: {len(stable_results):>4d}  "
                      f"eta~{eta_s/60.0:5.1f} min",
                      flush=True)

    print("-" * 100)
    n_stable = len(stable_results)
    print(f"Sweep complete. {n_stable} / {total_cfgs} configurations passed structural stability.")

    # Intermediate checkpoint: persist sweep results before long-run / vacuum so a
    # later failure does not destroy ~45 minutes of work.
    out_dir = os.path.join(parent_dir, "archive", "iter_233", "results")
    os.makedirs(out_dir, exist_ok=True)
    checkpoint_path = os.path.join(out_dir, "closed_loop_attraction_v2.partial.json")
    with open(checkpoint_path, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {
                "L": L, "steps": STEPS, "long_steps": LONG_STEPS,
                "cx": CX, "cz": CZ, "cy1": CY1, "cy2": CY2,
                "initial_separation": INITIAL_SEPARATION,
                "cutoff_radius": CUTOFF_RADIUS, "exponent": 1.0,
                "lut_seed": lut_seed, "sub_seed": sub_seed, "particle": particle,
            },
            "param_grid": {
                "alpha": alphas, "threshold": thresholds, "gamma": gammas,
                "kappa": kappas, "eta": etas,
            },
            "sweep_summary": {
                "total_configurations": total_cfgs,
                "stable_count": n_stable,
            },
            "all_results": sweep_results,
            "stable_results": stable_results,
        }, f, indent=2)
    print(f"Checkpoint written: {checkpoint_path}")

    best = None
    long_run = None
    vacuum_run = None
    if n_stable == 0:
        print("\n[FAILURE] No stable configurations were found in the sweep.")
    else:
        sorted_stable = sorted(stable_results,
                               key=lambda e: e["deflection"], reverse=True)
        best = sorted_stable[0]
        print(f"\nBEST CONFIGURATION (maximum deflection over {STEPS} steps):")
        print(f"  alpha={best['alpha']}, threshold={best['threshold']}, "
              f"gamma={best['gamma']}, kappa={best['kappa']}, eta={best['eta']}")
        print(f"  Y1={best['Y1_final']:+.4f}  Y2={best['Y2_final']:+.4f}  "
              f"sep={best['separation_final']:+.4f}  "
              f"deflection={best['deflection']:+.4f}")

        print("\n" + "=" * 110)
        print("TOP 10 STABLE CONFIGURATIONS  (sorted by deflection, descending)")
        print("=" * 110)
        header = (f"{'rank':>4} | {'alpha':>5} | {'thr':>4} | {'gamma':>5} | "
                  f"{'kappa':>5} | {'eta':>4} || "
                  f"{'Y1_fin':>8} | {'Y2_fin':>8} | "
                  f"{'sep_fin':>8} | {'defl':>9}")
        print(header)
        print("-" * len(header))
        for rank, e in enumerate(sorted_stable[:10], start=1):
            print(f"{rank:>4d} | {e['alpha']:>5.2f} | {e['threshold']:>4.2f} | "
                  f"{e['gamma']:>5.3f} | {e['kappa']:>5.3f} | {e['eta']:>4.2f} || "
                  f"{e['Y1_final']:>8.4f} | {e['Y2_final']:>8.4f} | "
                  f"{e['separation_final']:>8.4f} | {e['deflection']:>+9.4f}")
        print("-" * len(header))

        # ----------------------- Long run (with field) -----------------------
        print("\n" + "=" * 100)
        print(f"LONG RUN with best config for {LONG_STEPS} steps — sustained-attraction check")
        print("=" * 100)
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
            "separation_final": long_run_raw["separation_final"],
            "defl_Y1": long_run_raw["defl_Y1"],
            "defl_Y2": long_run_raw["defl_Y2"],
            "deflection": long_run_raw["deflection"],
            "trajectory_Y1": long_run_raw["trajectory_Y1"],
            "trajectory_Y2": long_run_raw["trajectory_Y2"],
            "bits_log": long_run_raw["bits_log"],
            "split_log": long_run_raw["split_log"],
        }
        print(f"  stable: {long_run['stable']}  n_steps_completed: {long_run['n_steps_completed']}")
        if long_run["fail_reason"]:
            print(f"  fail_reason: {long_run['fail_reason']}")
        print(f"  Y1_final={long_run['Y1_final']:+.4f}  Y2_final={long_run['Y2_final']:+.4f}  "
              f"sep_final={long_run['separation_final']:+.4f}  "
              f"deflection={long_run['deflection']:+.4f}")

        # ----------------------- Vacuum baseline (eta=0) -----------------------
        print("\n" + "=" * 100)
        print(f"VACUUM BASELINE  (same params, eta=0.0)  for {LONG_STEPS} steps")
        print("=" * 100)
        vacuum_raw = run_one(particle, lut_seed,
                             alpha=best["alpha"], threshold=best["threshold"],
                             gamma=best["gamma"], kappa=best["kappa"],
                             eta=0.0, steps=LONG_STEPS,
                             record_trajectories=True)
        vacuum_run = {
            "params": {
                "alpha": best["alpha"], "threshold": best["threshold"],
                "gamma": best["gamma"], "kappa": best["kappa"], "eta": 0.0,
                "cutoff_radius": CUTOFF_RADIUS, "L": L,
                "steps": LONG_STEPS, "cx": CX, "cy1": CY1, "cy2": CY2, "cz": CZ,
            },
            "stable": vacuum_raw["stable"],
            "n_steps_completed": vacuum_raw["n_steps_completed"],
            "fail_reason": vacuum_raw["fail_reason"],
            "Y1_final": vacuum_raw["Y1_final"],
            "Y2_final": vacuum_raw["Y2_final"],
            "separation_final": vacuum_raw["separation_final"],
            "defl_Y1": vacuum_raw["defl_Y1"],
            "defl_Y2": vacuum_raw["defl_Y2"],
            "deflection": vacuum_raw["deflection"],
            "trajectory_Y1": vacuum_raw["trajectory_Y1"],
            "trajectory_Y2": vacuum_raw["trajectory_Y2"],
            "bits_log": vacuum_raw["bits_log"],
            "split_log": vacuum_raw["split_log"],
        }
        print(f"  stable: {vacuum_run['stable']}  n_steps_completed: {vacuum_run['n_steps_completed']}")
        if vacuum_run["fail_reason"]:
            print(f"  fail_reason: {vacuum_run['fail_reason']}")
        print(f"  Y1_final={vacuum_run['Y1_final']:+.4f}  Y2_final={vacuum_run['Y2_final']:+.4f}  "
              f"sep_final={vacuum_run['separation_final']:+.4f}  "
              f"deflection={vacuum_run['deflection']:+.4f}")

        # ----------------------- Beautiful comparison table -----------------------
        print("\n" + "=" * 110)
        print("SIDE-BY-SIDE TRAJECTORY  best-config (eta>0)  vs  vacuum baseline (eta=0.0)")
        print("=" * 110)

        traj_Y1_b = long_run["trajectory_Y1"]
        traj_Y2_b = long_run["trajectory_Y2"]
        traj_Y1_v = vacuum_run["trajectory_Y1"]
        traj_Y2_v = vacuum_run["trajectory_Y2"]
        n_pts = min(len(traj_Y1_b), len(traj_Y1_v))

        if n_pts > 0:
            sample_steps = sorted(set(
                [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, n_pts - 1]
            ))
            sample_steps = [s for s in sample_steps if 0 <= s < n_pts]

            hdr = (f"{'step':>5} ||"
                   f" {'b_Y1':>8} {'b_Y2':>8} {'b_sep':>8} {'b_defl':>9} ||"
                   f" {'v_Y1':>8} {'v_Y2':>8} {'v_sep':>8} {'v_defl':>9} ||"
                   f" {'d_defl':>10}")
            print(hdr)
            print("-" * len(hdr))
            for t in sample_steps:
                y1b = traj_Y1_b[t]; y2b = traj_Y2_b[t]
                y1v = traj_Y1_v[t]; y2v = traj_Y2_v[t]
                sb = y2b - y1b; sv = y2v - y1v
                db = INITIAL_SEPARATION - sb
                dv = INITIAL_SEPARATION - sv
                print(f"{t:>5d} ||"
                      f" {y1b:>8.4f} {y2b:>8.4f} {sb:>8.4f} {db:>+9.4f} ||"
                      f" {y1v:>8.4f} {y2v:>8.4f} {sv:>8.4f} {dv:>+9.4f} ||"
                      f" {db - dv:>+10.4f}")
            print("-" * len(hdr))

        # ----------------------- step 160 vs step 240 check -----------------------
        print("\n" + "=" * 100)
        print("ATTRACTION-PERSISTENCE CHECK  (step 160 vs step 240, best config)")
        print("=" * 100)
        steps_to_compare = [STEPS, LONG_STEPS]
        n_traj = len(traj_Y1_b)
        sep_t160 = None
        sep_t240 = None
        if n_traj > STEPS:
            sep_t160 = traj_Y2_b[STEPS] - traj_Y1_b[STEPS]
        if n_traj > LONG_STEPS:
            sep_t240 = traj_Y2_b[LONG_STEPS] - traj_Y1_b[LONG_STEPS]

        print(f"  separation at step {STEPS}:        {sep_t160 if sep_t160 is None else f'{sep_t160:+.4f}'}")
        print(f"  separation at step {LONG_STEPS}:        {sep_t240 if sep_t240 is None else f'{sep_t240:+.4f}'}")
        if sep_t160 is not None and sep_t240 is not None:
            defl_160 = INITIAL_SEPARATION - sep_t160
            defl_240 = INITIAL_SEPARATION - sep_t240
            print(f"  deflection at step {STEPS}:        {defl_160:+.4f}")
            print(f"  deflection at step {LONG_STEPS}:        {defl_240:+.4f}")
            print(f"  Δ deflection  ({LONG_STEPS} − {STEPS}):  {defl_240 - defl_160:+.4f}  "
                  f"(positive = attraction continues to grow)")
        else:
            print("  (insufficient trajectory length — long run was unstable)")

    # --------------------------- Save summary ---------------------------
    out_dir = os.path.join(parent_dir, "archive", "iter_233", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "closed_loop_attraction_v2.json")

    summary = {
        "meta": {
            "L": L,
            "steps": STEPS,
            "long_steps": LONG_STEPS,
            "cx": CX, "cz": CZ, "cy1": CY1, "cy2": CY2,
            "initial_separation": INITIAL_SEPARATION,
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
        "vacuum_baseline": vacuum_run,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved summary to {out_path}")

    print("\n" + "=" * 100)
    if best is None:
        print("[FAILURE] No stable configuration found in sweep.")
    else:
        long_ok = bool(long_run["stable"])
        vac_ok  = bool(vacuum_run["stable"])
        b_defl160 = best["deflection"]
        b_defl240 = long_run["deflection"]
        v_defl240 = vacuum_run["deflection"]
        attraction_grows = (b_defl240 > b_defl160 - 1e-9) and long_ok
        attraction_above_vacuum = (b_defl240 > v_defl240 + 1e-9)

        if attraction_grows and attraction_above_vacuum:
            print("[SUCCESS] Two-body mutual gravitational attraction demonstrated.")
        else:
            print("[PARTIAL] Best config found, but attraction did not grow/exceed vacuum.")
        print(f"  Best params: alpha={best['alpha']}, threshold={best['threshold']}, "
              f"gamma={best['gamma']}, kappa={best['kappa']}, eta={best['eta']}")
        print(f"  Deflection at step {STEPS}:        {b_defl160:+.4f}")
        print(f"  Deflection at step {LONG_STEPS} (long-run):  {b_defl240:+.4f}  (stable={long_ok})")
        print(f"  Deflection at step {LONG_STEPS} (vacuum):    {v_defl240:+.4f}  (stable={vac_ok})")
        print(f"  Excess over vacuum:            {b_defl240 - v_defl240:+.4f}")
        print(f"  Attraction continues to grow:  {attraction_grows}")
    print("=" * 100)


if __name__ == "__main__":
    main()
