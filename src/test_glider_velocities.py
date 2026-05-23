import os, sys, json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import SHIFTS, stream, collide
from src.rigorous_glider_audit import build_oh_transforms, seed_grid, bounding_extent

L = 32

def get_center_of_mass(grid):
    # For simplicity, calculate unrolled center of mass
    bits = np.argwhere(grid > 0)
    if len(bits) == 0:
        return np.zeros(3)
    return bits[:, :3].mean(axis=0)

def main():
    with open(ROOT / "archive/iter_224/results/glider_00_lut08_sub03.json") as f:
        d = json.load(f)
    lut = np.array(d["lut"], dtype=np.uint16)
    pA = [tuple(c) for c in d["particle"]]
    
    transforms = build_oh_transforms()
    stable_particles = []
    for g_idx, (perm, M_g) in enumerate(transforms):
        p_rot = []
        for (dl, dr, dc, ch) in pA:
            v = M_g @ np.array([dl, dr, dc], dtype=float)
            p_rot.append((int(np.round(v[0])), int(np.round(v[1])), int(np.round(v[2])), int(perm[ch])))
        
        # Test vacuum stability
        grid = seed_grid(L, p_rot)
        if int(grid.sum()) != 4: continue
        curr = grid.copy()
        stable = True
        for _ in range(40):
            curr = collide(stream(curr), lut)
            if int(curr.sum()) != 4 or max(bounding_extent(curr)) > 5:
                stable = False
                break
        if stable:
            stable_particles.append((g_idx, p_rot))
            
    # Calculate velocity for pA
    grid_A = seed_grid(L, pA)
    com_0 = get_center_of_mass(grid_A)
    curr = grid_A.copy()
    for _ in range(40):
        curr = collide(stream(curr), lut)
    com_40 = get_center_of_mass(curr)
    vel_A = (com_40 - com_0) / 40.0
    print(f"Original particle velocity (pA): {vel_A}")
    
    # Calculate velocities for stable particles
    for idx, (g_idx, p_rot) in enumerate(stable_particles):
        grid = seed_grid(L, p_rot)
        com_0 = get_center_of_mass(grid)
        curr = grid.copy()
        for _ in range(40):
            curr = collide(stream(curr), lut)
        com_40 = get_center_of_mass(curr)
        # Unwrap COM crossing boundaries
        diff = com_40 - com_0
        for i in range(3):
            if diff[i] > 16: diff[i] -= 32
            elif diff[i] < -16: diff[i] += 32
        vel = diff / 40.0
        print(f"Stable particle {idx} (g_idx {g_idx}): velocity {vel}")

if __name__ == "__main__":
    main()
