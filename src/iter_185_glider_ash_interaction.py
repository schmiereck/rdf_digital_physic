#!/usr/bin/env python3
"""
iter_185_glider_ash_interaction.py — Can a glider perturb the 192-bit ash?

Stage 1: Reproduce 192-bit ash from iter_181 head-on collision.
         Glider A (East)  at [(32,64),(33,64),(33,65)]
         Glider B (West)  at [(96,64),(95,64),(95,63)]
         Simulate 300 steps until ash fully stabilizes.

Stage 2: Introduce a fresh 3-bit L-tromino glider aimed at the ash center
         (~row 64, col 64). Simulate 560 steps (≥500 post-collision).

Output: archive/iter_185/results/glider_ash_interaction.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
OUT_DIR      = PROJECT_ROOT / "archive" / "iter_185" / "results"
GIF_PATH     = OUT_DIR / "glider_ash_interaction.gif"

GRID_SIZE    = 128
STAGE1_STEPS = 300   # enough to stabilize the 192-bit ash

# Head-on collision gliders (same as iter_181)
GLIDER_A = [(32, 64), (33, 64), (33, 65)]   # East-moving
GLIDER_B = [(96, 64), (95, 64), (95, 63)]   # West-moving (C2 rotation)

# Glider C position is chosen dynamically after Stage 1 to avoid overlapping ash.
# Target col ~63-64 so it travels toward ash centre (row~64, col~63).
GLIDER_C_COL = 63   # target column for the glider

STAGE2_STEPS = 560   # ~60 steps travel + 500 post-collision

FRAME_EVERY  = 4     # 140 frames for 560 steps
FRAME_MS     = 60    # ~16 fps


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
    print("=== Glider-Ash Interaction — g10_rule_001 ===")
    lut = load_lut()
    print(f"LUT non-zero entries: {int(lut.sum())}\n")

    # ── Stage 1: Generate 192-bit ash ─────────────────────────────────────────
    print(f"STAGE 1: Head-on collision -> ash  ({STAGE1_STEPS} steps)")
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in GLIDER_A:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    for r, c in GLIDER_B:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1

    print(f"  Initial bits: {int(grid.sum())}  (expected 6)")
    for step in range(1, STAGE1_STEPS + 1):
        grid = step_grid(grid, lut)
        if step % 50 == 0:
            print(f"  step {step:4d}: bits={int(grid.sum())}")

    ash_bits = int(grid.sum())
    ash_com_row, ash_com_col = center_of_mass(grid)
    print(f"\nStage 1 done. ash_bits={ash_bits}  CoM=({ash_com_row:.1f}, {ash_com_col:.1f})")

    # Print ash row/col span for situational awareness
    ash_rows_idx, ash_cols_idx = np.where(grid > 0)
    print(f"  Ash row span: {ash_rows_idx.min()}..{ash_rows_idx.max()}"
          f"  col span: {ash_cols_idx.min()}..{ash_cols_idx.max()}")

    # Find a placement for glider C.
    # Strategy: scan candidate columns from target outward; for each col, find the
    # first row pair (r, r+1) where both cells (col, col+1) are empty.
    # If ash spans all rows in target cols, we accept an adjacent col offset.
    ash_center_row = int(round(ash_com_row))

    def find_clear_slot(grid, start_col, col_offsets=(0, -1, 1, -2, 2)):
        """Return (start_row, col) of first clear 2x2 block for L-tromino."""
        for dc in col_offsets:
            col = (start_col + dc) % GRID_SIZE
            col1 = (col + 1) % GRID_SIZE
            for r in range(GRID_SIZE):
                r1 = (r + 1) % GRID_SIZE
                if (grid[r, col] == 0 and grid[r1, col] == 0
                        and grid[r, col1] == 0 and grid[r1, col1] == 0):
                    return r, col
        return None, None

    glider_c_row, glider_c_col = find_clear_slot(grid, GLIDER_C_COL)
    if glider_c_row is None:
        print("ERROR: No clear 2x2 slot found anywhere near ash cols!")
        return 1

    # Standard L-tromino: [(r,c),(r+1,c),(r+1,c+1)] — East-moving
    glider_c = [
        (glider_c_row,       glider_c_col),
        (glider_c_row + 1,   glider_c_col),
        (glider_c_row + 1,   glider_c_col + 1),
    ]
    print(f"\n  Glider C placed at: {glider_c}  (col offset from target: {glider_c_col - GLIDER_C_COL})")

    # Compute travel distance to ash center on the torus (East = increasing row)
    travel_steps   = (ash_center_row - glider_c_row) % GRID_SIZE
    print(f"  Estimated steps to reach ash center row {ash_center_row}: ~{travel_steps}")
    actual_stage2_steps = max(STAGE2_STEPS, travel_steps + 510)
    if actual_stage2_steps != STAGE2_STEPS:
        print(f"  Extending simulation: travel ({travel_steps}) + 510 = {actual_stage2_steps} steps")

    # ── Stage 2: Glider-ash interaction ───────────────────────────────────────
    print(f"\nSTAGE 2: Introducing L-tromino glider C at {glider_c}")
    for r, c in glider_c:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1

    ash_plus_glider_bits = int(grid.sum())
    print(f"  Bits after adding glider C: {ash_plus_glider_bits}"
          f"  (ash={ash_bits} + 3 glider = expected {ash_bits+3})")

    frames     = [(0, grid.copy())]
    bit_counts = [ash_plus_glider_bits]

    # Detect first deviation from (ash_bits + 3) as proxy for collision
    pre_collision_bits = ash_plus_glider_bits
    collision_step     = None

    print(f"\n  {'step':>6}  {'bits':>6}")
    print("  " + "-" * 16)

    for step in range(1, actual_stage2_steps + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        bit_counts.append(bc)

        if collision_step is None and bc != pre_collision_bits:
            collision_step = step
            print(f"  COLLISION detected at step {step}: bits {pre_collision_bits} -> {bc}")

        if step % FRAME_EVERY == 0:
            frames.append((step, grid.copy()))

        if step % 50 == 0:
            print(f"  {step:>6}  {bc:>6}")

    final_bits = int(grid.sum())
    min_bits   = min(bit_counts)
    max_bits   = max(bit_counts)

    print(f"\nStage 2 done.")
    print(f"  ash_initial_bits:  {ash_bits}")
    print(f"  final_bits:        {final_bits}")
    print(f"  min_bits:          {min_bits}")
    print(f"  max_bits:          {max_bits}")
    print(f"  collision_step:    {collision_step}")

    # Classify outcome relative to ash_bits
    delta = final_bits - ash_bits
    if collision_step is None:
        outcome = "no interaction: glider never contacted ash"
    elif abs(delta) <= 3:
        outcome = f"ash nearly unchanged (delta={delta:+d}): glider absorbed/annihilated"
    elif delta > 3:
        outcome = f"ash grew by {delta} bits: glider catalyzed new structure"
    else:
        outcome = f"ash shrunk by {-delta} bits: glider partially destroyed ash"
    print(f"  outcome:           {outcome}")

    # Late-stage bit count trace
    actual_steps = len(bit_counts) - 1
    print(f"\nLate-stage bit counts (steps {actual_steps-20}-{actual_steps}):")
    for s in range(max(0, actual_steps - 20), actual_steps + 1):
        print(f"  step {s:4d}: {bit_counts[s]}")

    # ── Animation ─────────────────────────────────────────────────────────────
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
        f"Glider-Ash Interaction - g10_rule_001\n"
        f"Ash {ash_bits}b + L-tromino -> final {final_bits}b",
        color="white", fontsize=9,
    )
    ax.set_xlabel("col (N/S axis)", color="white")
    ax.set_ylabel("row (E/W axis)", color="white")
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")

    # Zoom to ash region with some margin
    zoom = 50
    cx = int(ash_com_row) if ash_com_row else 64
    cy = int(ash_com_col) if ash_com_col else 64
    ax.set_xlim(cy - zoom, cy + zoom)
    ax.set_ylim(cx + zoom, cx - zoom)  # flip so East is down

    img = ax.imshow(
        frames[0][1], origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
        extent=[0, GRID_SIZE, GRID_SIZE, 0],
    )
    info = ax.text(
        0.02, 0.97, f"step=0  bits={ash_plus_glider_bits}",
        transform=ax.transAxes, color="white", fontsize=9, va="top",
    )

    def update(frame_idx):
        step_n, g = frames[frame_idx]
        img.set_data(g)
        info.set_text(f"step={step_n}  bits={bit_counts[step_n]}")
        return img, info

    ani = animation.FuncAnimation(
        fig, update, frames=len(frames), interval=FRAME_MS, blit=True,
    )
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print(f"\n=== Summary ===")
    print(f"  ash_initial_bits:  {ash_bits}")
    print(f"  final_bits:        {final_bits}")
    print(f"  min_bits:          {min_bits}")
    print(f"  max_bits:          {max_bits}")
    print(f"  collision_step:    {collision_step}")
    print(f"  outcome:           {outcome}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
