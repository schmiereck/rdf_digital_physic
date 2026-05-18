#!/usr/bin/env python3
"""
verify_iter213_collision.py

Stability verification for iter_213: run the champion rule (pop index 0)
from iter_193 on the standard two-glider collision seed and save a GIF to
archive/iter_213/results/verification_collision.gif.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass as scipy_com

REPO_ROOT  = Path(__file__).parent.parent
POP_PATH   = REPO_ROOT / "archive/iter_193/iter_002/results/final_population.json"
OUTPUT_DIR = REPO_ROOT / "archive/iter_213/results"
GIF_NAME   = "verification_collision.gif"

GRID_SIZE    = 128
OBJECT_A     = [(60, 40), (61, 40), (60, 41)]
OBJECT_B     = [(67, 87), (68, 87), (67, 88)]
LABEL_STRUCT = np.ones((3, 3), dtype=np.uint8)
SIM_STEPS    = 500


def make_seed_grid() -> np.ndarray:
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in OBJECT_A:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    for r, c in OBJECT_B:
        grid[r % GRID_SIZE, c % GRID_SIZE] = 1
    return grid


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


def two_coms_distance(grid: np.ndarray):
    labels, n = label(grid, structure=LABEL_STRUCT)
    if n < 2:
        return None
    sizes = sorted(
        ((lbl, int(np.sum(labels == lbl))) for lbl in range(1, n + 1)),
        key=lambda x: x[1],
        reverse=True,
    )
    top2 = [sizes[0][0], sizes[1][0]]
    coms = scipy_com(grid, labels, top2)
    (r1, c1), (r2, c2) = coms
    return math.sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)


def save_gif(frames: list, gif_path: Path) -> int:
    try:
        from PIL import Image

        pil_frames = []
        for i, f in enumerate(frames):
            if i > 200 and i % 2 != 0:
                continue
            img = Image.fromarray((f * 255).astype(np.uint8), mode="L")
            img = img.resize((256, 256), Image.NEAREST).convert("P")
            pil_frames.append(img)

        pil_frames[0].save(
            gif_path,
            save_all=True,
            append_images=pil_frames[1:],
            duration=40,
            loop=0,
        )
        return gif_path.stat().st_size

    except ImportError:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.animation as animation

        sample = [f for i, f in enumerate(frames) if i <= 200 or i % 2 == 0]
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.axis("off")
        im = ax.imshow(sample[0], cmap="binary", vmin=0, vmax=1, interpolation="nearest")

        def update(i):
            im.set_data(sample[i])
            return [im]

        ani = animation.FuncAnimation(fig, update, frames=len(sample), interval=40, blit=True)
        ani.save(str(gif_path), writer="pillow", fps=25)
        plt.close(fig)
        return gif_path.stat().st_size


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading population: {POP_PATH}")
    with open(POP_PATH) as f:
        population = json.load(f)

    # Champion = top by fitness, then lowest original index
    population_sorted = sorted(population, key=lambda x: (-x["fitness"], x["index"]))
    champion = population_sorted[0]
    pop_index = champion["index"]
    fitness   = champion["fitness"]
    rule_dict = champion["rule_dict"]

    print(f"Champion: pop_index={pop_index}, fitness={fitness}")

    lut           = rule_dict_to_lut(rule_dict)
    initial_grid  = make_seed_grid()
    initial_bits  = int(initial_grid.sum())
    initial_dist  = two_coms_distance(initial_grid)

    print(f"Seed: {initial_bits} bits, initial distance = {initial_dist:.4f}")

    grid         = initial_grid.copy()
    frames       = [grid.copy()]
    min_distance = initial_dist

    for step in range(1, SIM_STEPS + 1):
        grid = step_grid(grid, lut)
        frames.append(grid.copy())
        d = two_coms_distance(grid)
        if d is not None and d < min_distance:
            min_distance = d

    final_bits = int(grid.sum())
    final_dist = two_coms_distance(grid)

    bits_ok   = final_bits == initial_bits
    approach_ok = min_distance < initial_dist - 1.0
    recede_ok = final_dist is not None and final_dist >= initial_dist

    if bits_ok and approach_ok and recede_ok:
        outcome = "ELASTIC"
    elif not bits_ok:
        outcome = "BIT_LOSS"
    elif final_dist is None:
        outcome = "FUSION"
    elif approach_ok:
        outcome = "PARTIAL"
    else:
        outcome = "NO_APPROACH"

    print(f"initial_bits     = {initial_bits}")
    print(f"final_bits       = {final_bits}")
    print(f"initial_distance = {initial_dist:.4f}")
    print(f"min_distance     = {min_distance:.4f}")
    print(f"final_distance   = {final_dist:.4f}" if final_dist is not None else "final_distance   = None (merged)")
    print(f"outcome          = {outcome}")

    gif_path = OUTPUT_DIR / GIF_NAME
    size_b   = save_gif(frames, gif_path)
    print(f"GIF saved: {gif_path}  ({size_b / 1024:.1f} KB)")

    if outcome != "ELASTIC":
        print("VERIFICATION FAILED: outcome is not ELASTIC", file=sys.stderr)
        return 1

    print("VERIFICATION PASSED: elastic collision confirmed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
