import numpy as np
from src.rigorous_glider_audit import build_oh_transforms
from src.glider_charge_analysis import make_BT

transforms = build_oh_transforms()
BT, BT_inv = make_BT()

v_grid = np.array([0.5, 0.0, 1.0])
v_cart = v_grid @ BT_inv
print(f"LUT-08 v_grid = {v_grid}, norm = {np.linalg.norm(v_grid):.4f}")
print(f"LUT-08 v_cart = {v_cart}, norm = {np.linalg.norm(v_cart):.4f}")
print()

# Check how M_g transforms the velocity
norms_grid = []
norma_cart = []
for i, (perm, M_g) in enumerate(transforms):
    v_rot_grid = M_g @ v_grid
    v_rot_cart = v_rot_grid @ BT_inv
    norms_grid.append(np.linalg.norm(v_rot_grid))
    norma_cart.append(np.linalg.norm(v_rot_cart))
    if i < 5:
        print(f"Transform {i}: v_rot_grid = {v_rot_grid}, norm = {np.linalg.norm(v_rot_grid):.4f}")
        print(f"           v_rot_cart = {v_rot_cart}, norm = {np.linalg.norm(v_rot_cart):.4f}")

print(f"\nGrid norm range: {min(norms_grid):.4f} - {max(norms_grid):.4f}")
print(f"Cart norm range: {min(norma_cart):.4f} - {max(norma_cart):.4f}")
