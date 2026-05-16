#!/usr/bin/env python3
"""
verify_iter193_champion.py

Load the champion rule from iter_193.2, run a 500-step simulation on the
standard 128x128 two-glider collision seed, generate a GIF, and report metrics.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass

# ── paths ───────────────────────────────────────────────────────────────────

REPO_ROOT   = Path(__file__).parent.parent
RULE_PATH   = REPO_ROOT / "archive/iter_193/iter_002/results/champion_rule.json"
OUTPUT_DIR  = REPO_ROOT / "archive/iter_193/iter_003/results"
GIF_PATH    = OUTPUT_DIR / "elastic_collision.gif"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).parent))

# ── constants (same as fitness.py) ──────────────────────────────────────────

GRID_SIZE   = 128
OBJECT_A    = [(60, 40), (61, 40), (60, 41)]
OBJECT_B    = [(67, 87), (68, 87), (67, 88)]
LABEL_STRUCT = np.ones((3, 3), dtype=np.uint8)
MARGIN      = 1.0
SIM_STEPS   = 500


# ── rule / grid helpers ─────────────────────────────────────────────────────

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
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)
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


def make_seed_grid() -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in OBJECT_A:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    for r, c in OBJECT_B:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    return grid


def two_coms_distance(grid: np.ndarray):
    """Return Euclidean distance between the two largest-component COMs, or None."""
    labels, n = label(grid, structure=LABEL_STRUCT)
    if n < 2:
        return None
    sizes = sorted(
        ((lbl, int(np.sum(labels == lbl))) for lbl in range(1, n + 1)),
        key=lambda x: x[1],
        reverse=True,
    )
    top2 = [sizes[0][0], sizes[1][0]]
    coms = center_of_mass(grid, labels, top2)
    (r1, c1), (r2, c2) = coms
    return math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)


# ── load champion ────────────────────────────────────────────────────────────

print(f"Loading champion rule from: {RULE_PATH}")
with open(RULE_PATH) as f:
    champion = json.load(f)

rule_dict = champion["rule_dict"]
stored_fitness = champion["metrics"]["fitness"]
print(f"  Stored fitness: {stored_fitness}")

lut = rule_dict_to_lut(rule_dict)

# ── simulate and collect frames ──────────────────────────────────────────────

grid = make_seed_grid()
initial_bits     = int(grid.sum())
initial_distance = two_coms_distance(grid)
min_distance     = initial_distance

print(f"\nSimulating {SIM_STEPS} steps on {GRID_SIZE}x{GRID_SIZE} grid …")
print(f"  Initial bits:     {initial_bits}")
print(f"  Initial distance: {initial_distance:.4f}")

# Store every frame for the GIF (500 frames at 128x128 is manageable).
frames = [grid.copy()]

for step in range(1, SIM_STEPS + 1):
    grid = step_grid(grid, lut)
    frames.append(grid.copy())

    d = two_coms_distance(grid)
    if d is not None and d < min_distance:
        min_distance = d

    if step % 100 == 0:
        bits = int(grid.sum())
        dist = d if d is not None else float("nan")
        print(f"  step {step:4d}: bits={bits}, dist={dist:.4f}")

# ── final metrics ─────────────────────────────────────────────────────────────

final_bits     = int(grid.sum())
bit_error      = abs(final_bits - initial_bits)
final_distance = two_coms_distance(grid)
final_distance_val = final_distance if final_distance is not None else 0.0

recession_score = min(1.0, final_distance_val / initial_distance) if initial_distance > 0 else 0.0
staged_score    = 1.0 + recession_score
fitness         = staged_score / (1.0 + bit_error)

approach_ok = min_distance < initial_distance - MARGIN

print()
print("=" * 50)
print("FINAL METRICS")
print("=" * 50)
print(f"  initial_bits:         {initial_bits}")
print(f"  final_bits:           {final_bits}")
print(f"  bit_error:            {bit_error}")
print(f"  initial_distance:     {initial_distance:.6f}")
print(f"  min_distance:         {min_distance:.6f}")
print(f"  final_distance:       {final_distance_val:.6f}")
print(f"  approach_ok:          {approach_ok}")
print(f"  recession_score:      {recession_score:.6f}  (final/initial)")
print(f"  staged_score:         {staged_score:.6f}  (1 + recession_score)")
print(f"  fitness:              {fitness:.6f}")
print("=" * 50)


# ── GIF generation ────────────────────────────────────────────────────────────

print(f"\nGenerating GIF ({len(frames)} frames) -> {GIF_PATH}")

try:
    from PIL import Image

    gif_frames = []
    # Use every frame for first 200 steps (collision region), then every 2nd
    for i, frame in enumerate(frames):
        if i > 200 and i % 2 != 0:
            continue
        # Scale to 256x256 with nearest-neighbour for visibility
        img_data = (frame * 255).astype(np.uint8)
        img = Image.fromarray(img_data, mode="L").resize((256, 256), Image.NEAREST)
        # Convert to RGB palette image for better GIF quality
        gif_frames.append(img.convert("P"))

    gif_frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=gif_frames[1:],
        duration=40,   # ms per frame → ~25 fps
        loop=0,
    )
    print(f"  GIF saved: {GIF_PATH.stat().st_size / 1024:.1f} KB, {len(gif_frames)} frames")

except ImportError:
    print("  PIL not available — trying imageio …")
    try:
        import imageio

        gif_frames = []
        for i, frame in enumerate(frames):
            if i > 200 and i % 2 != 0:
                continue
            img_data = (frame * 255).astype(np.uint8)
            # Upscale via numpy repeat
            img_up = np.repeat(np.repeat(img_data, 2, axis=0), 2, axis=1)
            gif_frames.append(img_up)

        imageio.mimsave(str(GIF_PATH), gif_frames, fps=25, loop=0)
        print(f"  GIF saved: {GIF_PATH.stat().st_size / 1024:.1f} KB, {len(gif_frames)} frames")

    except Exception as e:
        print(f"  imageio also failed: {e}")
        print("  Falling back to matplotlib …")

        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        fig, ax = plt.subplots(figsize=(4, 4))
        ax.axis("off")
        im = ax.imshow(frames[0], cmap="binary", vmin=0, vmax=1, interpolation="nearest")

        sample = frames[::2]

        def update(i):
            im.set_data(sample[i])
            return [im]

        ani = animation.FuncAnimation(fig, update, frames=len(sample), interval=40, blit=True)
        ani.save(str(GIF_PATH), writer="pillow", fps=25)
        plt.close(fig)
        print(f"  GIF saved via matplotlib: {GIF_PATH.stat().st_size / 1024:.1f} KB")

print("\nDone.")
