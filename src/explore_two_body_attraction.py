#!/usr/bin/env python3
"""
explore_two_body_attraction.py

Systematic parameter exploration for the Two-Body Cavendish Test (Mutual Deflection)
using the ClosedLoopLatchingEngine.
"""

import os
import sys
import json
import time
import multiprocessing
import numpy as np

# Adjust sys.path to ensure we can import engine_d4_closed_loop and search_3d_gliders
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.engine_d4_closed_loop import ClosedLoopLatchingEngine

def seed_gliders(engine: ClosedLoopLatchingEngine, particle: list):
    """Seed two parallel gliders in the grid of size L."""
    L = engine.L
    # Glider 1: Centered at cx=16, cy=13, cz=16
    cx1, cy1, cz1 = 16, 13, 16
    for dx, dy, dz, ch in particle:
        engine.temporal_grid[(cx1 + dx) % L, (cy1 + dy) % L, (cz1 + dz) % L, ch] = 1
    # Glider 2: Centered at cx=16, cy=19, cz=16
    cx2, cy2, cz2 = 16, 19, 16
    for dx, dy, dz, ch in particle:
        engine.temporal_grid[(cx2 + dx) % L, (cy2 + dy) % L, (cz2 + dz) % L, ch] = 1

def compute_single_centroid(cells, L):
    """
    Computes centroid of a single glider with 4 cells, unwrapping relative to cell 0 (the anchor)
    to handle toroidal boundaries.
    """
    anchor = cells[0]
    unwrapped = np.zeros_like(cells, dtype=np.float64)
    for d in range(3):
        unwrapped[:, d] = anchor[d] + np.mod(cells[:, d] - anchor[d] + L//2, L) - L//2
    return np.mean(unwrapped, axis=0)[:3]

def run_simulation(L, params, particle, lut_seed, max_steps=120):
    """
    Runs a single simulation and returns the trajectory, or (False, None) if unstable.
    """
    engine = ClosedLoopLatchingEngine(
        L=L,
        gamma=params['gamma'],
        kappa=params['kappa'],
        eta=params['eta'],
        threshold=params['threshold'],
        alpha=params['alpha'],
        cutoff_radius=params['cutoff_radius'],
        lut_seed=lut_seed,
        use_12_channels=True
    )
    
    seed_gliders(engine, particle)
    
    c1_continuous_history = []
    c2_continuous_history = []
    separation_history = []
    deflection_history = []
    
    # At t=0
    active_indices = np.argwhere((engine.temporal_grid == 1) | (engine.latched_grid == 1))
    if len(active_indices) != 8:
        return False, None
    
    x_vals = active_indices[:, 0]
    y_vals = active_indices[:, 1]
    unwrapped_y = 16.0 + np.mod(y_vals - 16 + L//2, L) - L//2
    
    glider1_indices = active_indices[unwrapped_y < 16.0]
    glider2_indices = active_indices[unwrapped_y >= 16.0]
    
    if len(glider1_indices) != 4 or len(glider2_indices) != 4:
        return False, None
        
    c1_toroidal = compute_single_centroid(glider1_indices, L)
    c2_toroidal = compute_single_centroid(glider2_indices, L)
    
    c1_continuous = c1_toroidal.copy()
    c2_continuous = c2_toroidal.copy()
    
    c1_prev_toroidal = c1_toroidal.copy()
    c2_prev_toroidal = c2_toroidal.copy()
    
    c1_continuous_history.append(c1_continuous.tolist())
    c2_continuous_history.append(c2_continuous.tolist())
    separation_history.append(float(c2_continuous[1] - c1_continuous[1]))
    deflection_history.append(0.0)
    
    for t in range(1, max_steps + 1):
        engine.step()
        
        # Stability check: bit count and active cell count
        total_bits = engine.temporal_grid.sum() + engine.latched_grid.sum()
        if total_bits != 8:
            return False, None
            
        active_indices = np.argwhere((engine.temporal_grid == 1) | (engine.latched_grid == 1))
        if len(active_indices) != 8:
            return False, None
            
        x_vals = active_indices[:, 0]
        y_vals = active_indices[:, 1]
        z_vals = active_indices[:, 2]
        unwrapped_y = 16.0 + np.mod(y_vals - 16 + L//2, L) - L//2
        
        glider1_indices = active_indices[unwrapped_y < 16.0]
        glider2_indices = active_indices[unwrapped_y >= 16.0]
        
        if len(glider1_indices) != 4 or len(glider2_indices) != 4:
            return False, None
            
        c1_toroidal = compute_single_centroid(glider1_indices, L)
        c2_toroidal = compute_single_centroid(glider2_indices, L)
        
        # Unwrap centroids over time
        step_change_1 = np.mod(c1_toroidal - c1_prev_toroidal + L//2, L) - L//2
        step_change_2 = np.mod(c2_toroidal - c2_prev_toroidal + L//2, L) - L//2
        c1_continuous += step_change_1
        c2_continuous += step_change_2
        
        c1_prev_toroidal = c1_toroidal.copy()
        c2_prev_toroidal = c2_toroidal.copy()
        
        separation = float(c2_continuous[1] - c1_continuous[1])
        deflection = float(6.0 - separation)
        
        c1_continuous_history.append(c1_continuous.tolist())
        c2_continuous_history.append(c2_continuous.tolist())
        separation_history.append(separation)
        deflection_history.append(deflection)
        
    trajectory = {
        'c1_continuous_history': c1_continuous_history,
        'c2_continuous_history': c2_continuous_history,
        'separation_history': separation_history,
        'deflection_history': deflection_history
    }
    return True, trajectory

def evaluate_params_task(task_args):
    """Task wrapper for parallel parameter evaluation."""
    params, particle, lut_seed, L, max_steps = task_args
    success, trajectory = run_simulation(L, params, particle, lut_seed, max_steps)
    if not success:
        return False, 0.0, params
    # Achieve maximum mutual deflection (highest value of deflection over 120 steps)
    max_deflection = max(trajectory['deflection_history'])
    return True, max_deflection, params

def main():
    # Load Glider
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
    print(f"Loading stable glider from {glider_path}...")
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
    
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    print(f"Glider Loaded. LUT Seed: {lut_seed}, Initial Bits: {glider_data['initial_bits']}")
    
    L = 32
    max_steps = 120
    
    # Run Vacuum Reference Run (eta = 0.0)
    print("\nRunning Vacuum Reference Run (eta = 0.0)...")
    vacuum_params = {
        'gamma': 0.1,
        'kappa': 0.05,
        'eta': 0.0,
        'threshold': 1.5,
        'alpha': 2.0,
        'cutoff_radius': 4
    }
    success, vacuum_traj = run_simulation(L, vacuum_params, particle, lut_seed, max_steps)
    if not success:
        print("Error: Vacuum run failed or was unstable!")
        sys.exit(1)
    
    vacuum_max_deflection = max(vacuum_traj['deflection_history'])
    print(f"Vacuum Run Succeeded. Max deflection: {vacuum_max_deflection:.6f} (expected exactly 0.0)")
    
    # Define Parameter Grid
    alphas = [1.0, 1.5, 2.0, 3.0]
    thresholds = [0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.5]
    gammas = [0.05, 0.1, 0.15, 0.2]
    kappas = [0.02, 0.05, 0.08, 0.12]
    etas = [0.1, 0.2, 0.5, 1.0, 1.5]
    cutoff_radius = 4
    
    tasks = []
    for alpha in alphas:
        for threshold in thresholds:
            for gamma in gammas:
                for kappa in kappas:
                    for eta in etas:
                        params = {
                            'alpha': alpha,
                            'threshold': threshold,
                            'gamma': gamma,
                            'kappa': kappa,
                            'eta': eta,
                            'cutoff_radius': cutoff_radius
                        }
                        tasks.append((params, particle, lut_seed, L, max_steps))
                        
    total_tasks = len(tasks)
    print(f"\nGenerated parameter grid with {total_tasks} combinations.")
    print("Starting systematic sweep using multiprocessing...")
    
    start_time = time.time()
    best_params = None
    best_max_deflection = -float('inf')
    stable_count = 0
    
    with multiprocessing.Pool() as pool:
        # Use imap_unordered for potential real-time progress logging
        for idx, (success, max_def, params) in enumerate(pool.imap_unordered(evaluate_params_task, tasks, chunksize=10)):
            if success:
                stable_count += 1
                if max_def > best_max_deflection:
                    best_max_deflection = max_def
                    best_params = params
                    print(f"New Best: Deflection = {best_max_deflection:.6f} with {params}")
            
            if (idx + 1) % 200 == 0 or (idx + 1) == total_tasks:
                elapsed = time.time() - start_time
                print(f"Progress: {idx + 1}/{total_tasks} sweeps complete ({elapsed:.1f}s elapsed)...")
                
    elapsed_time = time.time() - start_time
    print(f"\nGrid Sweep Complete in {elapsed_time:.2f} seconds.")
    print(f"Total Stable Configurations: {stable_count} / {total_tasks} ({stable_count/total_tasks*100:.1f}%)")
    
    if best_params is None:
        print("No stable parameter set found during sweep!")
        sys.exit(1)
        
    print(f"Best Parameters: {best_params}")
    print(f"Best Mutual Deflection Achieved: {best_max_deflection:.6f}")
    
    # Detailed Evaluation of the Best Attraction Run
    print("\nRe-running the best parameter set for detailed trajectory collection...")
    success, attraction_traj = run_simulation(L, best_params, particle, lut_seed, max_steps)
    if not success:
        print("Error: Re-running the best parameters failed stability!")
        sys.exit(1)
        
    # Print beautiful summary table at intervals of 10 steps
    print("\n" + "="*95)
    print(f"{'Step':^6} | {'Vacuum Centroid 1':^20} | {'Vacuum Centroid 2':^20} | {'Attr Centroid 1':^20} | {'Attr Centroid 2':^20} | {'Deflection':^10}")
    print("="*95)
    
    for t in range(0, max_steps + 1, 10):
        v_c1 = [round(c, 3) for c in vacuum_traj['c1_continuous_history'][t]]
        v_c2 = [round(c, 3) for c in vacuum_traj['c2_continuous_history'][t]]
        a_c1 = [round(c, 3) for c in attraction_traj['c1_continuous_history'][t]]
        a_c2 = [round(c, 3) for c in attraction_traj['c2_continuous_history'][t]]
        defl = attraction_traj['deflection_history'][t]
        
        print(f"{t:^6d} | {str(v_c1):^20} | {str(v_c2):^20} | {str(a_c1):^20} | {str(a_c2):^20} | {defl:^10.4f}")
        
    print("="*95)
    
    # Create output directory
    out_dir = "archive/iter_233/results/"
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "closed_loop_attraction.json")
    
    # Save the full results to json
    output_data = {
        'vacuum_trajectory': {
            'c1_continuous_history': vacuum_traj['c1_continuous_history'],
            'c2_continuous_history': vacuum_traj['c2_continuous_history'],
            'separation_history': vacuum_traj['separation_history'],
            'deflection_history': vacuum_traj['deflection_history']
        },
        'best_params': best_params,
        'attraction_trajectory': {
            'c1_continuous_history': attraction_traj['c1_continuous_history'],
            'c2_continuous_history': attraction_traj['c2_continuous_history'],
            'separation_history': attraction_traj['separation_history'],
            'deflection_history': attraction_traj['deflection_history']
        },
        'summary': {
            'sweep_time_sec': elapsed_time,
            'total_configurations': total_tasks,
            'stable_configurations': stable_count,
            'best_max_deflection': best_max_deflection,
            'final_deflection': attraction_traj['deflection_history'][-1]
        }
    }
    
    print(f"Saving full results to {out_path}...")
    with open(out_path, "w") as f:
        json.dump(output_data, f, indent=2)
        
    print("\nEXPLORATION COMPLETE!")

if __name__ == "__main__":
    main()
