Write a python script `src/simulate_time_dilation.py` that loads glider 2 from `archive/iter_224/results/glider_02_lut21_sub01.json` and runs two parallel 30-step simulations (one in Vacuum, one with a Gaussian Gravitational potential well at l=16 along the z-axis).
The script should unwrap the z-coordinate of the center of mass (the layer dimension, axis 0), calculate the local latency (latency = 1.0 + U(l)), and track physical proper time T.
Write the script to `src/simulate_time_dilation.py`, execute it, and print the results as a compact Markdown table. Save a JSON report to `archive/iter_224/results/time_dilation_report.json`.

Here is the exact code to write and run:
```python
import json
import os
import sys
import numpy as np

# Load glider 2
glider_path = 'archive/iter_224/results/glider_02_lut21_sub01.json'
with open(glider_path) as f:
    glider_data = json.load(f)

lut = np.array(glider_data['lut'], dtype=np.uint16)
particle = glider_data['particle']

# Add src to python path
sys.path.insert(0, os.path.abspath('src'))
from engine_3d import stream, collide

L, H, W = 32, 16, 16

def run_simulation(with_gravity=False):
    grid = np.zeros((L, H, W, 12), dtype=np.uint8)
    l0, r0, c0 = 0, 8, 8
    for dl, dr, dc, ch in particle:
        grid[(l0 + dl) % L, (r0 + dr) % H, (c0 + dc) % W, ch] = 1
        
    unwrapped_l = 0.0
    prev_wrapped_l = 0.0
    T = 0.0
    history = []
    
    for t in range(31):
        occupied = grid.sum(axis=-1) > 0
        ls, rs, cs = np.where(occupied)
        if len(ls) > 0:
            wrapped_l = float(np.mean(ls))
        else:
            wrapped_l = prev_wrapped_l
            
        if t == 0:
            unwrapped_l = wrapped_l
        else:
            diff = wrapped_l - prev_wrapped_l
            if diff > L / 2:
                diff -= L
            elif diff < -L / 2:
                diff += L
            unwrapped_l += diff
            
        dist_l = min(abs(wrapped_l - 16.0), L - abs(wrapped_l - 16.0))
        U = 2.0 * np.exp(- (dist_l**2) / (2.0 * 3.0**2))
        step_latency = 1.0 + U if with_gravity else 1.0
        
        if t > 0:
            T += step_latency
            
        history.append({
            'step': t,
            'wrapped_l': wrapped_l,
            'unwrapped_l': unwrapped_l,
            'physical_time': T,
            'latency': step_latency
        })
        
        prev_wrapped_l = wrapped_l
        grid = stream(grid)
        grid = collide(grid, lut)
        
    return history

vac_hist = run_simulation(with_gravity=False)
grav_hist = run_simulation(with_gravity=True)

# Print markdown table
print("| Step | Vac unwrapped L | Vac Phys Time | Grav unwrapped L | Grav Phys Time | Local Latency | Time Dilation (Grav/Vac) |")
print("|------|-----------------|---------------|------------------|----------------|---------------|--------------------------|")
for v, g in zip(vac_hist, grav_hist):
    step = v['step']
    dil = g['physical_time'] / v['physical_time'] if v['physical_time'] > 0 else 1.0
    print(f"| {step:4d} | {v['unwrapped_l']:15.3f} | {v['physical_time']:13.3f} | {g['unwrapped_l']:16.3f} | {g['physical_time']:14.3f} | {g['latency']:13.3f} | {dil:24.3f} |")

# Save report
report_data = {
    'vacuum': vac_hist,
    'gravitational_well': grav_hist,
    'total_delay_steps': grav_hist[-1]['physical_time'] - vac_hist[-1]['physical_time'],
    'max_dilation_factor': max(g['latency'] for g in grav_hist)
}

os.makedirs('archive/iter_224/results', exist_ok=True)
with open('archive/iter_224/results/time_dilation_report.json', 'w') as f:
    json.dump(report_data, f, indent=2)
print("\nReport saved successfully.")
```