import os
import sys
import json
import numpy as np

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

def toroidal_diff(p1, p2, L=32):
    """Computes p1 - p2 on toroidal lattice of size L."""
    diff = p1 - p2
    return np.mod(diff + L/2, L) - L/2

def get_toroidal_centroid(coords, anchor, L=32):
    """Computes centroid of coords unwrapped relative to an anchor coordinate."""
    diffs = toroidal_diff(coords, anchor, L)
    unwrapped = anchor + diffs
    return np.mean(unwrapped, axis=0)

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
    
    # Let's see the initial coordinates of the gliders
    pos1 = np.array([0, -3, 0], dtype=float)
    pos2 = np.array([0, 2, 0], dtype=float)
    
    p1_rot = np.round(M_g @ pos1).astype(int) + 16
    p2_rot = np.round(M_g @ pos2).astype(int) + 16
    
    cx1, cy1, cz1 = p1_rot
    cx2, cy2, cz2 = p2_rot
    
    part_rot = rotate_particle_list(particle, g, perms, S, S_pinv)
    
    seed_glider(engine, cx1, cy1, cz1, part_rot)
    seed_glider(engine, cx2, cy2, cz2, part_rot)
    
    # Track continuous positions of both gliders
    c1_continuous = np.array(p1_rot, dtype=float)
    c2_continuous = np.array(p2_rot, dtype=float)
    
    c1_prev_toroidal = np.mod(p1_rot, L).astype(float)
    c2_prev_toroidal = np.mod(p2_rot, L).astype(float)
    
    history = []
    
    for t in range(steps + 1):
        if t > 0:
            engine.step()
            
        total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
        
        # Get active cell coordinates
        active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
        idx = np.argwhere(active_mask)[:, :3]  # shape (N, 3)
        
        if idx.shape[0] == 8:
            # Cluster based on proximity to previous toroidal centroids
            # Compute toroidal distance to c1_prev_toroidal and c2_prev_toroidal
            d1 = np.linalg.norm(toroidal_diff(idx, c1_prev_toroidal, L), axis=1)
            d2 = np.linalg.norm(toroidal_diff(idx, c2_prev_toroidal, L), axis=1)
            
            # Since both gliders are identical and coherent, we assign the 4 closest to c1 and 4 closest to c2
            # Or simply assign to the closer centroid:
            mask1 = d1 < d2
            if mask1.sum() == 4:
                idx1 = idx[mask1]
                idx2 = idx[~mask1]
            else:
                # If simple clustering is not 4-4, sort by d1 - d2 and split
                sorted_indices = np.argsort(d1 - d2)
                idx1 = idx[sorted_indices[:4]]
                idx2 = idx[sorted_indices[4:]]
            
            # Compute new toroidal centroids
            c1_toroidal = np.mod(get_toroidal_centroid(idx1, c1_prev_toroidal, L), L)
            c2_toroidal = np.mod(get_toroidal_centroid(idx2, c2_prev_toroidal, L), L)
            
            # Update continuous positions
            c1_continuous += toroidal_diff(c1_toroidal, c1_prev_toroidal, L)
            c2_continuous += toroidal_diff(c2_toroidal, c2_prev_toroidal, L)
            
            c1_prev_toroidal = c1_toroidal.copy()
            c2_prev_toroidal = c2_toroidal.copy()
            
            # Separation in 3D unwrapped continuous space
            sep_3d = np.linalg.norm(c2_continuous - c1_continuous)
        else:
            sep_3d = float('nan')
            
        history.append({
            "step": t,
            "total_bits": total_bits,
            "separation": sep_3d,
            "c1": c1_continuous.copy() if idx.shape[0] == 8 else None,
            "c2": c2_continuous.copy() if idx.shape[0] == 8 else None,
        })
        
    return history

active_history = run_simulation(10, eta=2.0)
control_history = run_simulation(10, eta=0.0)

print("Active run history (eta=2.0):")
for entry in active_history[::20]:
    print(f"Step {entry['step']:3d}: Bits = {entry['total_bits']}, Separation = {entry['separation']:.4f}, C1 = {entry['c1']}, C2 = {entry['c2']}")

print("\nVacuum Control run history (eta=0.0):")
for entry in control_history[::20]:
    print(f"Step {entry['step']:3d}: Bits = {entry['total_bits']}, Separation = {entry['separation']:.4f}, C1 = {entry['c1']}, C2 = {entry['c2']}")
