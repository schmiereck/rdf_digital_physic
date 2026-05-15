#!/usr/bin/env python3
"""
glider_bit_collision.py — Collision experiment: v=1c glider vs. single stationary bit.

Setup:
  - 128x128 toroidal grid
  - Glider: L-tromino near (32, 64), moving East (+row direction)
    Shape: (32,64), (33,64), (33,65)
  - Target: single stationary '1' bit at (64, 64)
  - 500 simulation steps
  - Rule: g10_rule_001 from archive/iter_179/results/champion_rule.json

Output: archive/iter_181/results/glider_bit_collision.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
GIF_PATH     = PROJECT_ROOT / "archive" / "iter_181" / "results" / "glider_bit_collision.gif"

GRID_SIZE  = 128
SIM_STEPS  = 500
FRAME_EVERY = 2   # ~250 frames total
FRAME_MS    = 60

# Glider: original L-tromino orientation → moves East (+row)
GLIDER_CELLS = [(32, 64), (33, 64), (33, 65)]
# Target: single stationary bit in the glider's path
TARGET_CELL  = (64, 64)

INITIAL_BITS = len(GLIDER_CELLS) + 1  # 4


def load_rule() -> np.ndarray:
    print(f"Loading champion rule from {CHAMP_PATH}")
    with open(CHAMP_PATH) as f:
        data = json.load(f)
    chrom = data["chromosome"]
    print(f"Rule ID: {data['rule_id']}  fitness={data['fitness']}")
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


def main() -> int:
    print("=== iter_181.3 — Glider vs. Single Bit Collision ===")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}")
    print(f"Glider cells: {GLIDER_CELLS}  (L-tromino, moving East/+row)")
    print(f"Target cell:  {TARGET_CELL}")
    print(f"Initial bits: {INITIAL_BITS}")
    print(f"Steps: {SIM_STEPS}\n")

    # Load rule
    lut = load_rule()
    print(f"LUT loaded ({len(lut)} entries)  non-zero: {int(lut.sum())}\n")

    # Initialize grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in GLIDER_CELLS:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    r_t, c_t = TARGET_CELL
    grid[r_t % GRID_SIZE, c_t % GRID_SIZE] = 1

    initial_bc  = int(grid.sum())
    initial_com = center_of_mass(grid)
    print(f"Initial bit count: {initial_bc}")
    print(f"Initial CoM:       ({initial_com[0]:.2f}, {initial_com[1]:.2f})\n")

    # Track per-step data
    frames     = [(0, grid.copy())]
    bit_counts = [initial_bc]
    max_bits   = initial_bc
    collision_step = None
    explosion_detected = False

    print(f"{'step':>6}  {'bits':>6}  {'com_row':>8}  {'com_col':>8}")
    print("-" * 40)

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        bit_counts.append(bc)

        if bc > max_bits:
            max_bits = bc
        if bc > 10 and not explosion_detected:
            explosion_detected = True
            print(f"  *** Possible explosion at step={step}: bits={bc} ***")

        if step % FRAME_EVERY == 0:
            frames.append((step, grid.copy()))

        if step % 50 == 0:
            com = center_of_mass(grid)
            print(f"{step:>6}  {bc:>6}  {com[0]:>8.2f}  {com[1]:>8.2f}")

        # Detect collision point (first step where bit count changes from initial 4)
        if collision_step is None and bc != INITIAL_BITS:
            collision_step = step

    final_bc  = bit_counts[-1]
    final_com = center_of_mass(grid)

    print()
    print(f"=== Results ===")
    print(f"Initial bits:      {initial_bc}")
    print(f"Final bits:        {final_bc}")
    print(f"Max bits ever:     {max_bits}")
    print(f"Collision at step: {collision_step}")
    print(f"Explosion:         {explosion_detected}")
    print(f"Bit conserved:     {final_bc == INITIAL_BITS}")
    print(f"Final CoM:         ({final_com[0]:.2f}, {final_com[1]:.2f})")

    # Classify outcome
    if final_bc == 0:
        outcome = "annihilation"
    elif final_bc == INITIAL_BITS and max_bits == INITIAL_BITS:
        outcome = "elastic_or_pass_through"
    elif final_bc == INITIAL_BITS:
        outcome = "bit_conserved_after_disturbance"
    elif final_bc < INITIAL_BITS:
        outcome = "partial_annihilation"
    elif explosion_detected and max_bits > 20:
        outcome = "explosive_growth"
    else:
        outcome = "inelastic_creation"
    print(f"Outcome:           {outcome}")

    # Generate animation
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    GIF_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"\nGenerating animation ({len(frames)} frames) -> {GIF_PATH.name}")

    # Show the full 128x128 grid but zoom to region of interest
    R0, R1 = 20, 110
    C0, C1 = 50, 90

    fig, ax = plt.subplots(figsize=(5, 8), dpi=100)
    ax.set_title("Glider vs. Single Bit — g10_rule_001")
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
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print(f"\n=== Summary ===")
    print(f"  initial_bits:    {initial_bc}")
    print(f"  final_bits:      {final_bc}")
    print(f"  max_bits:        {max_bits}")
    print(f"  collision_step:  {collision_step}")
    print(f"  explosion:       {explosion_detected}")
    print(f"  outcome:         {outcome}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
