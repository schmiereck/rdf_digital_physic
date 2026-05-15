#!/usr/bin/env python3
"""
run_iter_180_collision.py

Head-on collision of two v=1c gliders using the champion rule g10_rule_001
from iter_179.

Setup:
  - 256x256 toroidal grid
  - Seed 1: L-tromino at (100, 128), original orientation, moving East (+row)
  - Seed 2: L-tromino at (155, 128), rotated 180 degrees, moving West (-row)
  - 100 simulation steps
Output: archive/iter_180/results/head_on_collision.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
POP_PATH     = PROJECT_ROOT / "archive" / "iter_179" / "results" / "final_population.json"
GIF_PATH     = PROJECT_ROOT / "archive" / "iter_180" / "results" / "head_on_collision.gif"

GRID_SIZE  = 256
SIM_STEPS  = 100
FRAME_MS   = 100  # ms per frame (10 fps)

# Seed 1 at (100, 128): original L-tromino orientation → moves East (+row)
# Shape: (r, c), (r+1, c), (r+1, c+1)
SEED1_CELLS = [(100, 128), (101, 128), (101, 129)]

# Seed 2 at (155, 128): 180°-rotated L-tromino → moves West (-row)
# 180° rotation of original shape: (r, c), (r, c+1), (r+1, c+1)
SEED2_CELLS = [(155, 128), (155, 129), (156, 129)]

INITIAL_BITS = len(SEED1_CELLS) + len(SEED2_CELLS)  # 6


def lut_from_chromosome(chrom: list) -> np.ndarray:
    return np.asarray(chrom, dtype=np.uint8)


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,     1, axis=1)
    nw = np.roll(w,    -1, axis=1)
    state = (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)
    return lut[state]


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def main():
    # Load champion rule g10_rule_001 from iter_179
    with open(POP_PATH) as f:
        pop_data = json.load(f)

    champion = next(r for r in pop_data["population"] if r["rule_id"] == "g10_rule_001")
    lut = lut_from_chromosome(champion["chromosome"])
    print(f"Loaded rule: {champion['rule_id']}  (stored fitness={champion['fitness']})")

    # Initialize grid with two seeds
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in SEED1_CELLS:
        grid[r, c] = 1
    for r, c in SEED2_CELLS:
        grid[r, c] = 1

    print(f"Grid size:    {GRID_SIZE}x{GRID_SIZE}")
    print(f"Seed 1 cells: {SEED1_CELLS}  (moving East, +row)")
    print(f"Seed 2 cells: {SEED2_CELLS}  (moving West, -row)")
    print(f"Initial bits: {INITIAL_BITS}")

    # Simulate and collect every frame
    frames     = [(0, grid.copy())]
    bit_counts = [int(grid.sum())]

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        bit_counts.append(bc)
        frames.append((step, grid.copy()))

        if step % 10 == 0:
            com = center_of_mass(grid)
            print(f"  step={step:3d}  bits={bc}  com=({com[0]:.2f},{com[1]:.2f})")

    final_bits = bit_counts[-1]
    max_bc     = max(bit_counts)
    min_bc     = min(bit_counts)

    # Determine qualitative outcome
    if final_bits == 0:
        outcome = "annihilation"
    elif final_bits == INITIAL_BITS:
        outcome = "elastic"
    elif final_bits < INITIAL_BITS:
        outcome = "partial_annihilation"
    else:
        outcome = "creation_or_fusion"

    print(f"\nFinal bits:  {final_bits}  (initial={INITIAL_BITS})")
    print(f"Bit range:   min={min_bc}  max={max_bc}")
    print(f"Outcome:     {outcome}")

    # ── Animation ──────────────────────────────────────────────────────────────
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    # Crop window centred on the collision zone
    R0, R1 = 80, 180
    C0, C1 = 110, 150

    print(f"\nGenerating animation ({len(frames)} frames, view rows {R0}-{R1}, cols {C0}-{C1}) ...")

    fig, ax = plt.subplots(figsize=(6, 8), dpi=100)
    ax.set_title("Head-on Collision — g10_rule_001")
    ax.set_xlabel("col")
    ax.set_ylabel("row")

    step0, g0 = frames[0]
    img = ax.imshow(
        g0[R0:R1, C0:C1],
        origin="upper",
        interpolation="nearest",
        cmap="hot",
        vmin=0, vmax=1,
        extent=[C0, C1, R1, R0],
    )
    info = ax.text(
        0.02, 0.97, f"step={step0}  bits={bit_counts[0]}",
        transform=ax.transAxes, color="white", fontsize=9, va="top",
    )

    def update(frame_idx):
        step, g = frames[frame_idx]
        img.set_data(g[R0:R1, C0:C1])
        info.set_text(f"step={step}  bits={bit_counts[step]}")
        return img, info

    ani = animation.FuncAnimation(
        fig, update,
        frames=len(frames),
        interval=FRAME_MS,
        blit=True,
    )

    GIF_PATH.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print(f"\n=== Summary ===")
    print(f"Rule:          g10_rule_001")
    print(f"Steps:         {SIM_STEPS}")
    print(f"Initial bits:  {INITIAL_BITS}")
    print(f"Final bits:    {final_bits}")
    print(f"Bit range:     min={min_bc}  max={max_bc}")
    print(f"Outcome:       {outcome}")
    print(f"GIF:           {GIF_PATH}")

    return final_bits, outcome, max_bc, min_bc


if __name__ == "__main__":
    final_bits, outcome, max_bc, min_bc = main()
    print(f"\nfinal_bits={final_bits}  outcome={outcome}")
    sys.exit(0)
