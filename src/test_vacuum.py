#!/usr/bin/env python3
import json
import numpy as np
from src.engine_d4_closed_loop import ClosedLoopLatchingEngine

def seed_gliders(engine: ClosedLoopLatchingEngine, particle: list):
    L = engine.L
    # Glider 1
    cx1, cy1, cz1 = 16, 13, 16
    for dx, dy, dz, ch in particle:
        engine.temporal_grid[(cx1 + dx) % L, (cy1 + dy) % L, (cz1 + dz) % L, ch] = 1
    # Glider 2
    cx2, cy2, cz2 = 16, 19, 16
    for dx, dy, dz, ch in particle:
        engine.temporal_grid[(cx2 + dx) % L, (cy2 + dy) % L, (cz2 + dz) % L, ch] = 1

def compute_single_centroid(cells, L):
    anchor = cells[0]
    unwrapped = np.zeros_like(cells, dtype=np.float64)
    for d in range(3):
        unwrapped[:, d] = anchor[d] + np.mod(cells[:, d] - anchor[d] + L//2, L) - L//2
    return np.mean(unwrapped, axis=0)[:3]

def main():
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    
    L = 32
    engine = ClosedLoopLatchingEngine(
        L=L,
        gamma=0.1,
        kappa=0.05,
        eta=0.0,
        threshold=1.5,
        alpha=2.0,
        cutoff_radius=4,
        lut_seed=lut_seed,
        use_12_channels=True
    )
    
    seed_gliders(engine, particle)
    
    # Trace lists
    c1_continuous_history = []
    c2_continuous_history = []
    separation_history = []
    deflection_history = []
    
    # At t=0
    active_indices = np.argwhere((engine.temporal_grid == 1) | (engine.latched_grid == 1))
    x_vals = active_indices[:, 0]
    y_vals = active_indices[:, 1]
    unwrapped_y = 16.0 + np.mod(y_vals - 16 + L//2, L) - L//2
    
    glider1_indices = active_indices[unwrapped_y < 16.0]
    glider2_indices = active_indices[unwrapped_y >= 16.0]
    
    c1_toroidal = compute_single_centroid(glider1_indices, L)
    c2_toroidal = compute_single_centroid(glider2_indices, L)
    
    c1_continuous = c1_toroidal.copy()
    c2_continuous = c2_toroidal.copy()
    
    c1_prev_toroidal = c1_toroidal.copy()
    c2_prev_toroidal = c2_toroidal.copy()
    
    c1_continuous_history.append(c1_continuous.tolist())
    c2_continuous_history.append(c2_continuous.tolist())
    separation_history.append(c2_continuous[1] - c1_continuous[1])
    deflection_history.append(0.0)
    
    for t in range(1, 121):
        engine.step()
        
        # Stability check
        total_bits = engine.temporal_grid.sum() + engine.latched_grid.sum()
        if total_bits != 8:
            print(f"Step {t}: Failed bit count stability check ({total_bits})")
            return
            
        active_indices = np.argwhere((engine.temporal_grid == 1) | (engine.latched_grid == 1))
        if len(active_indices) != 8:
            print(f"Step {t}: Failed active cells stability check ({len(active_indices)})")
            return
            
        x_vals = active_indices[:, 0]
        y_vals = active_indices[:, 1]
        z_vals = active_indices[:, 2]
        unwrapped_y = 16.0 + np.mod(y_vals - 16 + L//2, L) - L//2
        
        glider1_indices = active_indices[unwrapped_y < 16.0]
        glider2_indices = active_indices[unwrapped_y >= 16.0]
        
        if len(glider1_indices) != 4 or len(glider2_indices) != 4:
            print(f"Step {t}: Failed partition stability check (G1: {len(glider1_indices)}, G2: {len(glider2_indices)})")
            return
            
        c1_toroidal = compute_single_centroid(glider1_indices, L)
        c2_toroidal = compute_single_centroid(glider2_indices, L)
        
        # Unwrap centroids over time
        step_change_1 = np.mod(c1_toroidal - c1_prev_toroidal + L//2, L) - L//2
        step_change_2 = np.mod(c2_toroidal - c2_prev_toroidal + L//2, L) - L//2
        c1_continuous += step_change_1
        c2_continuous += step_change_2
        
        # Update prev centroids
        c1_prev_toroidal = c1_toroidal.copy()
        c2_prev_toroidal = c2_toroidal.copy()
        
        separation = c2_continuous[1] - c1_continuous[1]
        deflection = 6.0 - separation
        
        c1_continuous_history.append(c1_continuous.tolist())
        c2_continuous_history.append(c2_continuous.tolist())
        separation_history.append(separation)
        deflection_history.append(deflection)
        
    print("Simulated 120 steps successfully!")
    print(f"Step 120 continuous centroid 1: {c1_continuous_history[-1]}")
    print(f"Step 120 continuous centroid 2: {c2_continuous_history[-1]}")
    print(f"Step 120 separation: {separation_history[-1]}, deflection: {deflection_history[-1]}")

if __name__ == "__main__":
    main()
