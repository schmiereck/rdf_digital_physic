#!/usr/bin/env python3
"""
run_iter_194_robustness.py

Check robustness of elastic collision discovery from iter_193.
Loads ranks 2-5 from the final population, runs 400-step collision simulations,
generates GIF animations, and writes a summary JSON.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import label, center_of_mass

REPO_ROOT = Path(__file__).parent.parent
POPULATION_PATH = REPO_ROOT / "archive/iter_193/iter_002/results/final_population.json"
OUTPUT_DIR = REPO_ROOT / "archive/iter_194/results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GRID_SIZE = 128
OBJECT_A = [(60, 40), (61, 40), (60, 41)]
OBJECT_B = [(67, 87), (68, 87), (67, 88)]
LABEL_STRUCT = np.ones((3, 3), dtype=np.uint8)
MARGIN = 1.0
SIM_STEPS = 400


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


def classify_outcome(
    bit_error: int,
    approach_ok: bool,
    recession_score: float,
    final_bits: int,
    initial_bits: int,
) -> str:
    if not approach_ok:
        return "chaotic"
    if bit_error == 0 and recession_score >= 0.9:
        return "elastic"
    if final_bits < initial_bits - 1:
        return "inelastic_annihilation"
    if bit_error == 0 and recession_score < 0.5:
        return "inelastic_fusion"
    return "chaotic"


def save_gif(frames, gif_path: Path):
    try:
        from PIL import Image

        gif_frames = []
        for i, frame in enumerate(frames):
            if i > 200 and i % 2 != 0:
                continue
            img_data = (frame * 255).astype(np.uint8)
            img = Image.fromarray(img_data, mode="L").resize((256, 256), Image.NEAREST)
            gif_frames.append(img.convert("P"))

        gif_frames[0].save(
            gif_path,
            save_all=True,
            append_images=gif_frames[1:],
            duration=40,
            loop=0,
        )
        print(f"  GIF saved: {gif_path} ({gif_path.stat().st_size / 1024:.1f} KB, {len(gif_frames)} frames)")
        return True
    except Exception as e:
        print(f"  PIL failed: {e}, trying imageio …")

    try:
        import imageio

        gif_frames = []
        for i, frame in enumerate(frames):
            if i > 200 and i % 2 != 0:
                continue
            img_data = (frame * 255).astype(np.uint8)
            img_up = np.repeat(np.repeat(img_data, 2, axis=0), 2, axis=1)
            gif_frames.append(img_up)

        imageio.mimsave(str(gif_path), gif_frames, fps=25, loop=0)
        print(f"  GIF saved: {gif_path} ({gif_path.stat().st_size / 1024:.1f} KB, {len(gif_frames)} frames)")
        return True
    except Exception as e:
        print(f"  imageio failed: {e}")
        return False


# ── main ──────────────────────────────────────────────────────────────────────

print(f"Loading population from: {POPULATION_PATH}")
with open(POPULATION_PATH) as f:
    population = json.load(f)

print(f"Population size: {len(population)}")
print(f"Ranks 2-5 are indices 1-4 (0-indexed)")
print()

results = []

for rank in range(2, 6):
    idx = rank - 1  # population is 0-indexed, rank 1 = index 0
    entry = population[idx]
    rule_dict = entry["rule_dict"]
    stored_fitness = entry["fitness"]
    stored_metrics = entry["metrics"]

    print(f"=" * 60)
    print(f"Rank {rank} (index {idx}): stored fitness = {stored_fitness}")

    lut = rule_dict_to_lut(rule_dict)
    grid = make_seed_grid()
    initial_bits = int(grid.sum())
    initial_distance = two_coms_distance(grid)
    min_distance = initial_distance

    print(f"  Initial bits: {initial_bits}, initial distance: {initial_distance:.4f}")
    print(f"  Running {SIM_STEPS} steps …")

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
            print(f"    step {step:4d}: bits={bits}, dist={dist:.4f}")

    final_bits = int(grid.sum())
    bit_error = abs(final_bits - initial_bits)
    final_distance = two_coms_distance(grid)
    final_distance_val = final_distance if final_distance is not None else 0.0
    recession_score = min(1.0, final_distance_val / initial_distance) if initial_distance > 0 else 0.0
    approach_ok = min_distance < initial_distance - MARGIN

    outcome = classify_outcome(bit_error, approach_ok, recession_score, final_bits, initial_bits)

    print(f"  final_bits={final_bits}, bit_error={bit_error}")
    print(f"  min_distance={min_distance:.4f}, final_distance={final_distance_val:.4f}")
    print(f"  approach_ok={approach_ok}, recession_score={recession_score:.4f}")
    print(f"  --> OUTCOME: {outcome}")

    gif_path = OUTPUT_DIR / f"rank_{rank}_collision.gif"
    save_gif(frames, gif_path)

    results.append({
        "rank": rank,
        "population_index": idx,
        "stored_fitness": stored_fitness,
        "outcome": outcome,
        "metrics": {
            "initial_bits": initial_bits,
            "final_bits": final_bits,
            "bit_error": bit_error,
            "initial_distance": initial_distance,
            "min_distance": min_distance,
            "final_distance": final_distance_val,
            "approach_ok": approach_ok,
            "recession_score": recession_score,
        },
        "stored_metrics": stored_metrics,
    })
    print()

summary_path = OUTPUT_DIR / "robustness_check.json"
with open(summary_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"Summary written to: {summary_path}")

print()
print("=" * 60)
print("ROBUSTNESS CHECK SUMMARY")
print("=" * 60)
for r in results:
    print(f"  Rank {r['rank']}: {r['outcome']}")
print("=" * 60)
