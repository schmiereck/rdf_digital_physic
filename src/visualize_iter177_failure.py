#!/usr/bin/env python3
"""
visualize_iter177_failure.py

Load champion rule from iter_176 gen_5 (rule_019.json) and the L-tromino seed.
Run 500 steps on a 128x128 toroidal hexagonal grid, capturing each frame.
Generate an animated GIF showing the 'bloom-and-oscillate' failure mode.

Key visual cues:
  - Black cells = active bits
  - Red border = initial 3-cell seed region
  - Title shows step + bit_count to reveal bloom
  - Window tracks CoM to show oscillation / drift
"""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

PROJECT_ROOT  = Path(__file__).parent.parent
RULE_PATH     = PROJECT_ROOT / "archive" / "iter_176" / "results" / "gen_5" / "rule_019.json"
PARTICLE_PATH = PROJECT_ROOT / "archive" / "iter_176" / "results" / "best_particle.json"
RESULTS_DIR   = PROJECT_ROOT / "archive" / "iter_177" / "results"
GIF_OUT       = RESULTS_DIR / "failure_visualization.gif"

GRID_SIZE = 128
STEPS     = 500
CELL_PX   = 5          # pixels per grid cell
WIN_CELLS = 60         # window side in grid cells (square crop around CoM)
FRAME_SKIP = 1         # capture every Nth step (1 = all 501 frames)
GIF_DURATION_MS = 60   # ms per frame for early part
GIF_DURATION_FAST_MS = 40  # ms per frame after bloom

# colours
BG_COLOUR  = (240, 240, 240)   # light grey background
ON_COLOUR  = (10,  10,  80)    # dark blue-black for live cells
OFF_COLOUR = BG_COLOUR
SEED_MARK  = (200, 40,  40)    # red dot for original seed cells
TEXT_BG    = (20,  20,  20, 200)
TEXT_FG    = (255, 230, 80)


def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


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


def center_of_mass(grid: np.ndarray) -> tuple[float, float]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return float(GRID_SIZE // 2), float(GRID_SIZE // 2)
    return float(np.mean(rows)), float(np.mean(cols))  # (com_row, com_col)


def extract_window(grid: np.ndarray, cr: float, cc: float) -> np.ndarray:
    """Extract WIN_CELLS x WIN_CELLS window centred on (cr, cc) with toroidal wrap."""
    half = WIN_CELLS // 2
    r0 = int(round(cr)) - half
    c0 = int(round(cc)) - half
    rows = np.arange(r0, r0 + WIN_CELLS) % GRID_SIZE
    cols = np.arange(c0, c0 + WIN_CELLS) % GRID_SIZE
    return grid[np.ix_(rows, cols)].copy(), r0, c0


def render_frame(window: np.ndarray, step: int, bit_count: int,
                 seed_cells_in_window: list, r0: int, c0: int) -> Image.Image:
    """Render one grid window to a Pillow Image with annotation."""
    h, w = window.shape
    img_w = w * CELL_PX
    img_h = h * CELL_PX + 22   # extra row for text header

    img = Image.new("RGB", (img_w, img_h), BG_COLOUR)
    pix = img.load()

    # Draw cells
    for row in range(h):
        for col in range(w):
            colour = ON_COLOUR if window[row, col] else OFF_COLOUR
            for dy in range(CELL_PX):
                for dx in range(CELL_PX):
                    pix[col * CELL_PX + dx, row * CELL_PX + dy + 22] = colour

    # Mark initial seed cells (first few steps only — show where they started)
    for (sr, sc) in seed_cells_in_window:
        pr = (sr - r0) % GRID_SIZE
        pc = (sc - c0) % GRID_SIZE
        if 0 <= pr < h and 0 <= pc < w:
            x0p = pc * CELL_PX
            y0p = pr * CELL_PX + 22
            for dy in range(CELL_PX):
                for dx in range(CELL_PX):
                    pix[x0p + dx, y0p + dy] = SEED_MARK

    # Header bar
    draw = ImageDraw.Draw(img)
    draw.rectangle([(0, 0), (img_w, 21)], fill=(30, 30, 30))

    phase_label = ""
    if step <= 5:
        phase_label = " [SEED]"
    elif bit_count > 30:
        phase_label = " [BLOOM]"

    draw.text((4, 3),
              f"t={step:4d}  bits={bit_count:4d}{phase_label}",
              fill=TEXT_FG)

    return img


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading rule...", flush=True)
    with open(RULE_PATH) as f:
        data = json.load(f)
    lut = rule_dict_to_lut(data["rule"])
    print(f"  Rule: {data['rule_id']}  fitness={data['fitness']}", flush=True)

    print("Loading seed...", flush=True)
    with open(PARTICLE_PATH) as f:
        pdata = json.load(f)
    seed_cells = [tuple(c) for c in pdata["cells"]]  # list of (row, col)
    print(f"  Seed: {len(seed_cells)} cells at {seed_cells}", flush=True)

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in seed_cells:
        grid[r, c] = 1

    # Initial CoM anchors the window for the first few steps
    initial_cr, initial_cc = center_of_mass(grid)
    anchor_cr, anchor_cc = initial_cr, initial_cc

    frames = []
    bit_counts = []

    for step in range(STEPS + 1):
        bc = int(grid.sum())
        bit_counts.append(bc)

        # Move anchor to track CoM after bloom has settled
        if step > 10:
            cr, cc = center_of_mass(grid)
            # Smooth tracking: blend anchor toward current CoM
            alpha = 0.12
            anchor_cr = anchor_cr * (1 - alpha) + cr * alpha
            anchor_cc = anchor_cc * (1 - alpha) + cc * alpha

        window, r0, c0 = extract_window(grid, anchor_cr, anchor_cc)

        frame = render_frame(window, step, bc,
                             seed_cells if step <= 20 else [],
                             r0, c0)
        frames.append(frame)

        if step % 50 == 0:
            print(f"  t={step:4d}: bit_count={bc}", flush=True)

        if step < STEPS:
            grid = step_grid(grid, lut)

    print(f"\nRendered {len(frames)} frames.", flush=True)
    print(f"Bit count range: {min(bit_counts)} – {max(bit_counts)}", flush=True)

    # Build per-frame durations: slow at start, faster during oscillation
    bloom_step = next((i for i, b in enumerate(bit_counts) if b > 20), STEPS)
    durations = []
    for i in range(len(frames)):
        if i < bloom_step + 20:
            durations.append(GIF_DURATION_MS)
        else:
            durations.append(GIF_DURATION_FAST_MS)

    print(f"Bloom detected at step ~{bloom_step}", flush=True)
    print(f"Saving GIF to {GIF_OUT} ...", flush=True)

    frames[0].save(
        str(GIF_OUT),
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=False,
    )
    size_mb = GIF_OUT.stat().st_size / 1e6
    print(f"Saved: {GIF_OUT}  ({size_mb:.2f} MB)", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
