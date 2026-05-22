import os
import sys
import json
import numpy as np

# Bulletproof path resolving
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

# We will select 4 orientations representing different lattice axes:
# g=0: Identity (original parallel in-plane Y separation)
# g=5: Coordinate reflection
# g=10: 90-deg rotation of layers stacking
# g=21: Rotation mixing multiple axes
selected_gs = [0, 5, 10, 21]

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

def run_sim(g, eta, steps=80):
    L = 32
    # Baseline physical parameters from Phase 5.2 (iter_234)
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
    
    # Initial relative positions from center: pos1=(0, -3, 0) and pos2=(0, 2, 0)
    # The separation is 5.0 in the row direction (Y-axis)
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
    
    # Rotate particles
    part_rot = rotate_particle_list(particle, g)
    
    seed_glider(engine, cx1, cy1, cz1, part_rot)
    seed_glider(engine, cx2, cy2, cz2, part_rot)
    
    # We track separation along the rotated separation axis:
    sep_vec_original = pos2 - pos1  # [0, 5, 0]
    sep_vec_rot = M_g @ sep_vec_original
    sep_axis = sep_vec_rot / np.linalg.norm(sep_vec_rot)
    
    traj_sep = []
    
    for t in range(steps + 1):
        if t > 0:
            engine.step()
            
        total_bits = int(engine.temporal_grid.sum() + engine.latched_grid.sum())
        if total_bits != 8:
            return {"stable": False, "fail_reason": f"bit violation: {total_bits}", "deflection": 0.0}
            
        # Get active cell coordinates
        active_mask = (engine.temporal_grid == 1) | (engine.latched_grid == 1)
        idx = np.argwhere(active_mask)
        if idx.size == 0:
            return {"stable": False, "fail_reason": "no active bits", "deflection": 0.0}
            
        # Project coordinate vectors onto the separation axis to partition into two gliders
        coords = idx[:, :3].astype(float)
        # Unwrap to avoid toroidal wrap jumps
        coords_unwrapped = 16.0 + np.mod(coords - 16.0 + L/2, L) - L/2
        
        projections = coords_unwrapped @ sep_axis
        midpoint = np.mean(projections)
        
        g1_mask = projections < midpoint
        g2_mask = ~g1_mask
        
        if g1_mask.sum() == 0 or g2_mask.sum() == 0:
            return {"stable": False, "fail_reason": "cannot partition gliders", "deflection": 0.0}
            
        com1 = np.mean(projections[g1_mask])
        com2 = np.mean(projections[g2_mask])
        traj_sep.append(com2 - com1)
        
    initial_sep = traj_sep[0]
    final_sep = traj_sep[-1]
    deflection = initial_sep - final_sep
    return {
        "stable": True,
        "fail_reason": "",
        "deflection": deflection,
        "initial_sep": initial_sep,
        "final_sep": final_sep
    }

results = {}
for g in selected_gs:
    res_active = run_sim(g, eta=2.0, steps=80)
    res_control = run_sim(g, eta=0.0, steps=80)
    results[g] = {
        "active": res_active,
        "control": res_control
    }

# Save report
os.makedirs(os.path.join(parent_dir, "archive", "iter_235", "results"), exist_ok=True)
report_path = os.path.join(parent_dir, "archive", "iter_235", "results", "oh_covariance_report.txt")
with open(report_path, "w") as f:
    f.write("OCTAHEDRAL SYMMETRY COVARIANCE REPORT\n")
    f.write("=====================================\n\n")
    for g, data in results.items():
        f.write(f"Permutation {g}:\n")
        f.write(f"  Active run (eta=2.0):\n")
        f.write(f"    Stable: {data['active']['stable']} (Reason: {data['active']['fail_reason']})\n")
        f.write(f"    Initial Separation: {data['active'].get('initial_sep', 0.0):.4f}\n")
        f.write(f"    Final Separation: {data['active'].get('final_sep', 0.0):.4f}\n")
        f.write(f"    Deflection: {data['active']['deflection']:.4f}\n")
        f.write(f"  Vacuum Control run (eta=0.0):\n")
        f.write(f"    Stable: {data['control']['stable']}\n")
        f.write(f"    Deflection: {data['control']['deflection']:.4f}\n\n")

print("Symmetry report written successfully.")
for g, data in results.items():
    print(f"Perm {g:2d}: Active Deflection = {data['active']['deflection']:.4f}, Control = {data['control']['deflection']:.4f}")
