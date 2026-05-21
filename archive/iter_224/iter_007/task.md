Modify `src/simulate_time_dilation.py` so that the Gaussian potential well is defined along the **c-axis** (axis 2, column index) centered at c = 8.0 (with sigma = 2.0 and amplitude A = 2.0), because glider 2 travels along the c-axis in the negative direction.
The script should unwrap the c-coordinate of the center of mass, calculate the local latency as a function of the wrapped c-coordinate:
`dist_c = min(abs(wrapped_c - 8.0), W - abs(wrapped_c - 8.0))`
`U(c) = A * np.exp(- dist_c**2 / (2.0 * sigma**2))`
`latency(c) = 1.0 + U(c)`
Track physical proper time T. Run the simulations for 30 steps.
Print a compact Markdown table showing step t, wrapped and unwrapped c, physical time, latency, and coordinate velocity (dc/dT) for both Vacuum and Gravity.
Execute the script and output the results. Save the JSON report to `archive/iter_224/results/time_dilation_report.json`.

Here is the code to write to `src/simulate_time_dilation.py` and execute:
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

sys.path.insert(0, os.path.abspath('src'))
from engine_3d import stream, collide

L, H, W = 16, 16, 16

def run_simulation(with_gravity=False):
    grid = np.zeros((L, H, W, 12), dtype=np.uint8)
    l0, r0, c0 = 8, 8, 8
    for dl, dr, dc, ch in particle:
        grid[(l0 + dl) % L, (r0 + dr) % H, (c0 + dc) % W, ch] = 1
        
    unwrapped_c = 0.0
    prev_wrapped_c = 0.0
    T = 0.0
    history = []
    
    for t in range(31):
        occupied = grid.sum(axis=-1) > 0
        ls, rs, cs = np.where(occupied)
        if len(cs) > 0:
            wrapped_c = float(np.mean(cs))
        else:
            wrapped_c = prev_wrapped_c
            
        if t == 0:
            unwrapped_c = wrapped_c
        else:
            diff = wrapped_c - prev_wrapped_c
            if diff > W / 2:
                diff -= W
            elif diff < -W / 2:
                diff += W
            unwrapped_c += diff
            
        dist_c = min(abs(wrapped_c - 8.0), W - abs(wrapped_c - 8.0))
        U = 2.0 * np.exp(- (dist_c**2) / (2.0 * 2.0**2))
        step_latency = 1.0 + U if with_gravity else 1.0
        
        if t > 0:
            T += step_latency
            
        history.append({
            'step': t,
            'wrapped_c': wrapped_c,
            'unwrapped_c': unwrapped_c,
            'physical_time': T,
            'latency': step_latency
        })
        
        prev_wrapped_c = wrapped_c
        grid = stream(grid)
        grid = collide(grid, lut)
        
    return history

vac_hist = run_simulation(with_gravity=False)
grav_hist = run_simulation(with_gravity=True)

# Print markdown table
print("| Step | Vac unwrapped C | Vac Phys Time | Vac Vel (C/T) | Grav unwrapped C | Grav Phys Time | Grav Vel (C/T) | Local Latency | Time Dilation |")
print("|------|-----------------|---------------|---------------|------------------|----------------|----------------|---------------|---------------|")
for v, g in zip(vac_hist, grav_hist):
    step = v['step']
    dil = g['physical_time'] / v['physical_time'] if v['physical_time'] > 0 else 1.0
    
    # instantaneous velocity
    if step == 0:
        vac_vel = 0.0
        grav_vel = 0.0
    else:
        # relative to previous step
        prev_v = vac_hist[step-1]
        prev_g = grav_hist[step-1]
        vac_vel = (v['unwrapped_c'] - prev_v['unwrapped_c']) / (v['physical_time'] - prev_v['physical_time'])
        grav_vel = (g['unwrapped_c'] - prev_g['unwrapped_c']) / (g['physical_time'] - prev_g['physical_time'])
        
    print(f"| {step:4d} | {v['unwrapped_c']:15.3f} | {v['physical_time']:13.3f} | {vac_vel:13.3f} | {g['unwrapped_c']:16.3f} | {g['physical_time']:14.3f} | {grav_vel:14.3f} | {g['latency']:13.3f} | {dil:13.3f} |")

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