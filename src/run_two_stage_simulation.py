#!/usr/bin/env python3
"""
run_two_stage_simulation.py  (iter_118)

Stage 1 (Cooling): Run rule_023 on a 150x150 random soup for 1000 steps to
                   produce a stable ash.
Stage 2 (Motion):  Initialize a new grid from the ash coordinates, then run
                   symmetric_rule_nonconserving_A3_B14 for 1000 steps and
                   classify all resulting objects.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT      = Path(__file__).parent.parent
COOLING_RULE_PATH = PROJECT_ROOT / "archive" / "iter_105" / "population" / "rule_023.json"
MOTION_RULE_PATH  = Path(__file__).parent / "symmetric_rule_nonconserving_A3_B14.json"
RESULT_DIR        = PROJECT_ROOT / "archive" / "iter_118"
RESULT_YAML       = RESULT_DIR / "result.yaml"

GRID_SIZE          = 150
DENSITY            = 0.25
COOLING_STEPS      = 1000
MOTION_STEPS       = 1000
RANDOM_SEED        = 42
CHAR_STEPS         = 100
MAX_COMPONENT_SIZE = 200

# MSB encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
HEX_DIRS = [
    ( 1,  0),   # E  (bit5)
    ( 1, -1),   # SE (bit4)
    ( 0, -1),   # SW (bit3)
    (-1,  0),   # W  (bit2)
    (-1,  1),   # NW (bit1)
    ( 0,  1),   # NE (bit0)
]


# ── Rule loading ───────────────────────────────────────────────────────────────

def load_lookup(path: Path) -> np.ndarray:
    """128-element array: lookup[neighborhood_state] = new center bit (0 or 1)."""
    with open(path) as f:
        raw = json.load(f)
    lut = np.arange(128, dtype=np.uint8)
    for k, v in raw.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def load_rule_dict(path: Path) -> dict:
    """Rule as {int state -> int output_state} for sparse simulation."""
    with open(path) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


# ── Dense numpy grid (toroidal) ────────────────────────────────────────────────

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


# ── Connected components (toroidal) ────────────────────────────────────────────

def find_components(grid: np.ndarray) -> list:
    live = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    components = []

    for start in live:
        if start in visited:
            continue
        component: set = set()
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            component.add(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % GRID_SIZE, (r + dr) % GRID_SIZE)
                if nb in live and nb not in visited:
                    stack.append(nb)
        components.append(frozenset(component))

    return components


# ── Sparse CA step (infinite grid) ────────────────────────────────────────────

def _neighborhood(cells_set: frozenset, q: int, r: int) -> int:
    val = (1 if (q, r) in cells_set else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells_set else 0) << (5 - i)
    return val


def step_cells(cells: frozenset, rule: dict) -> frozenset:
    candidates: set = set(cells)
    for q, r in cells:
        for dq, dr in HEX_DIRS:
            candidates.add((q + dq, r + dr))
    new_cells: set = set()
    for q, r in candidates:
        nbr    = _neighborhood(cells, q, r)
        mapped = rule.get(nbr, nbr)
        if (mapped >> 6) & 1:
            new_cells.add((q, r))
    return frozenset(new_cells)


def _translate_normalize(cells: frozenset) -> frozenset:
    if not cells:
        return frozenset()
    sc = sorted(cells)
    q0, r0 = sc[0]
    return frozenset((q - q0, r - r0) for q, r in sc)


def _center_of_mass(cells: frozenset) -> tuple:
    n = len(cells)
    return (sum(q for q, _ in cells) / n, sum(r for _, r in cells) / n)


# ── Object characterization ────────────────────────────────────────────────────

def characterize_object(cells: frozenset, rule: dict, max_steps: int = CHAR_STEPS):
    """
    Simulate isolated object for up to max_steps steps on infinite grid.
    Returns dict with period, dq, dr, bit_count, kind; or None if no cycle found.
    """
    current = cells
    init_shape = _translate_normalize(current)
    history: dict = {init_shape: (0, _center_of_mass(current))}

    for t in range(max_steps):
        current = step_cells(current, rule)

        if len(current) == 0 or len(current) > MAX_COMPONENT_SIZE:
            return None

        shape = _translate_normalize(current)
        com   = _center_of_mass(current)

        if shape in history:
            prev_t, prev_com = history[shape]
            period      = (t + 1) - prev_t
            dq_f        = com[0] - prev_com[0]
            dr_f        = com[1] - prev_com[1]
            displacement = math.sqrt(dq_f * dq_f + dr_f * dr_f)
            dq          = round(dq_f)
            dr          = round(dr_f)

            if period == 1 and displacement < 1e-9:
                kind = "still_life"
            elif displacement > 1e-9:
                kind = "glider"
            else:
                kind = "oscillator"

            return {
                "bit_count":    len(current),
                "period":       period,
                "dq":           dq,
                "dr":           dr,
                "displacement": displacement,
                "kind":         kind,
            }

        history[shape] = (t + 1, com)

    return None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Stage 1: Cooling ──────────────────────────────────────────────────────

    print("=== Stage 1: Cooling ===")
    cooling_lookup = load_lookup(COOLING_RULE_PATH)
    print(f"Loaded cooling rule: {COOLING_RULE_PATH.name}")

    np_rng = np.random.default_rng(RANDOM_SEED)
    grid   = (np_rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
    print(f"Initial soup: {int(grid.sum())} live cells  "
          f"({GRID_SIZE}x{GRID_SIZE}, density={DENSITY}, seed={RANDOM_SEED})")

    for step in range(COOLING_STEPS):
        grid = step_grid(grid, cooling_lookup)
        if (step + 1) % 200 == 0:
            print(f"  Step {step+1:5d}: {int(grid.sum()):6d} live cells")

    ash_bit_count = int(grid.sum())
    print(f"Cooling complete. Ash: {ash_bit_count} live cells")

    ash_coords = list(map(tuple, np.argwhere(grid == 1)))

    # ── Stage 2: Motion ───────────────────────────────────────────────────────

    print("\n=== Stage 2: Motion ===")
    motion_lookup = load_lookup(MOTION_RULE_PATH)
    motion_rule   = load_rule_dict(MOTION_RULE_PATH)
    print(f"Loaded motion rule: {MOTION_RULE_PATH.name}")

    grid2 = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for q, r in ash_coords:
        grid2[q, r] = 1
    print(f"Stage 2 init: {int(grid2.sum())} live cells")

    for step in range(MOTION_STEPS):
        grid2 = step_grid(grid2, motion_lookup)
        if (step + 1) % 200 == 0:
            print(f"  Step {step+1:5d}: {int(grid2.sum()):6d} live cells")

    final_bit_count = int(grid2.sum())
    print(f"Motion complete. Final: {final_bit_count} live cells")

    # ── Characterize objects ──────────────────────────────────────────────────

    print("\n=== Characterizing Objects ===")
    components = find_components(grid2)
    print(f"Connected components found: {len(components)}")

    glider_count     = 0
    oscillator_count = 0
    still_life_count = 0
    first_glider     = None

    for i, comp in enumerate(components):
        if len(comp) > MAX_COMPONENT_SIZE:
            continue
        result = characterize_object(comp, motion_rule)
        if result is None:
            continue
        kind = result["kind"]
        if kind == "glider":
            glider_count += 1
            if first_glider is None:
                first_glider = result
            print(f"  Component {i:4d}: GLIDER   bits={result['bit_count']:3d}  "
                  f"period={result['period']:3d}  "
                  f"dq={result['dq']:+d}  dr={result['dr']:+d}")
        elif kind == "oscillator":
            oscillator_count += 1
        elif kind == "still_life":
            still_life_count += 1

    print(f"\nResults:")
    print(f"  glider_count:     {glider_count}")
    print(f"  oscillator_count: {oscillator_count}")
    print(f"  still_life_count: {still_life_count}")
    print(f"  ash_bit_count:    {ash_bit_count}")
    print(f"  final_bit_count:  {final_bit_count}")

    # ── Write result.yaml ─────────────────────────────────────────────────────

    yaml_result: dict = {
        "glider_count":     glider_count,
        "oscillator_count": oscillator_count,
        "still_life_count": still_life_count,
        "ash_bit_count":    ash_bit_count,
        "final_bit_count":  final_bit_count,
    }

    if first_glider is not None:
        yaml_result["glider_period"]    = int(first_glider["period"])
        yaml_result["glider_bit_count"] = int(first_glider["bit_count"])
        yaml_result["glider_velocity"]  = [int(first_glider["dq"]), int(first_glider["dr"])]

    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWritten: {RESULT_YAML}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
