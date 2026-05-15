#!/usr/bin/env python3
"""
run_iter_184_glancing.py — Glancing collision of two opposing v=1c 3-bit gliders.

Setup:
  - 256x256 toroidal hexagonal grid
  - Rule: g10_rule_001  (from archive/iter_179/results/champion_rule.json)
  - Glider A: L-tromino centered at (64, 128),  moving East (+row)
  - Glider B: L-tromino centered at (192, 130), moving West (-row)
  - Lateral (col-axis) offset: exactly 2 cells  → glancing interaction
  - 200 simulation steps

Outputs:
  archive/iter_184/results/glancing_collision.gif
  archive/iter_184/results/glancing_collision.json
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
GIF_PATH     = PROJECT_ROOT / "archive" / "iter_184" / "results" / "glancing_collision.gif"
JSON_PATH    = PROJECT_ROOT / "archive" / "iter_184" / "results" / "glancing_collision.json"

GRID_SIZE  = 256
SIM_STEPS  = 200
FRAME_EVERY = 2
FRAME_MS   = 60  # ~17 fps

# East (+row) L-tromino offsets, same as iter_179/180
EAST_OFFSETS = [(0, 0), (1, 0), (1, 1)]

# West (-row) L-tromino offsets — as validated in iter_180 head-on collision
# Shape: (r,c), (r,c+1), (r+1,c+1) → moves West (-row) under g10_rule_001
WEST_OFFSETS = [(0, 0), (0, 1), (1, 1)]

# Glider anchor positions (row, col)
GA_POS = (64, 128)   # Glider A — East
GB_POS = (192, 130)  # Glider B — West; col offset = 2


def load_rule() -> np.ndarray:
    with open(RULE_PATH) as f:
        data = json.load(f)
    print(f"Rule: {data['rule_id']}  fitness={data['fitness']}")
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


def place_glider(grid: np.ndarray, anchor: tuple, offsets: list) -> list:
    cells = []
    for dr, dc in offsets:
        r = (anchor[0] + dr) % GRID_SIZE
        c = (anchor[1] + dc) % GRID_SIZE
        grid[r, c] = 1
        cells.append((r, c))
    return cells


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def crop_window(grid: np.ndarray, row_c: int, col_c: int,
                half_h: int, half_w: int) -> np.ndarray:
    rows = np.arange(row_c - half_h, row_c + half_h) % GRID_SIZE
    cols = np.arange(col_c - half_w, col_c + half_w) % GRID_SIZE
    return grid[np.ix_(rows, cols)]


def classify_outcome(initial_bc: int, bit_counts: list) -> str:
    final_bc = bit_counts[-1]
    late_counts = bit_counts[int(len(bit_counts) * 0.7):]  # last 30% of simulation
    if final_bc == 0:
        return "Annihilation"
    if final_bc == initial_bc and all(b == initial_bc for b in late_counts):
        return "Passing Through"
    if final_bc == initial_bc and any(b != initial_bc for b in bit_counts):
        return "Elastic Scattering"
    if final_bc < initial_bc:
        return "Partial Annihilation"
    return "Inelastic Fusion"


def main() -> int:
    print("=== iter_184 — Glancing Collision Experiment (256x256) ===\n")

    lut = load_rule()

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    ga_cells = place_glider(grid, GA_POS, EAST_OFFSETS)
    gb_cells = place_glider(grid, GB_POS, WEST_OFFSETS)

    initial_bc  = int(grid.sum())
    initial_com = center_of_mass(grid)
    lateral_offset = abs(GB_POS[1] - GA_POS[1])

    print(f"Glider A: anchor={GA_POS}  cells={ga_cells}  direction=East(+row)")
    print(f"Glider B: anchor={GB_POS}  cells={gb_cells}  direction=West(-row)")
    print(f"Lateral (col) offset: {lateral_offset} cells")
    print(f"Row separation:       {abs(GB_POS[0] - GA_POS[0])} cells")
    print(f"Initial bit count:    {initial_bc}")
    print()

    # Fixed crop: centered on collision zone (midrow, midcol)
    col_mid  = (GA_POS[1] + GB_POS[1]) // 2   # ~129
    row_mid  = (GA_POS[0] + GB_POS[0]) // 2   # 128
    half_w   = 30
    half_h   = 80   # gliders travel ~64 rows to meet

    bit_counts = [initial_bc]
    frames     = [(0, crop_window(grid, row_mid, col_mid, half_h, half_w))]

    print(f"{'step':>6}  {'bits':>6}  {'com_row':>9}  {'com_col':>9}")
    print("-" * 42)
    print(f"{0:>6}  {initial_bc:>6}  {initial_com[0]:>9.3f}  {initial_com[1]:>9.3f}")

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        bit_counts.append(bc)

        if step % FRAME_EVERY == 0:
            frames.append((step, crop_window(grid, row_mid, col_mid, half_h, half_w)))

        if step % 20 == 0:
            com = center_of_mass(grid)
            print(f"{step:>6}  {bc:>6}  {com[0]:>9.3f}  {com[1]:>9.3f}")

    final_bc = bit_counts[-1]
    max_bc   = max(bit_counts)
    min_bc   = min(bit_counts)
    outcome  = classify_outcome(initial_bc, bit_counts)

    print()
    print("=== Results ===")
    print(f"Initial bits:     {initial_bc}")
    print(f"Final bits:       {final_bc}")
    print(f"Bit range:        min={min_bc}  max={max_bc}")
    print(f"Outcome:          {outcome}")

    # --- Save JSON ---
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "rule_id":             "g10_rule_001",
        "grid_size":           GRID_SIZE,
        "sim_steps":           SIM_STEPS,
        "lateral_offset":      lateral_offset,
        "glider_a_anchor":     list(GA_POS),
        "glider_b_anchor":     list(GB_POS),
        "initial_bits":        initial_bc,
        "final_bits":          final_bc,
        "min_bits":            min_bc,
        "max_bits":            max_bc,
        "outcome_description": outcome,
        "bit_counts":          bit_counts,
    }
    with open(JSON_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"JSON saved: {JSON_PATH}")

    # --- Animation ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    crop_h = 2 * half_h
    crop_w = 2 * half_w
    print(f"\nGenerating animation ({len(frames)} frames, crop {crop_h}x{crop_w}) ...")

    fig, ax = plt.subplots(figsize=(6, 10), dpi=100)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title(
        f"Glancing Collision — g10_rule_001\n"
        f"A=East(r=64,c=128) vs B=West(r=192,c=130)  lateral_off={lateral_offset}",
        color="white", fontsize=9,
    )
    ax.set_xlabel("col (relative)", color="white", fontsize=8)
    ax.set_ylabel("row (fixed view)", color="white", fontsize=8)
    ax.tick_params(colors="white")
    for sp in ax.spines.values():
        sp.set_edgecolor("white")

    s0, win0 = frames[0]
    img = ax.imshow(
        win0, origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
        extent=[-half_w, half_w, half_h, -half_h],
    )
    info = ax.text(
        0.02, 0.97, f"step={s0}  bits={bit_counts[s0]}",
        transform=ax.transAxes, color="white", fontsize=9, va="top",
    )

    def update(fi: int):
        s, win = frames[fi]
        img.set_data(win)
        info.set_text(f"step={s}  bits={bit_counts[s]}")
        return img, info

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=FRAME_MS, blit=True,
    )
    GIF_PATH.parent.mkdir(parents=True, exist_ok=True)
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print("\n=== Summary ===")
    print(f"  initial_bits:     {initial_bc}")
    print(f"  final_bits:       {final_bc}")
    print(f"  min_bits:         {min_bc}")
    print(f"  max_bits:         {max_bc}")
    print(f"  lateral_offset:   {lateral_offset}")
    print(f"  outcome:          {outcome}")
    print(f"  gif:              {GIF_PATH}")
    print(f"  json:             {JSON_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
