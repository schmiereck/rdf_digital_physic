import os
import sys
import json
import numpy as np

# Bulletproof path resolving
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from src.engine_d4_closed_loop_v2 import ClosedLoopLatchingEngine
from src.engine_3d import SHIFTS
from src.search_3d_gliders import get_oh_permutations

def rotate_particle_list(part, g, perms, S, S_pinv):
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

def run_simulation(g, eta, steps=160):
    glider_path = "archive/iter_224/results/glider_00_lut08_sub03.json"
    with open(glider_path, "r") as f:
        glider_data = json.load(f)
    particle = glider_data["particle"]
    lut_seed = glider_data["lut_seed"]

    S = np.array(SHIFTS, dtype=float)
    S_pinv = np.linalg.pinv(S)
    perms = get_oh_permutations()

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
    
    part_rot = rotate_particle_list(particle, g, perms, S, S_pinv)
    
    seed_glider(engine, cx1, cy1, cz1, part_rot)
    seed_glider(engine, cx2, cy2, cz2, part_rot)
    
    sep_vec_original = pos2 - pos1
    sep_vec_rot = M_g @ sep_vec_original
    sep_axis = sep_vec_rot / np.linalg.norm(sep_vec_rot)
    
    history = []
    
    for t in range(steps + 1):
        if t > 0:
            engine.step()
            
        total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
        
        active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
        idx = np.argwhere(active_mask)
        
        # We can still project coordinates onto the separation axis
        if idx.size > 0:
            coords = idx[:, :3].astype(float)
            coords_unwrapped = 16.0 + np.mod(coords - 16.0 + L/2, L) - L/2
            projections = coords_unwrapped @ sep_axis
            midpoint = np.mean(projections)
            g1_mask = projections < midpoint
            g2_mask = ~g1_mask
            
            if g1_mask.sum() > 0 and g2_mask.sum() > 0:
                com1 = np.mean(projections[g1_mask])
                com2 = np.mean(projections[g2_mask])
                sep = com2 - com1
            else:
                sep = float('nan')
        else:
            sep = float('nan')
            
        history.append({
            "step": t,
            "total_bits": total_bits,
            "separation": sep,
        })
        
    return history

active_history = run_simulation(10, eta=2.0)
control_history = run_simulation(10, eta=0.0)

print("Active run history (eta=2.0):")
for entry in active_history[::20]:
    print(f"Step {entry['step']:3d}: Bits = {entry['total_bits']}, Separation = {entry['separation']:.4f}")

print("\nVacuum Control run history (eta=0.0):")
for entry in control_history[::20]:
    print(f"Step {entry['step']:3d}: Bits = {entry['total_bits']}, Separation = {entry['separation']:.4f}")
