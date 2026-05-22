#!/usr/bin/env python3
import os
import sys
import json
import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.inspect_sweep_v4 import OptimizedClosedLoopEngine, seed_glider, partition_split, unwrap_y_centroid

def main():
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    
    alpha = 4.0
    threshold = 0.015
    gamma = 0.95
    eta = 5.0
    sigma = 2.5
    
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
    
    for t in range(5):
        # Let's find where active bits are
        active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
        idx = np.argwhere(active_mask)
        
        # Partition into glider 1 and glider 2
        ys = idx[:, 1]
        d1 = np.minimum(np.mod(ys - CY1, L), np.mod(CY1 - ys, L))
        d2 = np.minimum(np.mod(ys - CY2, L), np.mod(CY2 - ys, L))
        g1_idx = idx[d1 <= d2]
        g2_idx = idx[d1 > d2]
        
        print(f"--- Step {t} ---")
        print("Glider 1 active bits and latency field values:")
        for coord in g1_idx:
            x, y, z, ch = coord
            val = engine.latency_field[x, y, z]
            # duration if trapped
            dur = np.round(alpha * val)
            print(f"  Pos: ({x},{y},{z}) Ch {ch:2d} | Latency: {val:.6f} | Alpha*M: {alpha*val:.4f} | round: {dur}")
            
        print("Glider 2 active bits and latency field values:")
        for coord in g2_idx:
            x, y, z, ch = coord
            val = engine.latency_field[x, y, z]
            dur = np.round(alpha * val)
            print(f"  Pos: ({x},{y},{z}) Ch {ch:2d} | Latency: {val:.6f} | Alpha*M: {alpha*val:.4f} | round: {dur}")
            
        engine.step()

if __name__ == "__main__":
    main()
