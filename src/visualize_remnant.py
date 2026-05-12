#!/usr/bin/env python3
"""
visualize_remnant.py

Analyzes the spatial distribution of objects in the stable remnant produced
by rule_011 (iter_131). Simulates 200 steps, extracts connected components,
characterizes each object in isolation (type, period), computes center-of-mass,
and writes archive/iter_134/results/remnant_map.txt.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = Path(__file__).parent
RULE_PATH = PROJECT_ROOT / "archive" / "iter_131" / "population" / "rule_011.json"
ASH_PATTERN_PATH = SRC_DIR / "ash_pattern.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_134" / "results"
OUTPUT_PATH = RESULTS_DIR / "remnant_map.txt"

GRID_SIZE = 200
RUN_STEPS = 200
MAX_PERIOD_STEPS = 100
ISO_PADDING = 50

HEX_DIRS = [
    ( 1,  0),
    ( 1, -1),
    ( 0, -1),
    (-1,  0),
    (-1,  1),
    ( 0,  1),
]


def rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lookup: np.ndarray) -> np.ndarray:
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
    return lookup[state]


def get_connected_components(grid: np.ndarray, grid_size: int) -> list:
    live = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    components = []
    for start in live:
        if start in visited:
            continue
        component = []
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            component.append(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % grid_size, (r + dr) % grid_size)
                if nb in live and nb not in visited:
                    stack.append(nb)
        components.append(component)
    return components


def normalize_shape(cells) -> frozenset:
    if not cells:
        return frozenset()
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    min_q, min_r = min(qs), min(rs)
    return frozenset((q - min_q, r - min_r) for q, r in cells)


def characterize_object(cells: list, lut: np.ndarray,
                        max_steps: int = 100, padding: int = 50) -> tuple:
    """Simulate object in isolation to find its period.

    Returns (type_str, period) where type_str is 'still-life', 'oscillator',
    'decayed', or 'unknown'.
    """
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    min_q, max_q = min(qs), max(qs)
    min_r, max_r = min(rs), max(rs)
    h = max_q - min_q + 1 + 2 * padding
    w = max_r - min_r + 1 + 2 * padding

    iso = np.zeros((h, w), dtype=np.uint8)
    for q, r in cells:
        iso[q - min_q + padding, r - min_r + padding] = 1

    shape_to_step: dict = {}

    for step in range(max_steps + 1):
        live = list(map(tuple, np.argwhere(iso == 1)))
        if not live:
            return 'decayed', 0
        norm = normalize_shape(live)
        if norm in shape_to_step:
            prev = shape_to_step[norm]
            period = step - prev
            status = 'still-life' if period == 1 else 'oscillator'
            return status, period
        shape_to_step[norm] = step
        iso = step_grid(iso, lut)

    return 'unknown', 0


def center_of_mass(cells: list) -> tuple:
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    return sum(qs) / len(qs), sum(rs) / len(rs)


def mean_pairwise_dist(obj_list: list) -> float:
    if len(obj_list) < 2:
        return float('nan')
    dists = []
    for i in range(len(obj_list)):
        for j in range(i + 1, len(obj_list)):
            dq = obj_list[i]['com_q'] - obj_list[j]['com_q']
            dr = obj_list[i]['com_r'] - obj_list[j]['com_r']
            dists.append(math.sqrt(dq**2 + dr**2))
    return sum(dists) / len(dists)


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading rule: {RULE_PATH}", flush=True)
    with open(RULE_PATH) as f:
        rule_dict = json.load(f)
    lut = rule_to_lut(rule_dict)
    print(f"  {len(rule_dict)} entries loaded", flush=True)

    print(f"Loading ash pattern: {ASH_PATTERN_PATH}", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        if q < GRID_SIZE and r < GRID_SIZE:
            grid[q, r] = 1
    print(f"  {int(grid.sum())} bits on {GRID_SIZE}x{GRID_SIZE} grid", flush=True)

    print(f"\nRunning {RUN_STEPS} simulation steps...", flush=True)
    for s in range(RUN_STEPS):
        grid = step_grid(grid, lut)
        if (s + 1) % 50 == 0:
            print(f"  step {s+1:3d}: {int(grid.sum())} bits", flush=True)
    remnant_bits = int(grid.sum())
    print(f"  Remnant: {remnant_bits} live cells", flush=True)

    print(f"\nFinding connected components...", flush=True)
    components = get_connected_components(grid, GRID_SIZE)
    total = len(components)
    print(f"  Found {total} objects", flush=True)

    print(f"\nCharacterizing objects in isolation...", flush=True)
    rows = []
    for i, comp in enumerate(components):
        obj_type, period = characterize_object(
            comp, lut, max_steps=MAX_PERIOD_STEPS, padding=ISO_PADDING
        )
        bit_count = len(comp)
        com_q, com_r = center_of_mass(comp)
        rows.append({
            'object_id': i + 1,
            'type': obj_type,
            'period': period,
            'bit_count': bit_count,
            'com_q': com_q,
            'com_r': com_r,
        })
        print(f"  [{i+1:3d}/{total}] {obj_type:<12s} period={period:3d}  "
              f"bits={bit_count:3d}  COM=({com_q:6.1f}, {com_r:6.1f})", flush=True)

    print(f"\nWriting {OUTPUT_PATH}...", flush=True)
    with open(OUTPUT_PATH, 'w') as f:
        f.write("object_id, type, period, bit_count, com_q, com_r\n")
        for row in rows:
            f.write(
                f"{row['object_id']}, {row['type']}, {row['period']}, "
                f"{row['bit_count']}, {row['com_q']:.2f}, {row['com_r']:.2f}\n"
            )
    print(f"  Written {total} object records", flush=True)

    # --- Spatial analysis ---
    osc_rows = [r for r in rows if r['type'] == 'oscillator']
    sl_rows  = [r for r in rows if r['type'] == 'still-life']

    avg_osc_dist = mean_pairwise_dist(osc_rows)
    avg_all_dist = mean_pairwise_dist(rows)
    ratio = avg_osc_dist / avg_all_dist if avg_all_dist > 0 else float('nan')

    osc_qs = [r['com_q'] for r in osc_rows]
    osc_rs = [r['com_r'] for r in osc_rows]
    all_qs = [r['com_q'] for r in rows]
    all_rs = [r['com_r'] for r in rows]

    print(f"\n=== SPATIAL ANALYSIS ===", flush=True)
    print(f"  Oscillators : {len(osc_rows)}", flush=True)
    print(f"  Still-lifes : {len(sl_rows)}", flush=True)
    print(f"  Avg pairwise dist (oscillators only) : {avg_osc_dist:.2f}", flush=True)
    print(f"  Avg pairwise dist (all objects)       : {avg_all_dist:.2f}", flush=True)
    print(f"  Ratio osc/all                         : {ratio:.3f}", flush=True)
    if osc_qs:
        print(f"  Oscillator q range : [{min(osc_qs):.1f}, {max(osc_qs):.1f}]", flush=True)
        print(f"  Oscillator r range : [{min(osc_rs):.1f}, {max(osc_rs):.1f}]", flush=True)
    print(f"  All-obj q range    : [{min(all_qs):.1f}, {max(all_qs):.1f}]", flush=True)
    print(f"  All-obj r range    : [{min(all_rs):.1f}, {max(all_rs):.1f}]", flush=True)

    # Oscillator pairwise distances (for inspection)
    if len(osc_rows) >= 2:
        print(f"\n  Oscillator pairwise distances:", flush=True)
        for i in range(len(osc_rows)):
            for j in range(i + 1, len(osc_rows)):
                dq = osc_rows[i]['com_q'] - osc_rows[j]['com_q']
                dr = osc_rows[i]['com_r'] - osc_rows[j]['com_r']
                d = math.sqrt(dq**2 + dr**2)
                print(f"    obj{osc_rows[i]['object_id']} <-> obj{osc_rows[j]['object_id']}: "
                      f"{d:.2f}  ({osc_rows[i]['type']}/{osc_rows[j]['type']})", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
