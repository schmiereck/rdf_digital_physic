#!/usr/bin/env python3
"""
run_iter_182_3_glancing.py — Glancing (off-axis) collision of two 3-bit v=1c gliders.

Setup:
  - 256x256 toroidal hexagonal grid
  - Glider 1: L-tromino from iter_179, centered at row=128, col=100 → moves East (+row)
  - Glider 2: identical L-tromino, centered at row=128, col=154 → moves East (+row)
  - Both gliders move in the same direction (East/+row) with same column offset (54 cols apart)
  - 300 simulation steps using g10_rule_001

Outputs:
  archive/iter_182/results/glancing_collision_report.txt
  archive/iter_182/results/glancing_collision.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
REPORT_PATH  = PROJECT_ROOT / "archive" / "iter_182" / "results" / "glancing_collision_report.txt"
GIF_PATH     = PROJECT_ROOT / "archive" / "iter_182" / "results" / "glancing_collision.gif"

GRID_SIZE  = 256
SIM_STEPS  = 300
FRAME_EVERY = 2
FRAME_MS   = 60  # ~17 fps

# L-tromino seed: relative offsets (dr, dc) from centroid anchor
# Pattern: (0,0),(+1,0),(+1,+1) — same orientation as iter_179/180 glider
# This orientation moves East (+row direction) under g10_rule_001
GLIDER_OFFSETS = [(0, 0), (1, 0), (1, 1)]

# Centroid anchors as specified in the task (row, col)
G1_CENTER = (128, 100)
G2_CENTER = (128, 154)


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
    se = np.roll(e,  1, axis=1)
    nw = np.roll(w, -1, axis=1)
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


def place_glider(grid: np.ndarray, center_row: int, center_col: int) -> None:
    for dr, dc in GLIDER_OFFSETS:
        r = (center_row + dr) % GRID_SIZE
        c = (center_col + dc) % GRID_SIZE
        grid[r, c] = 1


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def crop_around(grid: np.ndarray, row_c: int, col_c: int, half_h: int, half_w: int) -> np.ndarray:
    """Extract a crop centered at (row_c, col_c) using toroidal wrapping."""
    rows = np.arange(row_c - half_h, row_c + half_h) % GRID_SIZE
    cols = np.arange(col_c - half_w, col_c + half_w) % GRID_SIZE
    return grid[np.ix_(rows, cols)]


def main() -> int:
    print("=== iter_182.3 — Glancing Collision Experiment (256x256) ===\n")

    lut = load_rule()

    # Build initial grid
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    place_glider(grid, G1_CENTER[0], G1_CENTER[1])
    place_glider(grid, G2_CENTER[0], G2_CENTER[1])

    g1_cells = [(G1_CENTER[0] + dr, G1_CENTER[1] + dc) for dr, dc in GLIDER_OFFSETS]
    g2_cells = [(G2_CENTER[0] + dr, G2_CENTER[1] + dc) for dr, dc in GLIDER_OFFSETS]

    initial_bc  = int(grid.sum())
    initial_com = center_of_mass(grid)

    print(f"Glider 1 center:  {G1_CENTER}  cells: {g1_cells}")
    print(f"Glider 2 center:  {G2_CENTER}  cells: {g2_cells}")
    print(f"Column separation: {abs(G2_CENTER[1] - G1_CENTER[1])} cells")
    print(f"Initial bit count: {initial_bc}")
    print(f"Initial CoM:       ({initial_com[0]:.3f}, {initial_com[1]:.3f})")
    print()

    # Determine crop window — fixed midpoint between the two gliders in column axis
    col_mid = (G1_CENTER[1] + G2_CENTER[1]) // 2    # ~127
    half_w  = (abs(G2_CENTER[1] - G1_CENTER[1]) // 2) + 20  # +20 px margin each side
    half_h  = 40  # track row movement

    # Simulation
    bit_counts   = [initial_bc]
    com_rows     = [initial_com[0]]
    com_cols     = [initial_com[1]]
    frames       = []

    def capture_frame(g, step):
        # Track row by current CoM row; col is fixed midpoint
        row_c = int(round(center_of_mass(g)[0])) % GRID_SIZE
        frames.append((step, crop_around(g, row_c, col_mid, half_h, half_w)))

    capture_frame(grid, 0)

    print(f"{'step':>6}  {'bits':>6}  {'com_row':>9}  {'com_col':>9}")
    print("-" * 42)
    print(f"{0:>6}  {initial_bc:>6}  {initial_com[0]:>9.3f}  {initial_com[1]:>9.3f}")

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        com  = center_of_mass(grid)

        bit_counts.append(bc)
        com_rows.append(com[0])
        com_cols.append(com[1])

        if step % FRAME_EVERY == 0:
            capture_frame(grid, step)

        if step % 50 == 0:
            print(f"{step:>6}  {bc:>6}  {com[0]:>9.3f}  {com[1]:>9.3f}")

    final_bc  = bit_counts[-1]
    final_com = (com_rows[-1], com_cols[-1])
    max_bc    = max(bit_counts)
    min_bc    = min(bit_counts)

    # --- Qualitative analysis ---
    # Determine if the bit count ever deviated from initial
    counts_after_settle = bit_counts[10:]
    always_6   = all(b == 6 for b in counts_after_settle)
    any_deviate = any(b != 6 for b in bit_counts)
    min_after_settle = min(counts_after_settle)
    max_after_settle = max(counts_after_settle)

    col_separation = abs(G2_CENTER[1] - G1_CENTER[1])

    if final_bc == 0:
        outcome = "annihilation"
    elif final_bc == initial_bc and always_6:
        outcome = "no_interaction_parallel_motion"
    elif final_bc < initial_bc:
        outcome = "partial_annihilation_or_absorption"
    else:
        outcome = "creation_or_fusion"

    print()
    print("=== Results ===")
    print(f"Initial bits:       {initial_bc}")
    print(f"Final bits:         {final_bc}")
    print(f"Bit range:          min={min_bc}  max={max_bc}")
    print(f"Always 6 (after 10): {always_6}")
    print(f"Any deviation:      {any_deviate}")
    print(f"Outcome:            {outcome}")
    print(f"Column separation:  {col_separation} cells")

    # --- Save report ---
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("=== iter_182.3: Glancing Collision Experiment ===\n\n")
        f.write(f"Rule:              g10_rule_001\n")
        f.write(f"Grid size:         {GRID_SIZE}x{GRID_SIZE} (toroidal hexagonal)\n")
        f.write(f"Simulation steps:  {SIM_STEPS}\n\n")
        f.write(f"Setup:\n")
        f.write(f"  Glider 1: centered at {G1_CENTER}, cells {g1_cells}\n")
        f.write(f"  Glider 2: centered at {G2_CENTER}, cells {g2_cells}\n")
        f.write(f"  Both gliders: identical L-tromino orientation (East/+row motion)\n")
        f.write(f"  Column separation: {col_separation} cells\n\n")
        f.write(f"Results:\n")
        f.write(f"  Initial bit count:  {initial_bc}\n")
        f.write(f"  Final bit count:    {final_bc}\n")
        f.write(f"  Min bit count:      {min_bc}\n")
        f.write(f"  Max bit count:      {max_bc}\n")
        f.write(f"  Outcome:            {outcome}\n\n")
        f.write(f"Bit count over time:\n")
        f.write(f"{'step':>6}  {'bits':>6}  {'com_row':>9}  {'com_col':>9}\n")
        f.write("-" * 36 + "\n")
        for s in range(0, SIM_STEPS + 1, 10):
            f.write(f"{s:>6}  {bit_counts[s]:>6}  {com_rows[s]:>9.3f}  {com_cols[s]:>9.3f}\n")
        f.write("\n")
        f.write("Qualitative Analysis:\n")
        f.write(f"  The two L-tromino gliders were placed at the same row (row 128)\n")
        f.write(f"  but separated by {col_separation} columns (col 100 vs col 154).\n")
        f.write(f"  Both gliders carry the same orientation and move East (+row direction)\n")
        f.write(f"  under rule g10_rule_001.\n\n")
        if always_6:
            f.write(f"  OUTCOME: No interaction detected. The two gliders propagate in\n")
            f.write(f"  parallel, maintaining their {col_separation}-column lateral separation\n")
            f.write(f"  throughout all {SIM_STEPS} steps. The bit count remains constant at\n")
            f.write(f"  {final_bc} (3+3), confirming independent motion with no interaction.\n\n")
            f.write(f"  This demonstrates that at large impact parameters ({col_separation} cells),\n")
            f.write(f"  same-direction gliders are effectively non-interacting.\n")
        else:
            f.write(f"  OUTCOME: Interaction detected (bits deviated from 6).\n")
            f.write(f"  Bit range during simulation: {min_bc} to {max_bc}.\n")
            f.write(f"  Final bit count: {final_bc}.\n")
        f.write("\n")
        f.write("Comparison with previous experiments:\n")
        f.write("  - Head-on collision (iter_180): catastrophic annihilation / non-trivial\n")
        f.write("    outcome when gliders travel toward each other on the same column\n")
        f.write("  - Constructive fusion (iter_181): glider + single lone bit fuse into\n")
        f.write("    a stable 5-bit composite glider\n")
        f.write(f"  - Glancing collision (this, impact_param={col_separation}): {outcome}\n")
    print(f"\nReport saved: {REPORT_PATH}")

    # --- Animation ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    crop_h = 2 * half_h
    crop_w = 2 * half_w

    print(f"\nGenerating animation ({len(frames)} frames, crop {crop_h}x{crop_w}) ...")

    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title(
        f"Glancing Collision — g10_rule_001\n"
        f"Both gliders East (+row), col-sep={col_separation}",
        color="white", fontsize=10,
    )
    ax.set_xlabel("col (relative to midpoint)", color="white", fontsize=8)
    ax.set_ylabel("row (tracking)", color="white", fontsize=8)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")

    step0, win0 = frames[0]
    img = ax.imshow(
        win0, origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
        extent=[-half_w, half_w, half_h, -half_h],
    )
    info = ax.text(
        0.02, 0.97,
        f"step={step0}  bits={bit_counts[step0]}",
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
    print(f"  grid_size:        {GRID_SIZE}")
    print(f"  sim_steps:        {SIM_STEPS}")
    print(f"  initial_bits:     {initial_bc}")
    print(f"  final_bits:       {final_bc}")
    print(f"  min_bits:         {min_bc}")
    print(f"  max_bits:         {max_bc}")
    print(f"  col_separation:   {col_separation}")
    print(f"  outcome:          {outcome}")
    print(f"  report:           {REPORT_PATH}")
    print(f"  gif:              {GIF_PATH}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
