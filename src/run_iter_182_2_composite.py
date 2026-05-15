#!/usr/bin/env python3
"""
run_iter_182_2_composite.py — Characterize isolated 5-bit composite glider on 256x256 grid.

archive/iter_181/results/glider_bit_collision_end.npy was not saved in iter_181.3.
We reconstruct the 5-bit composite by running the collision experiment (L-tromino +
single target bit on 128x128) for 100 warmup steps, then extract the 5-bit particle,
center it on a clean 256x256 toroidal grid, and simulate for 800 additional steps.

Outputs:
  archive/iter_182/results/composite_glider_properties.csv
  archive/iter_182/results/composite_glider.gif
"""

import csv
import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
CHAMP_PATH = PROJECT_ROOT / "archive" / "iter_179" / "results" / "champion_rule.json"
NPY_PATH   = PROJECT_ROOT / "archive" / "iter_181" / "results" / "glider_bit_collision_end.npy"
CSV_PATH   = PROJECT_ROOT / "archive" / "iter_182" / "results" / "composite_glider_properties.csv"
GIF_PATH   = PROJECT_ROOT / "archive" / "iter_182" / "results" / "composite_glider.gif"

GRID_SIZE    = 256
SIM_STEPS    = 800
WARMUP_STEPS = 100   # steps on 128x128 to form stable 5-bit composite
WARMUP_GRID  = 128
FRAME_EVERY  = 4     # ~200 frames total
FRAME_MS     = 40    # 25 fps
WIN_HALF     = 30    # 60x60 tracking window

# Initial conditions for the collision experiment (same as iter_181.3)
GLIDER_CELLS = [(32, 64), (33, 64), (33, 65)]
TARGET_CELL  = (64, 64)


# ── CA primitives ────────────────────────────────────────────────────────────

def load_rule() -> np.ndarray:
    print(f"Loading rule from {CHAMP_PATH}")
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


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def extract_window(grid: np.ndarray, com_row: float, com_col: float) -> np.ndarray:
    r_c = int(round(com_row)) % GRID_SIZE
    c_c = int(round(com_col)) % GRID_SIZE
    shifted = np.roll(
        np.roll(grid, GRID_SIZE // 2 - r_c, axis=0),
        GRID_SIZE // 2 - c_c, axis=1,
    )
    h = GRID_SIZE // 2
    return shifted[h - WIN_HALF: h + WIN_HALF, h - WIN_HALF: h + WIN_HALF]


# ── Particle reconstruction / isolation ──────────────────────────────────────

def reconstruct_composite(lut: np.ndarray) -> list:
    """Run collision on WARMUP_GRID for WARMUP_STEPS; return list of (row, col)."""
    grid = np.zeros((WARMUP_GRID, WARMUP_GRID), dtype=np.uint8)
    for r, c in GLIDER_CELLS:
        grid[r % WARMUP_GRID, c % WARMUP_GRID] = 1
    grid[TARGET_CELL[0] % WARMUP_GRID, TARGET_CELL[1] % WARMUP_GRID] = 1
    for _ in range(WARMUP_STEPS):
        grid = step_grid(grid, lut)
    bc = int(grid.sum())
    print(f"  Warmup complete: bit_count={bc}")
    xs, ys = np.where(grid > 0)
    return list(zip(xs.tolist(), ys.tolist()))


def isolate_5bit(cells: list) -> list:
    """If more than 5 bits, keep the 5 closest to the group centroid."""
    if len(cells) == 5:
        return cells
    if len(cells) < 5:
        print(f"  WARNING: only {len(cells)} bits — using all.")
        return cells
    print(f"  {len(cells)} bits found; trimming to 5 nearest centroid.")
    arr = np.array(cells, dtype=float)
    centroid = arr.mean(axis=0)
    dists = np.abs(arr - centroid).sum(axis=1)
    idx = np.argsort(dists)[:5]
    return [cells[i] for i in idx]


def center_cells(cells: list, target: int = GRID_SIZE // 2) -> list:
    """Shift cells so their centroid lands at (target, target)."""
    arr = np.array(cells, dtype=float)
    mean_r, mean_c = arr.mean(axis=0)
    dr = target - mean_r
    dc = target - mean_c
    centered = [(int(round(r + dr)) % GRID_SIZE, int(round(c + dc)) % GRID_SIZE)
                for r, c in cells]
    return centered


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    print("=== iter_182.2 — 5-bit Composite Glider Characterization (256x256) ===\n")

    lut = load_rule()
    print(f"LUT loaded: {len(lut)} entries, {int(lut.sum())} non-zero\n")

    # --- acquire particle ---
    if NPY_PATH.exists():
        print(f"Loading particle from {NPY_PATH}")
        src = np.load(str(NPY_PATH)).astype(np.uint8)
        print(f"  Source grid: {src.shape}  bits: {int(src.sum())}")
        xs, ys = np.where(src > 0)
        raw_cells = list(zip(xs.tolist(), ys.tolist()))
    else:
        print(f"File not found: {NPY_PATH}")
        print("Reconstructing 5-bit composite via warmup collision...")
        raw_cells = reconstruct_composite(lut)

    particle_cells = isolate_5bit(raw_cells)
    centered_cells = center_cells(particle_cells)
    print(f"Particle cells (centered): {sorted(centered_cells)}\n")

    # --- build 256x256 grid ---
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in centered_cells:
        grid[r, c] = 1

    initial_bc  = int(grid.sum())
    initial_com = center_of_mass(grid)
    print(f"Grid size:       {GRID_SIZE}x{GRID_SIZE}")
    print(f"Initial bits:    {initial_bc}")
    print(f"Initial CoM:     ({initial_com[0]:.3f}, {initial_com[1]:.3f})\n")

    # --- simulation ---
    bit_counts     = [initial_bc]
    com_rows       = [initial_com[0]]
    com_cols       = [initial_com[1]]
    # Unwrapped row position for clean velocity measurement
    unwrapped_rows = [initial_com[0]]
    frames         = [(0, extract_window(grid, initial_com[0], initial_com[1]))]

    csv_rows = [{
        "step": 0,
        "com_row": round(initial_com[0], 4),
        "com_col": round(initial_com[1], 4),
        "bit_count": initial_bc,
        "displacement_cells": 0.0,
    }]

    print(f"{'step':>6}  {'bits':>6}  {'com_row':>9}  {'com_col':>9}  {'displ':>8}")
    print("-" * 52)

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        bc   = int(grid.sum())
        com  = center_of_mass(grid)

        bit_counts.append(bc)
        com_rows.append(com[0])
        com_cols.append(com[1])

        if step % FRAME_EVERY == 0:
            frames.append((step, extract_window(grid, com[0], com[1])))

    # --- N_BITS-aware velocity + unwrapped trajectory ---
    # When k of the 5 cells cross the toroidal row boundary in one step, the
    # naive CoM delta is deflected by k * GRID_SIZE / N_BITS.  We recover the
    # true delta by rounding k = (v_est - raw_delta) * N_BITS / GRID_SIZE.
    N_BITS = 5
    settle = 20

    raw_deltas = []
    raw_steps  = []
    for s in range(settle + 1, SIM_STEPS + 1):
        if bit_counts[s] == N_BITS and bit_counts[s - 1] == N_BITS:
            raw_deltas.append(com_rows[s] - com_rows[s - 1])
            raw_steps.append(s)

    velocity, vel_std, r_sq = float("nan"), float("nan"), 0.0
    unwrapped_rows = [com_rows[0]] * (SIM_STEPS + 1)  # default; overwritten below

    if len(raw_deltas) > 10:
        # Pass 1: v_est from unambiguous positive steps (no boundary crossing)
        positive = [d for d in raw_deltas if d > 0.5]
        v_est = float(np.mean(positive)) if positive else 1.0

        # Pass 2: correct each delta
        corrected = []
        for d in raw_deltas:
            k = int(round((v_est - d) * N_BITS / GRID_SIZE))
            corrected.append(d + k * GRID_SIZE / N_BITS)

        velocity = float(np.mean(corrected))
        vel_std  = float(np.std(corrected))

        # Build fully unwrapped position series
        unwrapped_rows[raw_steps[0] - 1] = com_rows[raw_steps[0] - 1]
        for i, s in enumerate(raw_steps):
            unwrapped_rows[s] = unwrapped_rows[s - 1] + corrected[i]

        # Linear regression
        steps_arr = np.array([raw_steps[0] - 1] + raw_steps, dtype=float)
        pos_arr   = np.array(
            [unwrapped_rows[raw_steps[0] - 1]] + [unwrapped_rows[s] for s in raw_steps],
            dtype=float,
        )
        coeffs   = np.polyfit(steps_arr, pos_arr, 1)
        velocity = float(coeffs[0])
        residuals = pos_arr - np.polyval(coeffs, steps_arr)
        vel_std  = float(np.std(residuals))
        r_sq     = float(np.corrcoef(steps_arr, pos_arr)[0, 1] ** 2)

    # --- fill in CSV rows with proper displacement (unwrapped) ---
    for step in range(100, SIM_STEPS + 1, 100):
        displ = abs(unwrapped_rows[step] - unwrapped_rows[0])
        bc    = bit_counts[step]
        print(f"{step:>6}  {bc:>6}  {com_rows[step]:>9.3f}  {com_cols[step]:>9.3f}  {displ:>8.3f}")
        csv_rows.append({
            "step": step,
            "com_row": round(com_rows[step], 4),
            "com_col": round(com_cols[step], 4),
            "bit_count": bc,
            "displacement_cells": round(displ, 4),
        })

    # --- stability ---
    post_bits  = bit_counts[settle:]
    is_stable  = all(b == 5 for b in post_bits)
    final_bc   = bit_counts[-1]
    final_com  = (com_rows[-1], com_cols[-1])

    print()
    print("=== Results ===")
    print(f"Initial bits:    {initial_bc}")
    print(f"Final bits:      {final_bc}")
    print(f"Stable (all==5): {is_stable}")
    print(f"Velocity:        {velocity:.6f} cells/step")
    print(f"Vel std dev:     {vel_std:.6f}")
    print(f"R²:              {r_sq:.6f}")
    print(f"Final CoM:       ({final_com[0]:.3f}, {final_com[1]:.3f})")

    # --- save CSV ---
    CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["step", "com_row", "com_col", "bit_count", "displacement_cells"]
        )
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"\nCSV saved: {CSV_PATH}")

    # --- animation ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation

    vel_str = f"{velocity:.3f}" if not np.isnan(velocity) else "n/a"
    fig, ax = plt.subplots(figsize=(5, 5), dpi=100)
    fig.patch.set_facecolor("black")
    ax.set_facecolor("black")
    ax.set_title(
        f"5-bit Composite Glider (256×256) — g10_rule_001\nv = {vel_str} cells/step",
        color="white", fontsize=10,
    )
    ax.set_xlabel("col (relative)", color="white", fontsize=8)
    ax.set_ylabel("row (relative)", color="white", fontsize=8)
    ax.tick_params(colors="white")
    for spine in ax.spines.values():
        spine.set_edgecolor("white")

    step0, win0 = frames[0]
    img  = ax.imshow(win0, origin="upper", interpolation="nearest", cmap="hot", vmin=0, vmax=1)
    info = ax.text(
        0.02, 0.97, f"step={step0}  bits={bit_counts[0]}",
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
    ani.save(str(GIF_PATH), writer="pillow", fps=1000 // FRAME_MS)
    plt.close(fig)
    print(f"Animation saved: {GIF_PATH}")

    print("\n=== Summary ===")
    print(f"  grid_size:       {GRID_SIZE}")
    print(f"  sim_steps:       {SIM_STEPS}")
    print(f"  initial_bits:    {initial_bc}")
    print(f"  final_bits:      {final_bc}")
    print(f"  stable:          {is_stable}")
    print(f"  velocity:        {velocity:.6f}")
    print(f"  vel_std:         {vel_std:.6f}")
    print(f"  r_squared:       {r_sq:.6f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
