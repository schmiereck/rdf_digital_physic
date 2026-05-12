#!/usr/bin/env python3
"""
extract_glider_structure.py  (iter_114)

Re-runs the primordial soup experiment from iter_110 using rule_023 and seed 42,
identifies all 6-bit period-4 moving objects (gliders) in the resulting ash, and
saves the four-phase structure of the first found glider to a JSON file.
"""

import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_105" / "population" / "rule_023.json"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_114" / "results"
RESULT_YAML  = PROJECT_ROOT / "archive" / "iter_114" / "result.yaml"
GLIDER_JSON  = RESULTS_DIR / "glider_structure.json"

GRID_SIZE   = 150
DENSITY     = 0.25
SOUP_STEPS  = 1000
ISO_STEPS   = 200
RANDOM_SEED = 42

# MSB encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
HEX_DIRS = [
    ( 1,  0),   # E  (bit5)
    ( 1, -1),   # SE (bit4)
    ( 0, -1),   # SW (bit3)
    (-1,  0),   # W  (bit2)
    (-1,  1),   # NW (bit1)
    ( 0,  1),   # NE (bit0)
]

TARGET_BITS   = 6
TARGET_PERIOD = 4
MAX_COMPONENT_SIZE = 50   # skip components larger than this (chaotic blobs)


# ── Rule loading ───────────────────────────────────────────────────────────────

def load_lookup(path: Path) -> np.ndarray:
    """128-element array: lookup[neighborhood_state] = new center bit (0 or 1)."""
    with open(path) as f:
        raw = json.load(f)
    lookup_output = np.arange(128, dtype=np.uint8)
    for k, v in raw.items():
        lookup_output[int(k)] = int(v)
    return ((lookup_output >> 6) & 1).astype(np.uint8)


def load_rule_dict(path: Path) -> dict:
    """Rule as {int state -> int output_state} for sparse simulation."""
    with open(path) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


# ── Dense numpy grid simulation ────────────────────────────────────────────────

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


# ── Connected-components on toroidal grid ──────────────────────────────────────

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


# ── Sparse CA step (infinite grid, no wrapping) ───────────────────────────────

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

def characterize_object(cells: frozenset, rule: dict, max_steps: int = ISO_STEPS):
    """
    Simulate an isolated object for up to max_steps steps on an infinite grid.
    Returns a dict with period, bit_count, dq, dr, displacement, and phases
    (one frozenset per step of the period), or None if no cycle is found.
    """
    current = cells
    init_shape = _translate_normalize(current)
    history: dict = {init_shape: (0, _center_of_mass(current))}
    phase_history = [current]

    for t in range(max_steps):
        current = step_cells(current, rule)

        if len(current) == 0 or len(current) > MAX_COMPONENT_SIZE:
            return None

        shape = _translate_normalize(current)
        com   = _center_of_mass(current)

        if shape in history:
            prev_t, prev_com = history[shape]
            period = (t + 1) - prev_t
            dq     = com[0] - prev_com[0]
            dr     = com[1] - prev_com[1]
            displacement = math.sqrt(dq * dq + dr * dr)
            phases = phase_history[prev_t : prev_t + period]
            return {
                "bit_count":    len(current),
                "period":       period,
                "dq":           dq,
                "dr":           dr,
                "displacement": displacement,
                "phases":       phases,
            }

        history[shape] = (t + 1, com)
        phase_history.append(current)

    return None


# ── Phase normalization ────────────────────────────────────────────────────────

def normalize_phases(phases: list) -> list:
    """
    For each phase frozenset, subtract the center of mass from every cell
    coordinate and return a sorted list of [dq, dr] pairs (rounded to 6 dp).
    """
    result = []
    for phase in phases:
        com_q, com_r = _center_of_mass(phase)
        normalized = sorted(
            [round(q - com_q, 6), round(r - com_r, 6)]
            for q, r in phase
        )
        result.append(normalized)
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load rule
    lookup    = load_lookup(RULE_PATH)
    rule_dict = load_rule_dict(RULE_PATH)
    print(f"Loaded rule: {RULE_PATH.name}  ({len(rule_dict)} non-identity mappings)")

    # Create primordial soup (same seed and parameters as iter_105)
    np_rng = np.random.default_rng(RANDOM_SEED)
    grid   = (np_rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
    print(f"Initial soup: {int(grid.sum())} live cells "
          f"({GRID_SIZE}x{GRID_SIZE}, density={DENSITY}, seed={RANDOM_SEED})")

    # Run soup for SOUP_STEPS steps
    print(f"Simulating {SOUP_STEPS} steps ...")
    for step in range(SOUP_STEPS):
        grid = step_grid(grid, lookup)
        if (step + 1) % 200 == 0:
            print(f"  Step {step+1:5d}: {int(grid.sum()):6d} live cells")

    final_count = int(grid.sum())
    print(f"Final ash: {final_count} live cells")

    # Find all connected objects
    components = find_components(grid)
    total_objects = len(components)
    print(f"Connected components found: {total_objects}")

    # Characterize each component in isolation
    print("Characterizing objects ...")
    gliders = []
    for i, comp in enumerate(components):
        if len(comp) > MAX_COMPONENT_SIZE:
            continue
        result = characterize_object(comp, rule_dict)
        if result is None:
            continue
        if (result["bit_count"] == TARGET_BITS
                and result["period"] == TARGET_PERIOD
                and result["displacement"] > 1e-9):
            print(f"  Component {i:3d}: GLIDER  bits={result['bit_count']}  "
                  f"period={result['period']}  "
                  f"displacement={result['displacement']:.4f}  "
                  f"(dq={result['dq']:.1f}, dr={result['dr']:.1f})")
            gliders.append(result)

    gliders_found = len(gliders)
    print(f"\nTotal gliders found: {gliders_found}")

    # ── Save structure ─────────────────────────────────────────────────────────

    if gliders_found == 0:
        print("ERROR: no 6-bit period-4 glider found in the ash.")
        yaml_result = {
            "status": "error",
            "metrics": {
                "gliders_found":        0,
                "total_stable_objects": total_objects,
            },
            "experimenter_view": (
                f"No 6-bit period-4 glider was found after {SOUP_STEPS} steps. "
                f"The ash contained {total_objects} connected objects."
            ),
        }
        with open(RESULT_YAML, "w") as f:
            yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
        return 1

    first = gliders[0]
    phases_norm = normalize_phases(first["phases"])

    structure = {
        "period":    TARGET_PERIOD,
        "bit_count": TARGET_BITS,
        "phases":    phases_norm,
    }
    with open(GLIDER_JSON, "w") as f:
        json.dump(structure, f, indent=2)

    print(f"\nSaved glider structure: {GLIDER_JSON}")
    for i, ph in enumerate(phases_norm):
        print(f"  Phase {i}: {ph}")

    experimenter_view = (
        f"Re-ran the primordial soup experiment (rule_023, {GRID_SIZE}x{GRID_SIZE}, "
        f"seed={RANDOM_SEED}, {SOUP_STEPS} steps). "
        f"The ash contained {total_objects} connected objects, of which "
        f"{gliders_found} matched the 6-bit period-4 glider signature. "
        f"The file archive/iter_114/results/glider_structure.json was created and "
        f"contains {len(phases_norm)} phases, each listing the "
        f"{len(phases_norm[0])} center-of-mass-normalized [dq, dr] coordinates "
        f"of the glider for that phase of its cycle."
    )

    yaml_result = {
        "status": "ok",
        "metrics": {
            "gliders_found":        gliders_found,
            "total_stable_objects": total_objects,
        },
        "experimenter_view": experimenter_view,
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
    print(f"Saved result.yaml: {RESULT_YAML}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
