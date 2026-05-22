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
    
    alpha = 2.0
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
    
    print("Step | Temp Sum | Latch Sum | Max Latency | Sum Latency | Y1 Centroid | Y2 Centroid")
    print("-" * 90)
    for t in range(81):
        n1, n2, idx1, idx2 = partition_split(engine, CY1, CY2)
        y1 = unwrap_y_centroid(idx1[:, 1], CY1, L)
        y2 = unwrap_y_centroid(idx2[:, 1], CY2, L)
        
        t_sum = engine.temporal_grid.sum()
        l_sum = engine.latched_grid.sum()
        max_lat = engine.latency_field.max()
        sum_lat = engine.latency_field.sum()
        
        print(f"{t:4d} | {t_sum:8d} | {l_sum:9d} | {max_lat:11.6f} | {sum_lat:11.6f} | {y1:11.6f} | {y2:11.6f}")
        
        if t < 80:
            engine.step()

if __name__ == "__main__":
    main()
