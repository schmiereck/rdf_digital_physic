#!/usr/bin/env python3
"""
iter_185_glancing_collision.py — Parallel-trajectory glancing collision.

Two East-bound 3-bit L-tromino gliders on parallel tracks, offset 2 cells
in the North/South (column) direction. Starting positions place the gliders
near the grid center so their edge neighborhoods interact from step 1.

  Glider A (East): L-tromino at [(62,62),(63,62),(63,63)]  col track ~62
  Glider B (East): L-tromino at [(62,64),(63,64),(63,65)]  col track ~64
                   2-col North offset vs Glider A

Rule: g10_rule_001 from archive/iter_179/results/champion_rule.json
Grid: 128x128 torus.  Steps: 500.
Output: archive/iter_185/results/glancing_collision.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
OUT_DIR      = PROJECT_ROOT / "archive" / "iter_185" / "results"
GIF_PATH     = OUT_DIR / "glancing_collision.gif"

GRID_SIZE = 128
SIM_STEPS = 500

# Glider A: standard L-tromino [(r,c),(r+1,c),(r+1,c+1)]
# Placed near center (row 62-63, col 62-63), moves East (increasing row)
GLIDER_A = [(62, 62), (63, 62), (63, 63)]

# Glider B: same L-tromino orientation, 2-col North/South offset
# col 64-65, same row start — 2-cell lateral gap between their edges
GLIDER_B = [(62, 64), (63, 64), (63, 65)]

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


def center_of_mass(grid: np.ndarray):
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return None, None
    return float(np.mean(rows)), float(np.mean(cols))


def main() -> int:
    print("=== Parallel Glancing Collision Experiment — g10_rule_001 ===")
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}  Steps: {SIM_STEPS}")
    print(f"Glider A (East, col~62): {GLIDER_A}")
    print(f"Glider B (East, col~64): {GLIDER_B}  [+2 col N/S offset]\n")

    lut = load_lut()
    print(f"LUT loaded  non-zero: {int(lut.sum())}\n")

    # Initialize grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in GLIDER_A:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    for r, c in GLIDER_B:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1

    initial_bits = int(grid.sum())
    print(f"Initial bit count: {initial_bits}  (expected 6 = 3+3)\n")

    frames     = [(0, grid.copy())]
    bit_counts = [initial_bits]

    # Track center-of-mass trajectory to detect scatter vs fuse
    com_rows   = []
    com_cols   = []
    r0, c0 = center_of_mass(grid)
    com_rows.append(r0)
    com_cols.append(c0)

    print(f"{'step':>6}  {'bits':>6}  {'com_row':>10}  {'com_col':>10}")
    print("-" * 40)

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        bit_counts.append(bc)

        cr, cc = center_of_mass(grid)
        com_rows.append(cr)
        com_cols.append(cc)

        if step % FRAME_EVERY == 0:
            frames.append((step, grid.copy()))

        if step % 50 == 0:
            print(f"{step:>6}  {bc:>6}  {cr:>10.2f}  {cc:>10.2f}")

    final_bits = int(grid.sum())
    min_bits   = min(bit_counts)
    max_bits   = max(bit_counts)
    conserved  = all(bc == initial_bits for bc in bit_counts)

    # Find first step where bit count deviates from initial
    deviation_step = next(
        (s for s, bc in enumerate(bit_counts) if bc != initial_bits), None
    )

    print()
    print(f"Initial bit count:   {initial_bits}")
    print(f"Final bit count:     {final_bits}")
    print(f"Min bits observed:   {min_bits}")
    print(f"Max bits observed:   {max_bits}")
    print(f"Bits conserved:      {conserved}")
    print(f"First deviation:     step {deviation_step}")

    # Center-of-mass displacement (East = row direction)
    if com_rows[-1] is not None and com_rows[0] is not None:
        row_disp = (com_rows[-1] - com_rows[0]) % GRID_SIZE
        col_disp = (com_cols[-1] - com_cols[0]) % GRID_SIZE
        print(f"CoM row displacement: {row_disp:.2f} (East motion)")
        print(f"CoM col displacement: {col_disp:.2f} (N/S scatter)")

    # Classify collision outcome
    if final_bits == initial_bits and conserved:
        outcome = "elastic (bits conserved throughout — gliders passed through or fused & re-split)"
    elif final_bits == initial_bits and not conserved:
        outcome = "partially inelastic (bits fluctuate mid-sim, recover to initial count)"
    elif final_bits == 2 * initial_bits // 2 and final_bits > 0:
        outcome = f"possible fuse or scatter (final={final_bits})"
    elif final_bits > 0 and final_bits != initial_bits:
        outcome = f"inelastic scatter (final={final_bits}, initial={initial_bits})"
    elif final_bits == 0:
        outcome = "annihilation (all bits destroyed)"
    else:
        outcome = f"unknown (final={final_bits})"
    print(f"Collision outcome:   {outcome}")

    # Bit-count trace around first deviation
    if deviation_step is not None:
        lo = max(0, deviation_step - 3)
        hi = min(len(bit_counts) - 1, deviation_step + 25)
        print(f"\nBit-count trace around first deviation (steps {lo}-{hi}):")
        for s in range(lo, hi + 1):
            marker = " <-- first deviation" if s == deviation_step else ""
            print(f"  step {s:4d}: {bit_counts[s]}{marker}")

    # Late-stage bit counts to see if stabilized
    print(f"\nLate-stage bit counts (steps 480-500):")
    for s in range(480, 501):
        print(f"  step {s:4d}: {bit_counts[s]}")

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
        "Parallel Glancing Collision — g10_rule_001 — 500 steps\n"
        "(Both East-bound, 2-col N/S offset)",
        color="white", fontsize=9,
    )
    ax.set_xlabel("col (N/S axis)", color="white")
    ax.set_ylabel("row (E/W axis)", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")

    # Zoom in on center region to see gliders clearly
    zoom = 40
    cx, cy = 64, 64
    ax.set_xlim(cy - zoom, cy + zoom)
    ax.set_ylim(cx + zoom, cx - zoom)  # flip for East=down display

    img = ax.imshow(
        frames[0][1], origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
        extent=[0, GRID_SIZE, GRID_SIZE, 0],
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
    print(f"  deviation_step:  {deviation_step}")
    print(f"  outcome:         {outcome}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
