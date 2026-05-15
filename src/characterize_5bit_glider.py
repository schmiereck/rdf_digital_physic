#!/usr/bin/env python3
"""
characterize_5bit_glider.py — Characterize the 5-bit composite glider from iter_181.3.

Same initial conditions as iter_181.3:
  - 128x128 toroidal grid
  - Glider: L-tromino at [(32,64),(33,64),(33,65)], moving East (+row)
  - Target: single stationary bit at (64,64)
  - 850 simulation steps
  - Rule: g10_rule_001

Goals:
  - Determine velocity of the 5-bit composite via linear regression on unwrapped CoM
  - Confirm stability (no bit loss/gain post-collision)
  - Save animation with glider-tracking window

Output: archive/iter_182/results/5bit_composite_glider.gif
"""

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH   = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
GIF_PATH     = PROJECT_ROOT / "archive" / "iter_182" / "results" / "5bit_composite_glider.gif"

GRID_SIZE   = 128
SIM_STEPS   = 850
FRAME_EVERY = 2      # ~425 frames
FRAME_MS    = 40     # 25 fps

GLIDER_CELLS = [(32, 64), (33, 64), (33, 65)]
TARGET_CELL  = (64, 64)
WIN_HALF     = 24    # half-size of tracking window (48x48 crop)


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


def extract_window(grid: np.ndarray, com_row: float, com_col: float) -> np.ndarray:
    """Return WIN_HALF*2 x WIN_HALF*2 crop centered on (com_row, com_col), toroidal."""
    r_c = int(round(com_row)) % GRID_SIZE
    c_c = int(round(com_col)) % GRID_SIZE
    shifted = np.roll(np.roll(grid, GRID_SIZE // 2 - r_c, axis=0),
                      GRID_SIZE // 2 - c_c, axis=1)
    h = GRID_SIZE // 2
    return shifted[h - WIN_HALF : h + WIN_HALF, h - WIN_HALF : h + WIN_HALF]


def main() -> int:
    print("=== iter_182.1 — Characterize 5-bit Composite Glider ===")
    print(f"Grid:         {GRID_SIZE}x{GRID_SIZE}")
    print(f"Glider cells: {GLIDER_CELLS}")
    print(f"Target cell:  {TARGET_CELL}")
    print(f"Steps:        {SIM_STEPS}\n")

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

    # Per-step tracking
    bit_counts  = [initial_bc]
    com_rows    = [initial_com[0]]
    com_cols    = [initial_com[1]]
    frames      = [(0, extract_window(grid, initial_com[0], initial_com[1]))]

    max_bits          = initial_bc
    collision_step    = None
    composite_step    = None

    print(f"{'step':>6}  {'bits':>6}  {'com_row':>8}  {'com_col':>8}")
    print("-" * 40)

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        com  = center_of_mass(grid)

        bit_counts.append(bc)
        com_rows.append(com[0])
        com_cols.append(com[1])

        if bc > max_bits:
            max_bits = bc
        if collision_step is None and bc != initial_bc:
            collision_step = step
        if composite_step is None and bc == 5:
            composite_step = step

        if step % FRAME_EVERY == 0:
            frames.append((step, extract_window(grid, com[0], com[1])))

        if step % 50 == 0:
            print(f"{step:>6}  {bc:>6}  {com[0]:>8.2f}  {com[1]:>8.2f}")

    final_bc  = bit_counts[-1]
    final_com = (com_rows[-1], com_cols[-1])

    # ── Velocity via n_bits-aware boundary correction + linear regression ─────
    # When k of the n_bits cells cross the toroidal boundary in one step, the
    # naive CoM delta is:  delta_raw = delta_true - k * GRID_SIZE / n_bits
    # We recover delta_true by rounding k = (v_est - delta_raw)*n_bits/GRID_SIZE
    N_BITS = 5
    settle = (composite_step or 1) + 20

    # Collect raw step-to-step deltas for stable region
    raw_deltas = []
    raw_steps  = []
    for s in range(settle + 1, SIM_STEPS + 1):
        if bit_counts[s] == N_BITS and bit_counts[s - 1] == N_BITS:
            raw_deltas.append(com_rows[s] - com_rows[s - 1])
            raw_steps.append(s)

    if len(raw_deltas) > 10:
        # Pass 1: estimate velocity from positive deltas (no boundary crossing)
        positive = [d for d in raw_deltas if d > 0.5]
        v_est = float(np.mean(positive)) if positive else 1.0

        # Pass 2: correct each delta for k boundary-crossing cells
        corrected = []
        for d in raw_deltas:
            k = int(round((v_est - d) * N_BITS / GRID_SIZE))
            corrected.append(d + k * GRID_SIZE / N_BITS)

        velocity = float(np.mean(corrected))
        vel_std  = float(np.std(corrected))

        # Build unwrapped position series and fit
        unwrapped = [com_rows[raw_steps[0] - 1]]
        for c in corrected:
            unwrapped.append(unwrapped[-1] + c)
        steps_arr = np.array([raw_steps[0] - 1] + raw_steps, dtype=float)
        pos_arr   = np.array(unwrapped, dtype=float)
        coeffs    = np.polyfit(steps_arr, pos_arr, 1)
        velocity  = float(coeffs[0])
        r_sq      = float(np.corrcoef(steps_arr, pos_arr)[0, 1] ** 2)
    else:
        velocity, r_sq, vel_std = float("nan"), 0.0, float("nan")
        raw_steps = []

    # ── Stability check ───────────────────────────────────────────────────────
    post_bits   = bit_counts[composite_step or 1:]
    is_stable   = all(b == 5 for b in post_bits)
    post_steps  = len(post_bits)

    print()
    print("=== Results ===")
    print(f"Initial bits:            {initial_bc}")
    print(f"Final bits:              {final_bc}")
    print(f"Max bits ever:           {max_bits}")
    print(f"Collision at step:       {collision_step}")
    print(f"5-bit composite formed:  {composite_step}")
    print(f"Post-formation steps:    {post_steps}")
    print(f"Stable (all bits==5):    {is_stable}")
    print(f"Velocity (cells/step):   {velocity:.6f}")
    print(f"Velocity std dev:        {vel_std:.6f}")
    print(f"R² of linear fit:        {r_sq:.6f}")
    print(f"Final CoM:               ({final_com[0]:.2f}, {final_com[1]:.2f})")

    # ── Animation ────────────────────────────────────────────────────────────
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    GIF_PATH.parent.mkdir(parents=True, exist_ok=True)
    n_frames = len(frames)
    print(f"\nGenerating animation ({n_frames} frames) -> {GIF_PATH}")

    vel_str = f"{velocity:.3f}" if not np.isnan(velocity) else "n/a"
    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title(
        f"5-bit Composite Glider — g10_rule_001\nv = {vel_str} cells/step",
        color="white", fontsize=10,
    )
    ax.set_xlabel("col (relative)", color="white", fontsize=8)
    ax.set_ylabel("row (relative)", color="white", fontsize=8)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")

    step0, win0 = frames[0]
    img = ax.imshow(
        win0, origin="upper", interpolation="nearest",
        cmap="hot", vmin=0, vmax=1,
    )
    info = ax.text(
        0.02, 0.97, f"step={step0}  bits={bit_counts[0]}",
        transform=ax.transAxes, color="white", fontsize=9, va="top",
    )

    def update(fi):
        step, win = frames[fi]
        img.set_data(win)
        info.set_text(f"step={step}  bits={bit_counts[step]}")
        return img, info

    ani = animation.FuncAnimation(
        fig, update, frames=n_frames, interval=FRAME_MS, blit=True,
    )
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print("\n=== Summary ===")
    print(f"  initial_bits:   {initial_bc}")
    print(f"  final_bits:     {final_bc}")
    print(f"  composite_step: {composite_step}")
    print(f"  stable:         {is_stable}")
    print(f"  velocity:       {velocity:.6f}")
    print(f"  vel_std:        {vel_std:.6f}")
    print(f"  r_squared:      {r_sq:.6f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
