#!/usr/bin/env python3
"""Temporary script to inspect sweep results at step 80."""

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

class OptimizedClosedLoopEngine(ClosedLoopLatchingEngine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        L = self.L
        k = np.fft.fftfreq(L)
        KX, KY, KZ = np.meshgrid(k, k, k, indexing="ij")
        K_sq = KX**2 + KY**2 + KZ**2
        self._H = np.exp(-2.0 * (np.pi * self.sigma)**2 * K_sq)

    def gaussian_blur_3d_fft(self, field: np.ndarray, sigma: float) -> np.ndarray:
        field_fft = np.fft.fftn(field)
        return np.real(np.fft.ifftn(field_fft * self._H))

def seed_glider(engine: ClosedLoopLatchingEngine, cx: int, cy: int, cz: int, particle: list) -> None:
    L = engine.L
    for dl, dr, dc, ch in particle:
        engine.temporal_grid[(cx + dl) % L, (cy + dr) % L, (cz + dc) % L, ch] = 1

def partition_split(engine: ClosedLoopLatchingEngine, cy1: int, cy2: int) -> tuple[int, int, np.ndarray, np.ndarray]:
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
    L = 32
    CY1 = 13
    CY2 = 19
    
    engine = OptimizedClosedLoopEngine(
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
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    
    # Sweep Parameters
    alphas = [1.0, 2.0, 3.0, 4.0]
    thresholds = [0.015, 0.025, 0.035, 0.045, 0.055, 0.065]
    gammas = [0.90, 0.95]
    etas = [1.0, 2.0, 3.0, 4.0, 5.0]
    sigma = 2.5
    
    sweep_results = []
    combinations = list(itertools.product(alphas, thresholds, gammas, etas))
    print(f"Running sweep over {len(combinations)} configurations...")
    
    t0 = time.time()
    for alpha, threshold, gamma, eta in combinations:
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
        sweep_results.append({
            "alpha": alpha,
            "threshold": threshold,
            "gamma": gamma,
            "eta": eta,
            "stable": res["stable"],
            "fail_reason": res["fail_reason"],
            "deflection": res["deflection"]
        })
    print(f"Sweep took {time.time() - t0:.2f} seconds.")
    
    stable = [r for r in sweep_results if r["stable"]]
    print(f"Total stable: {len(stable)}")
    
    print("\nTop 30 sorted by deflection at step 80:")
    for r in sorted(stable, key=lambda x: x["deflection"], reverse=True)[:30]:
        print(f"alpha={r['alpha']}, thresh={r['threshold']:.3f}, gamma={r['gamma']:.2f}, eta={r['eta']:.2f} -> deflection={r['deflection']:.6f}")

if __name__ == "__main__":
    main()
