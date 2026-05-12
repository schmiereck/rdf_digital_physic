#!/usr/bin/env python3
"""
run_iter143_long_run_verification.py

Long-run verification for rule_016 from iter_142.
Runs 2000 steps on a 400x400 grid, records COM at steps 400, 800, 1200, 1600,
and computes displacement-based velocity ratio to check motion sustainability.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_142" / "results" / "population" / "rule_016.json"
ASH_PATH     = Path(__file__).parent / "ash_pattern.json"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_143" / "results"
METRICS_JSON = RESULTS_DIR / "long_run_metrics.json"

GRID_SIZE    = 400
TOTAL_STEPS  = 2000
RECORD_STEPS = {400, 800, 1200, 1600}


def rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


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


def distance(a: tuple, b: tuple) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load rule ─────────────────────────────────────────────────────────────
    print("=== Loading inputs ===", flush=True)
    with open(RULE_PATH) as f:
        rule_dict = json.load(f)
    lut = rule_to_lut(rule_dict)
    print(f"  Rule: {len(rule_dict)} mapped states", flush=True)

    # ── Load ash pattern and center on 400x400 grid ───────────────────────────
    with open(ASH_PATH) as f:
        ash = json.load(f)

    ash_cells = ash["cells"]
    ash_qs    = [c[0] for c in ash_cells]
    ash_rs    = [c[1] for c in ash_cells]
    ash_q_center = (min(ash_qs) + max(ash_qs)) // 2
    ash_r_center = (min(ash_rs) + max(ash_rs)) // 2
    q_offset = GRID_SIZE // 2 - ash_q_center
    r_offset = GRID_SIZE // 2 - ash_r_center

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    placed = 0
    for q, r in ash_cells:
        nq, nr = q + q_offset, r + r_offset
        if 0 <= nq < GRID_SIZE and 0 <= nr < GRID_SIZE:
            grid[nq, nr] = 1
            placed += 1

    initial_bits = int(grid.sum())
    print(f"  Ash pattern: {initial_bits} bits centered on {GRID_SIZE}x{GRID_SIZE} grid "
          f"(offset q={q_offset}, r={r_offset})", flush=True)
    if placed < len(ash_cells):
        print(f"  WARNING: {len(ash_cells) - placed} cells out of bounds", flush=True)

    # ── Run simulation ────────────────────────────────────────────────────────
    print(f"\n=== Simulating {TOTAL_STEPS} steps ===", flush=True)
    com_snapshots: dict = {}

    for s in range(1, TOTAL_STEPS + 1):
        grid = step_grid(grid, lut)

        if s in RECORD_STEPS:
            com  = center_of_mass(grid)
            bits = int(grid.sum())
            com_snapshots[s] = {"com": com, "bits": bits}
            print(f"  t={s:4d}: bits={bits:6d}  COM=({com[0]:.4f}, {com[1]:.4f})", flush=True)
        elif s % 200 == 0:
            com  = center_of_mass(grid)
            bits = int(grid.sum())
            print(f"  t={s:4d}: bits={bits:6d}  COM=({com[0]:.4f}, {com[1]:.4f})", flush=True)

    final_bits = int(grid.sum())

    # ── Compute displacement metrics ──────────────────────────────────────────
    com_400  = com_snapshots[400]["com"]
    com_800  = com_snapshots[800]["com"]
    com_1200 = com_snapshots[1200]["com"]
    com_1600 = com_snapshots[1600]["com"]

    disp_400_800   = distance(com_800, com_400)
    disp_1200_1600 = distance(com_1600, com_1200)
    velocity_ratio = (disp_1200_1600 / disp_400_800
                      if disp_400_800 > 1e-10 else 0.0)
    motion_sustained = bool(velocity_ratio >= 0.9)

    # ── Print summary ─────────────────────────────────────────────────────────
    print("\n=== Displacement results ===", flush=True)
    print(f"  COM at t=400:   ({com_400[0]:.4f}, {com_400[1]:.4f})", flush=True)
    print(f"  COM at t=800:   ({com_800[0]:.4f}, {com_800[1]:.4f})", flush=True)
    print(f"  COM at t=1200:  ({com_1200[0]:.4f}, {com_1200[1]:.4f})", flush=True)
    print(f"  COM at t=1600:  ({com_1600[0]:.4f}, {com_1600[1]:.4f})", flush=True)
    print(f"  disp_400_800:   {disp_400_800:.6f}", flush=True)
    print(f"  disp_1200_1600: {disp_1200_1600:.6f}", flush=True)
    print(f"  velocity_ratio: {velocity_ratio:.6f}", flush=True)
    print(f"  motion_sustained (ratio >= 0.9): {motion_sustained}", flush=True)
    print(f"  final_bit_count at t=2000: {final_bits}", flush=True)

    # ── Save metrics JSON ─────────────────────────────────────────────────────
    metrics = {
        "rule": "rule_016",
        "source": "archive/iter_142/results/population/rule_016.json",
        "grid_size": GRID_SIZE,
        "total_steps": TOTAL_STEPS,
        "initial_bit_count": initial_bits,
        "com_at_400":  list(com_400),
        "com_at_800":  list(com_800),
        "com_at_1200": list(com_1200),
        "com_at_1600": list(com_1600),
        "disp_400_800":        round(disp_400_800, 8),
        "disp_1200_1600":      round(disp_1200_1600, 8),
        "velocity_ratio":      round(velocity_ratio, 8),
        "final_bit_count_at_2000": final_bits,
        "motion_sustained":    motion_sustained,
    }
    with open(METRICS_JSON, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nSaved: {METRICS_JSON}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
