Create and run the python script `src/run_dynamic_attraction.py` to simulate emergent gravitational attraction between two moving 3D gliders.

The python code for `src/run_dynamic_attraction.py` is provided below. Please write this code to `src/run_dynamic_attraction.py` and run it using `python src/run_dynamic_attraction.py`.

```python
#!/usr/bin/env python3
import os
import sys
import json
import numpy as np

# Adjust sys.path to import our dynamic engine
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.engine_d4_dynamic import DynamicLatchingEngine

def seed_glider(engine, cx, cy, cz, particle):
    for dl, dr, dc, ch in particle:
        engine.temporal_grid[(cx + dl) % engine.L, (cy + cz) % engine.L, (cz + dc) % engine.L, ch] = 1

def get_y_centroid(engine, y_min, y_max):
    # Sum of temporal + latched masks
    active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
    indices = np.argwhere(active_mask)
    if len(indices) == 0:
        return None
    y_vals = []
    for x, y, z, ch in indices:
        if y_min <= y <= y_max:
            y_vals.append(y)
    if len(y_vals) == 0:
        return None
    return float(np.mean(y_vals))

def main():
    print("="*80)
    print("DEMONSTRATING EMERGENT ATTRIBUTION (MUTUAL DEFLECTION) OF TWO 3D GLIDERS")
    print("="*80)
    
    # 1. Load glider config
    glider_path = os.path.join(parent_dir, "archive", "iter_224", "results", "glider_00_lut08_sub03.json")
    if not os.path.exists(glider_path):
        # fallback to local path or raise
        glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
        
    print(f"Loading glider from: {glider_path}")
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
        
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]
    
    L = 32
    steps = 80
    
    # We test two cases:
    # 1. Vacuum (no latching)
    # 2. Dynamic Gravity (alpha = 3.0, threshold = 2.5, exponent = 1.0)
    
    engine_vac = DynamicLatchingEngine(L=L, alpha=0.0, threshold=100.0, exponent=1.0, lut_seed=lut_seed)
    engine_dyn = DynamicLatchingEngine(L=L, alpha=3.0, threshold=2.5, exponent=1.0, lut_seed=lut_seed)
    
    # Seed both with parallel gliders at Y=13 and Y=19
    # This separation of 6 is close enough to overlap when smoothed (smoothing radius = 1)
    # Let's seed them at cx=16, cz=16
    seed_glider(engine_vac, cx=16, cy=13, cz=16, particle=particle)
    seed_glider(engine_vac, cx=16, cy=19, cz=16, particle=particle)
    
    seed_glider(engine_dyn, cx=16, cy=13, cz=16, particle=particle)
    seed_glider(engine_dyn, cx=16, cy=19, cz=16, particle=particle)
    
    initial_bits_vac = int(engine_vac.temporal_grid.sum() + engine_vac.latched_grid.sum())
    initial_bits_dyn = int(engine_dyn.temporal_grid.sum() + engine_dyn.latched_grid.sum())
    print(f"Initial bits vacuum : {initial_bits_vac}")
    print(f"Initial bits dynamic: {initial_bits_dyn}")
    assert initial_bits_vac == 8 and initial_bits_dyn == 8, "Expected 8 total bits!"
    
    # Keep track of trajectories
    trajectories = []
    
    for t in range(steps + 1):
        # Track centroids in Y
        # Glider 1 is in Y range [8, 15]
        # Glider 2 is in Y range [17, 24]
        Y1_vac = get_y_centroid(engine_vac, 8, 15)
        Y2_vac = get_y_centroid(engine_vac, 17, 24)
        
        Y1_dyn = get_y_centroid(engine_dyn, 8, 15)
        Y2_dyn = get_y_centroid(engine_dyn, 17, 24)
        
        if Y1_vac is None or Y2_vac is None or Y1_dyn is None or Y2_dyn is None:
            print(f"Warning: Glider lost at step {t}")
            break
            
        d_vac = Y2_vac - Y1_vac
        d_dyn = Y2_dyn - Y1_dyn
        
        defl_Y1 = Y1_dyn - Y1_vac
        defl_Y2 = Y2_dyn - Y2_vac
        
        trajectories.append({
            "step": t,
            "Y1_vac": Y1_vac,
            "Y2_vac": Y2_vac,
            "d_vac": d_vac,
            "Y1_dyn": Y1_dyn,
            "Y2_dyn": Y2_dyn,
            "d_dyn": d_dyn,
            "defl_Y1": defl_Y1,
            "defl_Y2": defl_Y2
        })
        
        # Verify perfect bit conservation
        current_bits_vac = int(engine_vac.temporal_grid.sum() + engine_vac.latched_grid.sum())
        current_bits_dyn = int(engine_dyn.temporal_grid.sum() + engine_dyn.latched_grid.sum())
        assert current_bits_vac == initial_bits_vac, f"Vacuum bit violation at step {t}"
        assert current_bits_dyn == initial_bits_dyn, f"Dynamic bit violation at step {t}"
        
        if t < steps:
            engine_vac.step()
            engine_dyn.step()
            
    # Print beautiful table
    print("\nTrajectories & Emergent Deflection Table:")
    print("-" * 110)
    print(f"{'Step':^5} | {'Y1 Vac':^8} | {'Y1 Dyn':^8} | {'Defl Y1':^9} | {'Y2 Vac':^8} | {'Y2 Dyn':^8} | {'Defl Y2':^9} | {'Dist Vac':^9} | {'Dist Dyn':^9}")
    print("-" * 110)
    for row in trajectories[::5]: # every 5 steps
        print(f"{row['step']:^5d} | {row['Y1_vac']:^8.4f} | {row['Y1_dyn']:^8.4f} | {row['defl_Y1']:+9.4f} | {row['Y2_vac']:^8.4f} | {row['Y2_dyn']:^8.4f} | {row['defl_Y2']:+9.4f} | {row['d_vac']:^9.4f} | {row['d_dyn']:^9.4f}")
    # Print final step too
    last_row = trajectories[-1]
    if last_row['step'] % 5 != 0:
        print(f"{last_row['step']:^5d} | {last_row['Y1_vac']:^8.4f} | {last_row['Y1_dyn']:^8.4f} | {last_row['defl_Y1']:+9.4f} | {last_row['Y2_vac']:^8.4f} | {last_row['Y2_dyn']:^8.4f} | {last_row['defl_Y2']:+9.4f} | {last_row['d_vac']:^9.4f} | {last_row['d_dyn']:^9.4f}")
    print("-" * 110)
    
    # Save results
    out_dir = os.path.join(parent_dir, "archive", "iter_230", "results")
    os.makedirs(out_dir, exist_ok=True)
    summary_path = os.path.join(out_dir, "attraction_summary.json")
    
    summary = {
        "alpha": 3.0,
        "threshold": 2.5,
        "exponent": 1.0,
        "steps": len(trajectories) - 1,
        "initial_separation": trajectories[0]["d_vac"],
        "final_separation_vacuum": trajectories[-1]["d_vac"],
        "final_separation_dynamic": trajectories[-1]["d_dyn"],
        "final_deflection_Y1": trajectories[-1]["defl_Y1"],
        "final_deflection_Y2": trajectories[-1]["defl_Y2"],
        "separation_reduction": trajectories[0]["d_vac"] - trajectories[-1]["d_dyn"],
        "bit_conservation_vacuum": "perfect",
        "bit_conservation_dynamic": "perfect",
        "trajectories": trajectories
    }
    
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved attraction summary to: {summary_path}")
    
    if summary["final_deflection_Y1"] > 0 and summary["final_deflection_Y2"] < 0:
        print("\n[SUCCESS] Emergent gravitational attraction successfully demonstrated!")
        print(f"          Glider 1 deflected by {summary['final_deflection_Y1']:.4f} units towards Glider 2.")
        print(f"          Glider 2 deflected by {summary['final_deflection_Y2']:.4f} units towards Glider 1.")
        print(f"          Mutual separation reduced from {summary['initial_separation']:.4f} to {summary['final_separation_dynamic']:.4f} units!")
    else:
        print("\n[INFO] Run finished, but no mutual attraction observed. Check parameter alignment.")
        
if __name__ == "__main__":
    main()
```
