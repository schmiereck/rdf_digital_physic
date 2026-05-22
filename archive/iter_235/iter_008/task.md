Write the following Python script to `src/test_bound_state_long.py`:

```python
import os
import sys
import json
import numpy as np

# Resolve paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.engine_d4_closed_loop_v2 import ClosedLoopLatchingEngine
from src.engine_3d import SHIFTS
from src.search_3d_gliders import get_oh_permutations

# 1. Load glider configuration
glider_path = os.path.join(parent_dir, "archive", "iter_224", "results", "glider_00_lut08_sub03.json")
if not os.path.exists(glider_path):
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
with open(glider_path, "r") as f:
    glider_data = json.load(f)
particle = glider_data["particle"]
lut_seed = glider_data["lut_seed"]

# 2. Setup shifts and permutations
S = np.array(SHIFTS, dtype=float)
S_pinv = np.linalg.pinv(S)
perms = get_oh_permutations()

g = 10  # Permutation 10 (90-degree layer stacking rotation)

def rotate_particle_list(part, g):
    perm = perms[g]
    S_rot = np.zeros_like(S)
    for i in range(12):
        S_rot[i] = S[perm[i]]
    M_g = S_rot.T @ S_pinv.T
    
    rotated = []
    for (dl, dr, dc, ch) in part:
        pos = np.array([dl, dr, dc], dtype=float)
        pos_rot = np.round(M_g @ pos).astype(int)
        ch_rot = perm[ch]
        rotated.append([int(pos_rot[0]), int(pos_rot[1]), int(pos_rot[2]), int(ch_rot)])
    return rotated

def seed_glider(engine, cx, cy, cz, rotated_part):
    L = engine.L
    for dl, dr, dc, ch in rotated_part:
        engine.temporal_grid[(cx + dl) % L, (cy + dr) % L, (cz + dc) % L, ch] = 1

def run_sim(eta, steps=160):
    L = 32
    engine = ClosedLoopLatchingEngine(
        L=L,
        gamma=0.90,
        eta=eta,
        threshold=0.045,
        alpha=2.0,
        sigma=2.5,
        lut_seed=lut_seed,
        use_12_channels=True
    )
    
    perm = perms[g]
    S_rot = np.zeros_like(S)
    for i in range(12):
        S_rot[i] = S[perm[i]]
    M_g = S_rot.T @ S_pinv.T
    
    pos1 = np.array([0, -3, 0], dtype=float)
    pos2 = np.array([0, 2, 0], dtype=float)
    
    p1_rot = np.round(M_g @ pos1).astype(int) + 16
    p2_rot = np.round(M_g @ pos2).astype(int) + 16
    
    cx1, cy1, cz1 = p1_rot
    cx2, cy2, cz2 = p2_rot
    
    part_rot = rotate_particle_list(particle, g)
    
    seed_glider(engine, cx1, cy1, cz1, part_rot)
    seed_glider(engine, cx2, cy2, cz2, part_rot)
    
    sep_vec_original = pos2 - pos1  # [0, 5, 0]
    sep_vec_rot = M_g @ sep_vec_original
    sep_axis = sep_vec_rot / np.linalg.norm(sep_vec_rot)
    
    history = []
    
    for t in range(steps + 1):
        if t > 0:
            engine.step()
            
        total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
        if total_bits != 8:
            history.append((t, total_bits, float("nan"), "bit violation"))
            continue
            
        active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
        idx = np.argwhere(active_mask)
        if idx.size == 0:
            history.append((t, total_bits, float("nan"), "no active bits"))
            continue
            
        coords = idx[:, :3].astype(float)
        coords_unwrapped = 16.0 + np.mod(coords - 16.0 + L/2, L) - L/2
        
        projections = coords_unwrapped @ sep_axis
        midpoint = np.mean(projections)
        
        g1_mask = projections < midpoint
        g2_mask = ~g1_mask
        
        if g1_mask.sum() == 0 or g2_mask.sum() == 0:
            history.append((t, total_bits, float("nan"), "partition error"))
            continue
            
        com1 = np.mean(projections[g1_mask])
        com2 = np.mean(projections[g2_mask])
        sep = com2 - com1
        history.append((t, total_bits, sep, "ok"))
        
    return history

print("Running 160-step simulations for Permutation 10...")
hist_active = run_sim(eta=2.0, steps=160)
hist_control = run_sim(eta=0.0, steps=160)

# Save report
os.makedirs(os.path.join(parent_dir, "archive", "iter_235", "results"), exist_ok=True)
report_path = os.path.join(parent_dir, "archive", "iter_235", "results", "bound_state_long_report.txt")
with open(report_path, "w") as f:
    f.write("LONG-TERM SUSTAINED BOUND STATE REPORT (PERMUTATION 10)\n")
    f.write("=====================================================\n\n")
    f.write("Step | Active Bits | Active Sep | Active Status | Control Bits | Control Sep | Control Status\n")
    f.write("--------------------------------------------------------------------------------------------\n")
    for idx in range(len(hist_active)):
        t, b_a, s_a, st_a = hist_active[idx]
        _, b_c, s_c, st_c = hist_control[idx]
        f.write(f"{t:4d} | {b_a:11d} | {s_a:10.4f} | {st_a:13s} | {b_c:12d} | {s_c:11.4f} | {st_c:14s}\n")

print("Sustained bound state report written successfully.")
print("\nKey frames of the trajectory (Active vs Control):")
print("Step | Active Sep | Control Sep")
print("-------------------------------")
for step in [0, 20, 40, 60, 80, 100, 120, 140, 160]:
    t, _, s_a, _ = hist_active[step]
    _, _, s_c, _ = hist_control[step]
    print(f"{t:4d} | {s_a:10.4f} | {s_c:11.4f}")
```

Execute this script using Python and verify it runs successfully. Print the output in your response.
