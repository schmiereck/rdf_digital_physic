import os, sys, json
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.engine_3d import SHIFTS, stream, collide
from src.rigorous_glider_audit import build_oh_transforms, seed_grid, bounding_extent

L = 32

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
        for _ in range(80):
            curr = collide(stream(curr), lut)
            if int(curr.sum()) != 4 or max(bounding_extent(curr)) > 5:
                stable = False
                break
        if stable:
            stable_particles.append((g_idx, p_rot))
            
    print(f"Found {len(stable_particles)} stable rotated particles under O_h transformations.")
    
    # Let's measure their displacement over 40 steps
    for g_idx, pB in stable_particles:
        grid = seed_grid(L, pB)
        curr = grid.copy()
        for _ in range(40):
            curr = collide(stream(curr), lut)
        bits = np.argwhere(curr > 0)
        # Compute center of mass
        com = bits[:, :3].mean(axis=0) - L//2
        print(f"g_idx {g_idx}: COM after 40 steps = {com}")

if __name__ == "__main__":
    main()
