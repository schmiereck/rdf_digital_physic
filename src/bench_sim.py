#!/usr/bin/env python3
"""Quick benchmark of simulate speed."""
import sys, time
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.engine_3d import stream, collide, SHIFTS
from src.rigorous_glider_audit import seed_grid, compute_com_circular, bounding_extent
from src.search_3d_gliders import generate_symmetric_lut, get_oh_permutations, precompute_perm_action, compute_orbits, compute_all_stabilizers

perms = get_oh_permutations()
action = precompute_perm_action(perms)
orbits, _ = compute_orbits(action)
stabs = compute_all_stabilizers(action)
lut = generate_symmetric_lut(seed=42, perms=perms, action=action, orbits=orbits, stabs=stabs)

particle = [(0,0,0,i) for i in range(4)]
L = 32
steps = 16

# Warmup
grid = seed_grid(L, particle)
for _ in range(10):
    grid = stream(grid)
    grid = collide(grid, lut)

# Time
n = 100
t0 = time.time()
for _ in range(n):
    grid = seed_grid(L, particle)
    for __ in range(steps):
        grid = stream(grid)
        grid = collide(grid, lut)
t1 = time.time()
print(f"{n} runs of {steps} steps: {t1-t0:.3f}s")
print(f"Per run: {(t1-t0)/n*1000:.2f} ms")

# Test with COM tracking too
n2 = 100
t0 = time.time()
for _ in range(n2):
    grid = seed_grid(L, particle)
    for __ in range(steps):
        grid = stream(grid)
        grid = collide(grid, lut)
        _ = compute_com_circular(grid)
        _ = bounding_extent(grid)
t1 = time.time()
print(f"With COM+extent: {n2} runs of {steps} steps: {t1-t0:.3f}s")
print(f"Per run: {(t1-t0)/n2*1000:.2f} ms")
