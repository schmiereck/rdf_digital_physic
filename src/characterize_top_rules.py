#!/usr/bin/env python3
"""
characterize_top_rules.py

Load the top 5 rules from the iter_193 final population, simulate each for 500
steps on the standard two-glider collision seed, save a GIF per rule, classify
the collision outcome, and write a summary.json report.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass as scipy_com

# ── paths ────────────────────────────────────────────────────────────────────

REPO_ROOT   = Path(__file__).parent.parent
POP_PATH    = REPO_ROOT / "archive/iter_193/iter_002/results/final_population.json"
OUTPUT_DIR  = REPO_ROOT / "archive/iter_195/results"

# ── seed constants (identical to fitness.py _STAGED_* values) ───────────────

GRID_SIZE    = 128
OBJECT_A     = [(60, 40), (61, 40), (60, 41)]
OBJECT_B     = [(67, 87), (68, 87), (67, 88)]
LABEL_STRUCT = np.ones((3, 3), dtype=np.uint8)
SIM_STEPS    = 500
TOP_N        = 5


# ── helpers ──────────────────────────────────────────────────────────────────

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


def two_coms_distance(grid: np.ndarray) -> float | None:
    """Euclidean distance between the two largest-component COMs, or None."""
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


def classify_outcome(
    initial_bits: int,
    final_bits: int,
    initial_distance: float,
    final_distance: float | None,
    min_distance: float,
) -> str:
    """Classify the 500-step collision result."""
    bits_ok = final_bits == initial_bits
    if not bits_ok:
        return "BIT_LOSS"
    if final_distance is None:
        return "FUSION"
    approach_ok = min_distance < initial_distance - 1.0
    recede_ok   = final_distance >= initial_distance
    if approach_ok and recede_ok:
        return "ELASTIC"
    if approach_ok:
        return "PARTIAL"  # approached but did not fully recede
    return "NO_APPROACH"


# ── GIF writer ───────────────────────────────────────────────────────────────

def save_gif(frames: list, gif_path: Path) -> int:
    """Save list of uint8 numpy grids as a GIF. Returns file size in bytes."""
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


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading population from: {POP_PATH}")
    with open(POP_PATH) as f:
        population = json.load(f)

    # Sort by fitness (descending); break ties by original index (ascending).
    population_sorted = sorted(population, key=lambda x: (-x["fitness"], x["index"]))
    top5 = population_sorted[:TOP_N]
    print(f"  Total entries: {len(population)}")
    print(f"  Top {TOP_N} fitness scores: {[e['fitness'] for e in top5]}\n")

    initial_grid    = make_seed_grid()
    initial_bits    = int(initial_grid.sum())
    initial_distance = two_coms_distance(initial_grid)
    print(f"Seed: {initial_bits} bits, initial inter-glider distance = {initial_distance:.4f}\n")

    summary = []

    for rank, entry in enumerate(top5, start=1):
        pop_index    = entry["index"]
        pop_fitness  = entry["fitness"]
        rule_dict    = entry["rule_dict"]
        stored_metrics = entry.get("metrics", {})

        print(f"--- Rule {rank} (pop index {pop_index}, fitness={pop_fitness}) ---")

        lut    = rule_dict_to_lut(rule_dict)
        grid   = make_seed_grid()
        frames = [grid.copy()]
        min_distance = initial_distance

        for step in range(1, SIM_STEPS + 1):
            grid = step_grid(grid, lut)
            frames.append(grid.copy())
            d = two_coms_distance(grid)
            if d is not None and d < min_distance:
                min_distance = d

        final_bits     = int(grid.sum())
        final_distance = two_coms_distance(grid)
        outcome        = classify_outcome(
            initial_bits, final_bits, initial_distance, final_distance, min_distance
        )

        print(f"  initial_bits     = {initial_bits}")
        print(f"  final_bits       = {final_bits}")
        print(f"  initial_distance = {initial_distance:.4f}")
        print(f"  min_distance     = {min_distance:.4f}")
        print(f"  final_distance   = {final_distance:.4f}" if final_distance is not None else "  final_distance   = None (merged)")
        print(f"  outcome          = {outcome}")

        gif_name = f"top_{rank}_collision.gif"
        gif_path = OUTPUT_DIR / gif_name
        size_b   = save_gif(frames, gif_path)
        print(f"  GIF saved: {gif_path}  ({size_b / 1024:.1f} KB)\n")

        summary.append({
            "rank":              rank,
            "population_index":  pop_index,
            "population_fitness": pop_fitness,
            "stored_metrics":    stored_metrics,
            "sim_steps":         SIM_STEPS,
            "initial_bits":      initial_bits,
            "final_bits":        final_bits,
            "initial_distance":  round(initial_distance, 6),
            "min_distance":      round(min_distance, 6),
            "final_distance":    round(final_distance, 6) if final_distance is not None else None,
            "outcome":           outcome,
            "gif_file":          gif_name,
        })

    summary_path = OUTPUT_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Summary written: {summary_path}")

    # Print compact table
    print("\n=== SUMMARY TABLE ===")
    print(f"{'Rank':>4}  {'Pop#':>4}  {'Fit':>5}  {'FinalBits':>9}  {'FinalDist':>9}  Outcome")
    print("-" * 60)
    for r in summary:
        fd = f"{r['final_distance']:.4f}" if r["final_distance"] is not None else "  None"
        print(f"{r['rank']:>4}  {r['population_index']:>4}  {r['population_fitness']:>5}  "
              f"{r['final_bits']:>9}  {fd:>9}  {r['outcome']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
