#!/usr/bin/env python3
"""
validate_metric.py

Validates the velocity-stability fitness metric (iter_149) against rule_016,
which is known to exhibit decaying motion (confirmed in iter_143).

Expected result: fitness < 0.1  (high std_dev of per-window velocities).
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR      = Path(__file__).parent

# Primary paths from task specification
RULE_PATH_PRIMARY   = PROJECT_ROOT / "archive" / "iter_135" / "results" / "rules" / "rule_016.txt"
STATE_PATH_PRIMARY  = PROJECT_ROOT / "archive" / "iter_132" / "results" / "remnant.npy"

# Fallback paths from existing codebase evidence
RULE_PATH_FALLBACK  = PROJECT_ROOT / "archive" / "iter_142" / "results" / "population" / "rule_016.json"
ASH_PATTERN_PATH    = SRC_DIR / "ash_pattern.json"

OUTPUT_DIR  = PROJECT_ROOT / "archive" / "iter_149" / "results"
OUTPUT_JSON = OUTPUT_DIR / "validation_results.json"

GRID_SIZE        = 400   # match iter_143 setup for meaningful displacements
STEPS_PER_WINDOW = 400
NUM_WINDOWS      = 4


# ── Simulation primitives (self-contained, no external import) ─────────────────

def _rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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


def _center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


# ── Fitness function ──────────────────────────────────────────────────────────

def calculate_velocity_stability(
    rule_dict: dict,
    initial_state: np.ndarray,
    steps_per_window: int = STEPS_PER_WINDOW,
    num_windows: int = NUM_WINDOWS,
) -> tuple:
    """Returns (fitness, velocities, std_dev). fitness = 1 / (1 + std_dev)."""
    lut  = _rule_to_lut(rule_dict)
    grid = np.copy(initial_state)

    com_checkpoints = [_center_of_mass(grid)]
    print(f"  Window 0: COM=({com_checkpoints[0][0]:.4f}, {com_checkpoints[0][1]:.4f})  "
          f"bits={int(grid.sum())}", flush=True)

    for w in range(num_windows):
        for _ in range(steps_per_window):
            grid = _step_grid(grid, lut)
        com = _center_of_mass(grid)
        com_checkpoints.append(com)
        bits = int(grid.sum())
        print(f"  Window {w+1}: COM=({com[0]:.4f}, {com[1]:.4f})  bits={bits}", flush=True)

    velocities = []
    for i in range(num_windows):
        sq, sr = com_checkpoints[i]
        eq, er = com_checkpoints[i + 1]
        disp = math.sqrt((eq - sq) ** 2 + (er - sr) ** 2)
        velocities.append(disp)
        print(f"  v[{i}] = {disp:.4f} cells/window", flush=True)

    std_dev = float(np.std(velocities))
    fitness  = 1.0 / (1.0 + std_dev)
    return fitness, velocities, std_dev


# ── Loaders ───────────────────────────────────────────────────────────────────

def load_rule(path: Path) -> tuple:
    """Load rule from .json or .txt (tries JSON first). Returns (rule_dict, path_used)."""
    if path.exists():
        print(f"Loading rule from {path}", flush=True)
        with open(path) as f:
            raw = f.read().strip()
        try:
            data = json.loads(raw)
            return {int(k): int(v) for k, v in data.items()}, path
        except (json.JSONDecodeError, ValueError) as err:
            print(f"  WARNING: could not parse {path} as JSON ({err})", flush=True)

    # Fallback to iter_142 JSON
    if RULE_PATH_FALLBACK.exists():
        print(f"Falling back to {RULE_PATH_FALLBACK}", flush=True)
        with open(RULE_PATH_FALLBACK) as f:
            data = json.load(f)
        return {int(k): int(v) for k, v in data.items()}, RULE_PATH_FALLBACK

    raise FileNotFoundError(
        f"rule_016 not found at {path} or {RULE_PATH_FALLBACK}"
    )


def load_initial_state(path: Path) -> tuple:
    """Load grid from .npy or reconstruct from ash_pattern centred on GRID_SIZE grid.
    Returns (grid, label)."""
    if path.exists():
        print(f"Loading initial state from {path}", flush=True)
        grid = np.load(path)
        # Pad/resize to GRID_SIZE if needed
        if grid.shape != (GRID_SIZE, GRID_SIZE):
            padded = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
            h, w = grid.shape
            q0 = GRID_SIZE // 2 - h // 2
            r0 = GRID_SIZE // 2 - w // 2
            padded[q0:q0+h, r0:r0+w] = grid[:min(h,GRID_SIZE), :min(w,GRID_SIZE)]
            grid = padded
        return grid.astype(np.uint8), str(path.relative_to(PROJECT_ROOT))

    print(f"  {path} not found — centering ash_pattern.json on {GRID_SIZE}x{GRID_SIZE} grid "
          f"(matches iter_143 setup)", flush=True)
    if not ASH_PATTERN_PATH.exists():
        raise FileNotFoundError(f"ash_pattern.json not found at {ASH_PATTERN_PATH}")

    with open(ASH_PATTERN_PATH) as f:
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

    print(f"  ash_pattern: {placed} bits centred on {GRID_SIZE}x{GRID_SIZE} grid "
          f"(offset q={q_offset}, r={r_offset})", flush=True)
    return grid, f"ash_pattern_centred_{GRID_SIZE}x{GRID_SIZE}"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load rule
    rule_dict, rule_path_used = load_rule(RULE_PATH_PRIMARY)
    print(f"  Rule has {len(rule_dict)} non-identity mappings", flush=True)

    # Load initial state
    initial_state, state_label = load_initial_state(STATE_PATH_PRIMARY)
    print(f"  Initial state: {int(initial_state.sum())} live cells  "
          f"shape={initial_state.shape}", flush=True)

    # Run experiment
    print(f"\nCalculating velocity stability "
          f"({NUM_WINDOWS} windows x {STEPS_PER_WINDOW} steps) ...", flush=True)
    fitness, velocities, std_dev = calculate_velocity_stability(
        rule_dict, initial_state,
        steps_per_window=STEPS_PER_WINDOW,
        num_windows=NUM_WINDOWS,
    )

    # Report
    print(f"\n=== Results ===", flush=True)
    print(f"  velocities:  {[round(v, 8) for v in velocities]}", flush=True)
    print(f"  std_dev:     {std_dev:.8f}", flush=True)
    print(f"  fitness:     {fitness:.8f}", flush=True)
    print(f"  fitness < 0.1: {fitness < 0.1}", flush=True)

    metric_works = bool(fitness < 0.1)
    print(f"\nMetric correctly identifies decaying motion: {metric_works}", flush=True)

    results = {
        "rule_id":        "rule_016",
        "rule_source":    str(rule_path_used.relative_to(PROJECT_ROOT)),
        "initial_state":  state_label,
        "num_windows":    NUM_WINDOWS,
        "steps_per_window": STEPS_PER_WINDOW,
        "velocities":     [round(v, 8) for v in velocities],
        "std_dev":        round(std_dev, 8),
        "fitness":        round(fitness, 8),
        "metric_correctly_identifies_decay": metric_works,
    }

    with open(OUTPUT_JSON, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {OUTPUT_JSON}", flush=True)

    return 0 if metric_works else 1


if __name__ == "__main__":
    sys.exit(main())
