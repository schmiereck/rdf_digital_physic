#!/usr/bin/env python3
"""Deep inspect collision step for LUT-08 reference."""
import json, numpy as np, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.engine_3d import stream, collide, pack, SHIFTS
from src.rigorous_glider_audit import seed_grid

with open('archive/iter_224/results/glider_00_lut08_sub03.json') as f:
    ref = json.load(f)
lut = np.array(ref["lut"], dtype=np.uint16)
particle = [tuple(c) for c in ref["particle"]]

L = 32
grid = seed_grid(L, particle)
print("Initial particle:", particle)

for step in range(6):
    bits = np.argwhere(grid > 0)
    print(f"\n=== Step {step} ===")
    print(f"Bits: {len(bits)}")
    for b in bits:
        print(f"  cell=({b[0]},{b[1]},{b[2]}) ch={b[3]}")

    # Stream
    streamed = stream(grid)
    s_bits = np.argwhere(streamed > 0)
    print(f"After stream: {len(s_bits)} bits")
    cell_counts = {}
    for b in s_bits:
        cell = (int(b[0]), int(b[1]), int(b[2]))
        cell_counts[cell] = cell_counts.get(cell, 0) + 1
    multi = {c: n for c, n in cell_counts.items() if n > 1}
    print(f"Cells with multi-bit AFTER STREAM: {multi}")

    # Packed state before collision
    packed_before = pack(streamed)
    non_zero_cells = np.argwhere(packed_before > 0)
    print(f"Non-zero packed cells before collision: {len(non_zero_cells)}")
    for c in non_zero_cells[:20]:
        cell = (int(c[0]), int(c[1]), int(c[2]))
        val = int(packed_before[cell])
        print(f"  cell={cell} packed={val} bits={bin(val).count('1')}")

    # Collide
    grid = collide(streamed, lut)
    c_bits = np.argwhere(grid > 0)
    print(f"After collide: {len(c_bits)} bits")
