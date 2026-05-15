#!/usr/bin/env python3
"""
glancing_collision.py — Off-axis (glancing) collision between two v=1c gliders.

Setup is identical to iter_181.2 head-on collision except Glider B is offset
by +2 cells in the column direction, creating partial (glancing) overlap.

  Glider A (East): L-tromino at [(32, 64), (33, 64), (33, 65)] — unchanged
  Glider B (West): 180°-rotated L-tromino at [(96, 66), (95, 66), (95, 65)]
                   (column shifted by +2 vs head-on)

Rule: g10_rule_001 from archive/iter_179/results/champion_rule.json
Grid: 128x128 torus.  Steps: 500.
Output: archive/iter_182/results/glancing_collision.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
OUT_DIR      = PROJECT_ROOT / "archive" / "iter_182" / "results"
GIF_PATH     = OUT_DIR / "glancing_collision.gif"

GRID_SIZE = 128
SIM_STEPS = 500

# Glider A: standard L-tromino — same as head-on iter_181.2
# moves East (increasing row)
GLIDER_A = [(32, 64), (33, 64), (33, 65)]

# Glider B: 180°-rotated L-tromino, shifted +2 cols vs head-on (64->66)
# moves West (decreasing row)
GLIDER_B = [(96, 66), (95, 66), (95, 65)]

FRAME_EVERY = 4   # 125 frames for 500 steps
FRAME_MS    = 60  # ~16 fps


def load_lut() -> np.ndarray:
    with open(CHAMP_PATH) as f:
        data = json.load(f)
    print(f"Rule ID: {data['rule_id']}  fitness={data['fitness']}")
    return np.asarray(data["chromosome"], dtype=np.uint8)


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


def main() -> int:
    print("=== Glancing (Off-Axis) Collision Experiment — g10_rule_001 ===")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}  Steps: {SIM_STEPS}")
    print(f"Glider A (East): {GLIDER_A}")
    print(f"Glider B (West): {GLIDER_B}  [+2 col offset vs head-on]\n")

    lut = load_lut()
    print(f"LUT loaded  non-zero: {int(lut.sum())}\n")

    # Initialize grid with both gliders
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in GLIDER_A:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    for r, c in GLIDER_B:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1

    initial_bits = int(grid.sum())
    print(f"Initial bit count: {initial_bits}  (expected 6 = 3+3)\n")

    frames     = [(0, grid.copy())]
    bit_counts = [initial_bits]

    print(f"{'step':>6}  {'bits':>6}")
    print("-" * 16)

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        bit_counts.append(bc)

        if step % FRAME_EVERY == 0:
            frames.append((step, grid.copy()))

        if step % 50 == 0:
            print(f"{step:>6}  {bc:>6}")

    final_bits = int(grid.sum())
    min_bits   = min(bit_counts)
    max_bits   = max(bit_counts)
    conserved  = all(bc == initial_bits for bc in bit_counts)

    # Find first step where bit count changes (collision onset)
    collision_step = next(
        (s for s, bc in enumerate(bit_counts) if bc != initial_bits), None
    )

    print()
    print(f"Initial bit count:  {initial_bits}")
    print(f"Final bit count:    {final_bits}")
    print(f"Min bits observed:  {min_bits}")
    print(f"Max bits observed:  {max_bits}")
    print(f"Bits conserved:     {conserved}")
    print(f"Collision at step:  {collision_step}")

    # Classify collision outcome
    if final_bits == initial_bits and conserved:
        outcome = "elastic (bits conserved throughout)"
    elif final_bits == initial_bits and not conserved:
        outcome = "partially inelastic (bits vary mid-simulation, recover to initial)"
    elif final_bits > 0 and final_bits != initial_bits:
        outcome = f"inelastic (final={final_bits}, initial={initial_bits})"
    else:
        outcome = "annihilation (no bits remain)"
    print(f"Collision outcome:  {outcome}")

    # Print per-step bit count around collision
    if collision_step is not None:
        lo = max(0, collision_step - 5)
        hi = min(len(bit_counts) - 1, collision_step + 20)
        print(f"\nBit-count trace around collision (steps {lo}–{hi}):")
        for s in range(lo, hi + 1):
            marker = " <-- collision onset" if s == collision_step else ""
            print(f"  step {s:4d}: {bit_counts[s]}{marker}")

    # Save animation
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nGenerating animation ({len(frames)} frames) -> {GIF_PATH.name}")

    fig, ax = plt.subplots(figsize=(6, 6), dpi=100)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title(
        "Glancing Collision — g10_rule_001 — 500 steps\n(Glider B col offset +2)",
        color="white", fontsize=9,
    )
    ax.set_xlabel("col", color="white")
    ax.set_ylabel("row", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")

    img = ax.imshow(
        frames[0][1], origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
    )
    info = ax.text(
        0.02, 0.97, f"step=0  bits={initial_bits}",
        transform=ax.transAxes, color="white", fontsize=9, va="top",
    )

    def update(frame_idx):
        step, g = frames[frame_idx]
        img.set_data(g)
        info.set_text(f"step={step}  bits={bit_counts[step]}")
        return img, info

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=FRAME_MS, blit=True,
    )
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print(f"\n=== Summary ===")
    print(f"  initial_bits:    {initial_bits}")
    print(f"  final_bits:      {final_bits}")
    print(f"  min_bits:        {min_bits}")
    print(f"  max_bits:        {max_bits}")
    print(f"  conserved:       {conserved}")
    print(f"  collision_step:  {collision_step}")
    print(f"  outcome:         {outcome}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
