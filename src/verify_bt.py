#!/usr/bin/env python3
"""Verify BT conversion."""
import sys, json
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.glider_charge_analysis import make_BT

BT, BT_inv = make_BT()
print("BT =")
print(BT)
print("\nBT_inv =")
print(BT_inv)

# LUT-08 displacement over 200 steps in grid coords
cumdisp_grid = np.array([50.0, 0.0, 100.0])
steps = 200
v_grid = cumdisp_grid / steps

# Convert to cartesian
v_cart_via_BT = v_grid @ BT
v_cart_via_BTinv = v_grid @ BT_inv

print(f"\nv_grid = {v_grid}")
print(f"v_cart @ BT = {v_cart_via_BT}")
print(f"v_cart @ BT_inv = {v_cart_via_BTinv}")

# What's the FCC NN vector (0,1,0) in Cartesian?
print(f"\nSHIFTS[0] [0,1,0] @ BT = {np.array([0,1,0]) @ BT}")
print(f"SHIFTS[0] [0,1,0] @ BT_inv = {np.array([0,1,0]) @ BT_inv}")

# What's (1,0,0) in Cartesian? This should be the basis vector for the grid
print(f"\nGrid (1,0,0) @ BT = {np.array([1,0,0]) @ BT}")
print(f"Grid (1,0,0) @ BT_inv = {np.array([1,0,0]) @ BT_inv}")

# Reference: FCC vectors
from src.search_3d_gliders import fcc_neighbor_vectors
C = fcc_neighbor_vectors().astype(float)
print(f"\nFCC vector 0 (1,1,0): {C[0]}")
print(f"FCC vector 4 (1,0,1): {C[4]}")
print(f"FCC vector 8 (0,1,1): {C[8]}")
