#!/usr/bin/env python3
"""
characterize_remnant.py

Analyzes the composition of the stable remnant produced by rule_011 (iter_131).
Runs a 200-step simulation, extracts connected components, characterizes each
object in isolation to determine its period, catalogs unique oscillator types,
and writes summary YAML + per-type JSON files.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = Path(__file__).parent
RULE_PATH = PROJECT_ROOT / "archive" / "iter_131" / "population" / "rule_011.json"
ASH_PATTERN_PATH = SRC_DIR / "ash_pattern.json"
RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_133" / "results"
RESULT_YAML_PATH = PROJECT_ROOT / "archive" / "iter_133" / "result.yaml"

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
    """BFS connected-component labeling on the hex grid with wrapping."""
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
    """Return cell coordinates relative to the bounding-box minimum."""
    if not cells:
        return frozenset()
    qs = [c[0] for c in cells]
    rs = [c[1] for c in cells]
    min_q, min_r = min(qs), min(rs)
    return frozenset((q - min_q, r - min_r) for q, r in cells)


def canonical_phase_key(phases: list) -> tuple:
    """Minimum cyclic rotation of phase sequence for type-identity comparison."""
    if not phases:
        return ()
    canon = [tuple(sorted(p)) for p in phases]
    n = len(canon)
    return min(tuple(canon[i:] + canon[:i]) for i in range(n))


def characterize_object(cells: list, lut: np.ndarray,
                        max_steps: int = 100, padding: int = 50) -> tuple:
    """
    Run the object in isolation on a small grid to detect its period.

    Returns (status, period, phases):
      status  : 'still_life' | 'oscillator' | 'decayed' | 'unknown'
      period  : int (1 for still_life, 0 for decayed/unknown)
      phases  : list[frozenset] — one normalized shape per unique phase
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
    shapes_at_step: dict = {}

    for step in range(max_steps + 1):
        live = list(map(tuple, np.argwhere(iso == 1)))
        if not live:
            return 'decayed', 0, []

        norm = normalize_shape(live)

        if norm in shape_to_step:
            prev = shape_to_step[norm]
            period = step - prev
            phases = [shapes_at_step[s] for s in range(prev, step)]
            status = 'still_life' if period == 1 else 'oscillator'
            return status, period, phases

        shape_to_step[norm] = step
        shapes_at_step[step] = norm
        iso = step_grid(iso, lut)

    return 'unknown', 0, []


def make_type_id(period: int, bit_count: int, variant_idx: int) -> str:
    base = f"p{period}_{bit_count}bit"
    return base if variant_idx == 0 else f"{base}_v{variant_idx}"


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Loading rule: {RULE_PATH}", flush=True)
    with open(RULE_PATH) as f:
        rule_dict = json.load(f)
    lut = rule_to_lut(rule_dict)
    print(f"  {len(rule_dict)} rule entries loaded", flush=True)

    print(f"Loading ash pattern: {ASH_PATTERN_PATH}", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        if q < GRID_SIZE and r < GRID_SIZE:
            grid[q, r] = 1
    print(f"  {int(grid.sum())} bits on {GRID_SIZE}x{GRID_SIZE} grid", flush=True)

    print(f"\nRunning {RUN_STEPS} steps to generate stable remnant...", flush=True)
    for s in range(RUN_STEPS):
        grid = step_grid(grid, lut)
        if (s + 1) % 50 == 0:
            print(f"  step {s+1:3d}: {int(grid.sum())} bits", flush=True)
    remnant_bits = int(grid.sum())
    print(f"  Remnant: {remnant_bits} live cells", flush=True)

    print(f"\nFinding connected components...", flush=True)
    components = get_connected_components(grid, GRID_SIZE)
    total_objects = len(components)
    print(f"  Found {total_objects} objects", flush=True)

    print(f"\nCharacterizing objects in isolation (max {MAX_PERIOD_STEPS} steps each)...",
          flush=True)
    obj_results = []
    for i, comp in enumerate(components):
        status, period, phases = characterize_object(
            comp, lut, max_steps=MAX_PERIOD_STEPS, padding=ISO_PADDING
        )
        obj_results.append({
            'status': status,
            'period': period,
            'bit_count': len(comp),
            'phases': phases,
        })
        print(f"  [{i+1:3d}/{total_objects}] status={status:<12s} period={period:3d}  "
              f"bits={len(comp):3d}", flush=True)

    # Group by canonical type key
    type_groups: dict = {}
    for i, obj in enumerate(obj_results):
        if obj['status'] in ('decayed', 'unknown'):
            k = obj['status']
        else:
            k = (obj['period'], canonical_phase_key(obj['phases']))
        if k not in type_groups:
            type_groups[k] = []
        type_groups[k].append(i)

    still_life_count = sum(1 for o in obj_results if o['period'] == 1)
    decayed_count = sum(1 for o in obj_results if o['status'] == 'decayed')
    osc_type_keys = {k: v for k, v in type_groups.items()
                     if k not in ('decayed', 'unknown')}
    unique_type_count = len(osc_type_keys)

    # Assign IDs and write per-type JSON files
    type_counts: dict = {}
    variant_counter: dict = defaultdict(int)
    sorted_keys = sorted(
        osc_type_keys.keys(),
        key=lambda k: (k[0], -len(osc_type_keys[k]))
    )

    print(f"\nCataloging {unique_type_count} unique oscillator type(s)...", flush=True)
    for key in sorted_keys:
        indices = osc_type_keys[key]
        rep = obj_results[indices[0]]
        period = rep['period']
        bit_count = rep['bit_count']
        base = (period, bit_count)
        vidx = variant_counter[base]
        variant_counter[base] += 1
        type_id = make_type_id(period, bit_count, vidx)
        type_counts[type_id] = len(indices)

        phases_list = [
            sorted([[int(q), int(r)] for q, r in phase])
            for phase in rep['phases']
        ]
        json_path = RESULTS_DIR / f"{type_id}.json"
        with open(json_path, 'w') as f:
            json.dump({'period': period, 'bit_count': bit_count, 'phases': phases_list},
                      f, indent=2)
        print(f"  {type_id}: count={len(indices)}, period={period}, bits={bit_count}",
              flush=True)

    if decayed_count > 0:
        type_counts['decayed'] = decayed_count

    result = {
        'total_objects_in_remnant': total_objects,
        'unique_oscillator_types_count': unique_type_count,
        'still_life_count': still_life_count,
        'decayed_count': decayed_count,
        'type_counts': type_counts,
    }
    with open(RESULT_YAML_PATH, 'w') as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)

    print(f"\nSaved: {RESULT_YAML_PATH}", flush=True)
    print(f"\n=== RESULTS ===", flush=True)
    print(f"  total_objects_in_remnant:    {total_objects}", flush=True)
    print(f"  unique_oscillator_types_count: {unique_type_count}", flush=True)
    print(f"  still_life_count:            {still_life_count}", flush=True)
    print(f"  decayed_count:               {decayed_count}", flush=True)
    for tid, cnt in type_counts.items():
        print(f"    {tid}: {cnt}", flush=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
