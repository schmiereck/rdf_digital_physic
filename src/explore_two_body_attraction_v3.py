#!/usr/bin/env python3
"""explore_two_body_attraction_v3.py

This script runs a compact parameter sweep over the new closed-loop cellular automaton engine.
It loads the stable 3D glider from `archive/iter_224/results/glider_00_lut08_sub03.json`,
seeds two gliders at Y=13 and Y=19 on a 32x32x32 toroidal grid, and sweeps through parameters:
  - alpha: [2.0, 2.5, 3.0]
  - threshold: [0.1, 0.2, 0.4]
  - gamma: [0.90, 0.95]
  - eta: [0.5, 1.0, 1.5, 2.0]
  - sigma: 2.5 (fixed)

Stable configurations are evaluated, and the highest mutual deflection is identified.
The best configuration is validated for 120 steps to ensure sustained attraction.
"""

from __future__ import annotations

import os
import sys
import json
import time
import numpy as np
import itertools

# Adjust sys.path to ensure we can import engine_d4_closed_loop_v2
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.engine_d4_closed_loop_v2 import ClosedLoopLatchingEngine

def seed_glider(engine: ClosedLoopLatchingEngine, cx: int, cy: int, cz: int, particle: list) -> None:
    """Seed glider on the temporal grid."""
    L = engine.L
    for dl, dr, dc, ch in particle:
        engine.temporal_grid[(cx + dl) % L, (cy + dr) % L, (cz + dc) % L, ch] = 1

def partition_split(engine: ClosedLoopLatchingEngine, cy1: int, cy2: int) -> tuple[int, int, np.ndarray, np.ndarray]:
    """Assign active cells to glider 1 or glider 2 using nearest toroidal Y-distance."""
    active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
    idx = np.argwhere(active_mask)
    if idx.size == 0:
        return 0, 0, np.empty((0, 4), dtype=int), np.empty((0, 4), dtype=int)
    L = engine.L
    ys = idx[:, 1]
    d1 = np.minimum(np.mod(ys - cy1, L), np.mod(cy1 - ys, L))
    d2 = np.minimum(np.mod(ys - cy2, L), np.mod(cy2 - ys, L))
    mask1 = d1 <= d2
    return int(mask1.sum()), int((~mask1).sum()), idx[mask1], idx[~mask1]

def unwrap_y_centroid(ys: np.ndarray, cy: int, L: int) -> float:
    """Unwrap Y coordinates relative to anchor cy to compute continuous/unwrapped centroid."""
    if ys.size == 0:
        return float("nan")
    unwrapped = cy + np.mod(ys.astype(np.float64) - cy + L // 2, L) - L // 2
    return float(np.mean(unwrapped))

def run_simulation(
    particle: list,
    lut_seed: int,
    alpha: float,
    threshold: float,
    gamma: float,
    eta: float,
    sigma: float,
    steps: int = 80
) -> dict:
    """Runs a 3D toroidal simulation of two gliders and returns metrics, or stable=False if breakup occurs."""
    L = 32
    CY1 = 13
    CY2 = 19
    
    engine = ClosedLoopLatchingEngine(
        L=L,
        gamma=gamma,
        eta=eta,
        threshold=threshold,
        alpha=alpha,
        sigma=sigma,
        lut_seed=lut_seed,
        use_12_channels=True
    )
    
    seed_glider(engine, 16, CY1, 16, particle)
    seed_glider(engine, 16, CY2, 16, particle)
    
    traj_Y1 = []
    traj_Y2 = []
    
    # Step 0 metrics
    n1, n2, idx1, idx2 = partition_split(engine, CY1, CY2)
    Y1 = unwrap_y_centroid(idx1[:, 1], CY1, L)
    Y2 = unwrap_y_centroid(idx2[:, 1], CY2, L)
    traj_Y1.append(Y1)
    traj_Y2.append(Y2)
    
    stable = True
    fail_reason = ""
    
    for t in range(1, steps + 1):
        engine.step()
        
        # 1. Total bit conservation check
        total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
        if total_bits != 8:
            stable = False
            fail_reason = f"bit violation at step {t}: total_bits={total_bits}"
            break
            
        # 2. Partition and support checks
        n1, n2, idx1, idx2 = partition_split(engine, CY1, CY2)
        if n1 == 0 or n2 == 0:
            stable = False
            fail_reason = f"glider vanished at step {t} (n1={n1}, n2={n2})"
            break
            
        g1_cells = set(tuple(p[:3]) for p in idx1)
        g2_cells = set(tuple(p[:3]) for p in idx2)
        total_cells = set(tuple(p[:3]) for p in np.argwhere((engine.temporal_grid == 1) | (engine.latched_grid == 1)))
        
        # Breakup constraints: support of active cells > 16 cells per glider or total support > 32 cells
        if len(g1_cells) > 16:
            stable = False
            fail_reason = f"glider 1 breakup at step {t}: support={len(g1_cells)}"
            break
        if len(g2_cells) > 16:
            stable = False
            fail_reason = f"glider 2 breakup at step {t}: support={len(g2_cells)}"
            break
        if len(total_cells) > 32:
            stable = False
            fail_reason = f"total grid breakup at step {t}: total_support={len(total_cells)}"
            break
            
        # Track centroids
        Y1 = unwrap_y_centroid(idx1[:, 1], CY1, L)
        Y2 = unwrap_y_centroid(idx2[:, 1], CY2, L)
        traj_Y1.append(Y1)
        traj_Y2.append(Y2)
        
    if not stable:
        return {
            "stable": False,
            "fail_reason": fail_reason,
            "traj_Y1": [],
            "traj_Y2": [],
            "deflection": 0.0,
            "final_separation": 6.0
        }
        
    initial_sep = traj_Y2[0] - traj_Y1[0]
    final_sep = traj_Y2[-1] - traj_Y1[-1]
    deflection = initial_sep - final_sep
    
    return {
        "stable": True,
        "fail_reason": "",
        "traj_Y1": traj_Y1,
        "traj_Y2": traj_Y2,
        "deflection": deflection,
        "final_separation": final_sep
    }

def main():
    print("="*80)
    print("CLOSED-LOOP TWO-BODY ATTRACTION SWEEP V3")
    print("="*80)
    
    # Load Glider Configuration
    glider_path = os.path.join(parent_dir, "archive", "iter_224", "results", "glider_00_lut08_sub03.json")
    if not os.path.exists(glider_path):
        glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
        
    print(f"Loading glider config from: {glider_path}")
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
        
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    
    # Sweep Grid Parameters
    alphas = [2.0, 2.5, 3.0]
    thresholds = [0.1, 0.2, 0.4]
    gammas = [0.90, 0.95]
    etas = [0.5, 1.0, 1.5, 2.0]
    sigma = 2.5  # Fixed
    
    sweep_results = []
    stable_count = 0
    total_count = 0
    
    t0 = time.time()
    
    # Generate all combinations
    combinations = list(itertools.product(alphas, thresholds, gammas, etas))
    print(f"Running compact parameter sweep with {len(combinations)} configurations...")
    
    for alpha, threshold, gamma, eta in combinations:
        total_count += 1
        res = run_simulation(
            particle=particle,
            lut_seed=lut_seed,
            alpha=alpha,
            threshold=threshold,
            gamma=gamma,
            eta=eta,
            sigma=sigma,
            steps=80
        )
        
        entry = {
            "alpha": alpha,
            "threshold": threshold,
            "gamma": gamma,
            "eta": eta,
            "sigma": sigma,
            "stable": res["stable"],
            "fail_reason": res["fail_reason"],
            "deflection": res["deflection"],
            "final_separation": res["final_separation"]
        }
        sweep_results.append(entry)
        if res["stable"]:
            stable_count += 1
            
    elapsed = time.time() - t0
    print(f"Sweep complete in {elapsed:.2f} seconds. Stable configurations: {stable_count} / {total_count}")
    
    # Filter stable configurations and sort by highest deflection
    stable_cfgs = [c for c in sweep_results if c["stable"]]
    stable_cfgs_sorted = sorted(stable_cfgs, key=lambda x: x["deflection"], reverse=True)
    
    print("\nTOP 10 STABLE PARAMETER CONFIGURATIONS AT STEP 80:")
    print("-" * 75)
    print(f"{'Rank':^5} | {'Alpha':^6} | {'Thresh':^6} | {'Gamma':^6} | {'Eta':^5} | {'Deflection':^12} | {'Final Sep':^10}")
    print("-" * 75)
    for rank, cfg in enumerate(stable_cfgs_sorted[:10], 1):
        print(f"{rank:^5d} | {cfg['alpha']:^6.2f} | {cfg['threshold']:^6.2f} | {cfg['gamma']:^6.2f} | {cfg['eta']:^5.2f} | {cfg['deflection']:^12.6f} | {cfg['final_separation']:^10.4f}")
    print("-" * 75)
    
    if not stable_cfgs_sorted:
        print("[ERROR] No stable configurations found in the sweep!")
        sys.exit(1)
        
    best_cfg = stable_cfgs_sorted[0]
    print(f"\nAbsolute Best Configuration: alpha={best_cfg['alpha']}, threshold={best_cfg['threshold']}, gamma={best_cfg['gamma']}, eta={best_cfg['eta']}, deflection={best_cfg['deflection']:.6f}")
    
    # Perform longer validation (120 steps) on the best configuration
    print("\nRunning longer validation (120 steps) to confirm non-transient growing attraction...")
    val_res = run_simulation(
        particle=particle,
        lut_seed=lut_seed,
        alpha=best_cfg["alpha"],
        threshold=best_cfg["threshold"],
        gamma=best_cfg["gamma"],
        eta=best_cfg["eta"],
        sigma=sigma,
        steps=120
    )
    
    if not val_res["stable"]:
        print(f"[WARNING] Best configuration was unstable in the long validation run! Reason: {val_res['fail_reason']}")
        # Fallback to next stable configuration
        print("Trying runner-up stable configurations...")
        for runner_up in stable_cfgs_sorted[1:]:
            val_res = run_simulation(
                particle=particle,
                lut_seed=lut_seed,
                alpha=runner_up["alpha"],
                threshold=runner_up["threshold"],
                gamma=runner_up["gamma"],
                eta=runner_up["eta"],
                sigma=sigma,
                steps=120
            )
            if val_res["stable"]:
                best_cfg = runner_up
                print(f"Selected runner-up: alpha={best_cfg['alpha']}, threshold={best_cfg['threshold']}, gamma={best_cfg['gamma']}, eta={best_cfg['eta']}, deflection={best_cfg['deflection']:.6f}")
                break
                
    if not val_res["stable"]:
        print("[ERROR] No stable configuration is stable up to 120 steps!")
        sys.exit(1)
        
    # Analyze validation trajectory
    traj_Y1 = val_res["traj_Y1"]
    traj_Y2 = val_res["traj_Y2"]
    
    deflection_80 = 6.0 - (traj_Y2[80] - traj_Y1[80])
    deflection_120 = 6.0 - (traj_Y2[120] - traj_Y1[120])
    
    print(f"Deflection at Step 80:  {deflection_80:.6f}")
    print(f"Deflection at Step 120: {deflection_120:.6f}")
    
    growing = deflection_120 > deflection_80
    print(f"Is attraction growing and non-transient? {'YES' if growing else 'NO'}")
    
    # Save the summary of the best sweep results to archive/iter_234/results/v3_sweep_results.json
    out_dir = os.path.join(parent_dir, "archive", "iter_234", "results")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "v3_sweep_results.json")
    
    summary_data = {
        "best_configuration": best_cfg,
        "long_validation": {
            "stable": val_res["stable"],
            "deflection_80": deflection_80,
            "deflection_120": deflection_120,
            "attraction_growing": growing,
            "traj_Y1": traj_Y1,
            "traj_Y2": traj_Y2
        },
        "all_stable_configurations": stable_cfgs_sorted[:10],
        "sweep_statistics": {
            "total_configurations": total_count,
            "stable_configurations": stable_count,
            "elapsed_seconds": elapsed
        }
    }
    
    with open(out_path, "w") as f:
        json.dump(summary_data, f, indent=2)
        
    print(f"\nSaved v3 sweep results summary to: {out_path}")
    print("="*80)

if __name__ == "__main__":
    main()
