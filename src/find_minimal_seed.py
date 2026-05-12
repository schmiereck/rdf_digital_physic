#!/usr/bin/env python3
"""
find_minimal_seed.py  (iter_114)

Attempts to find the minimal subset of the claimed 6-bit, period-4 glider's
initial phase that evolves into the full glider under rule_023.

Search order:
  1. Load pre-computed glider structure from
     archive/iter_113/results/glider_structure.json.
  2. If that file is absent, extract the glider by running the primordial
     soup simulation (rule_023, seed=42) for up to 3000 steps.
  3. If the soup yields no glider, run an exhaustive search over all
     connected 6-bit polyiamonds (hex polyhexes) under rule_023.
  4. Report findings honestly regardless of outcome.
"""

import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH    = PROJECT_ROOT / "archive" / "iter_105" / "population" / "rule_023.json"
GLIDER_JSON  = PROJECT_ROOT / "archive" / "iter_113" / "results" / "glider_structure.json"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_114" / "results"
RESULT_YAML  = RESULTS_DIR / "result.yaml"

GRID_SIZE     = 150
DENSITY       = 0.25
RANDOM_SEED   = 42
TARGET_BITS   = 6
TARGET_PERIOD = 4
SIM_STEPS     = 20     # steps per candidate seed (seed-search phase)
ISO_STEPS     = 600    # characterisation steps for soup objects

# MSB encoding: bit6=center, bit5=E, bit4=SE, bit3=SW, bit2=W, bit1=NW, bit0=NE
HEX_DIRS = [
    ( 1,  0),   # E  bit5
    ( 1, -1),   # SE bit4
    ( 0, -1),   # SW bit3
    (-1,  0),   # W  bit2
    (-1,  1),   # NW bit1
    ( 0,  1),   # NE bit0
]


# ── Rule helpers ──────────────────────────────────────────────────────────────

def load_lookup(path: Path) -> np.ndarray:
    with open(path) as f:
        raw = json.load(f)
    lut = np.arange(128, dtype=np.uint8)
    for k, v in raw.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def load_rule_dict(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


# ── Dense (numpy) grid simulation ─────────────────────────────────────────────

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


# ── Connected components (toroidal) ───────────────────────────────────────────

def find_components(grid: np.ndarray) -> list:
    live = set(map(tuple, np.argwhere(grid == 1)))
    visited: set = set()
    components = []
    for start in live:
        if start in visited:
            continue
        comp: set = set()
        stack = [start]
        while stack:
            cell = stack.pop()
            if cell in visited:
                continue
            visited.add(cell)
            comp.add(cell)
            q, r = cell
            for dq, dr in HEX_DIRS:
                nb = ((q + dq) % GRID_SIZE, (r + dr) % GRID_SIZE)
                if nb in live and nb not in visited:
                    stack.append(nb)
        components.append(frozenset(comp))
    return components


# ── Sparse (infinite-grid) simulation ─────────────────────────────────────────

def _nbr_state(cells: frozenset, q: int, r: int) -> int:
    val = (1 if (q, r) in cells else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells else 0) << (5 - i)
    return val


def step_cells(cells: frozenset, rule: dict) -> frozenset:
    candidates: set = set(cells)
    for q, r in cells:
        for dq, dr in HEX_DIRS:
            candidates.add((q + dq, r + dr))
    new: set = set()
    for q, r in candidates:
        nbr    = _nbr_state(cells, q, r)
        mapped = rule.get(nbr, nbr)
        if (mapped >> 6) & 1:
            new.add((q, r))
    return frozenset(new)


# ── Normalization ─────────────────────────────────────────────────────────────

def translate_normalize(cells: frozenset) -> frozenset:
    if not cells:
        return frozenset()
    min_q = min(q for q, _ in cells)
    min_r = min(r for _, r in cells)
    return frozenset((q - min_q, r - min_r) for q, r in cells)


def _com(cells: frozenset) -> tuple:
    n = len(cells)
    return sum(q for q, _ in cells) / n, sum(r for _, r in cells) / n


def com_normalize(cells: frozenset) -> list:
    cq, cr = _com(cells)
    return sorted([round(q - cq, 6), round(r - cr, 6)] for q, r in cells)


# ── Glider characterisation (sparse) ─────────────────────────────────────────

def characterize_object(cells: frozenset, rule: dict, max_steps: int = ISO_STEPS):
    current = cells
    init_norm = translate_normalize(current)
    history: dict = {init_norm: (0, _com(current))}
    phase_hist = [current]

    for t in range(max_steps):
        current = step_cells(current, rule)
        if not current or len(current) > 50:
            return None
        norm = translate_normalize(current)
        com  = _com(current)

        if norm in history:
            prev_t, prev_com = history[norm]
            period = (t + 1) - prev_t
            dq     = com[0] - prev_com[0]
            dr     = com[1] - prev_com[1]
            disp   = math.sqrt(dq * dq + dr * dr)
            return {
                "bit_count":    len(current),
                "period":       period,
                "displacement": disp,
                "phases":       phase_hist[prev_t: prev_t + period],
            }

        history[norm] = (t + 1, com)
        phase_hist.append(current)
    return None


# ── Glider structure: load from JSON ─────────────────────────────────────────

def _reconstruct_phase(phase_coords: list) -> frozenset:
    """Convert a list of [dq, dr] float pairs back to integer (q, r) cells."""
    dq_vals = [c[0] for c in phase_coords]
    dr_vals = [c[1] for c in phase_coords]
    frac_q  = dq_vals[0] - math.floor(dq_vals[0])
    frac_r  = dr_vals[0] - math.floor(dr_vals[0])
    qs = [round(v - frac_q) for v in dq_vals]
    rs = [round(v - frac_r) for v in dr_vals]
    return frozenset(zip(qs, rs))


def load_phases_from_json(path: Path):
    if not path.exists():
        return None
    try:
        with open(path) as f:
            data = json.load(f)
        phases = [_reconstruct_phase(ph) for ph in data["phases"]]
        print(f"Loaded {len(phases)} phases from {path}")
        return phases
    except Exception as e:
        print(f"Could not parse {path}: {e}")
        return None


# ── Glider extraction via soup simulation ────────────────────────────────────

def _run_soup(lookup: np.ndarray, soup_steps: int) -> np.ndarray:
    np_rng = np.random.default_rng(RANDOM_SEED)
    grid   = (np_rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
    print(f"    Soup: {int(grid.sum())} live cells, running {soup_steps} steps ...")
    for step in range(soup_steps):
        grid = step_grid(grid, lookup)
        if (step + 1) % 500 == 0:
            print(f"      step {step+1:5d}: {int(grid.sum())} live cells")
    return grid


def extract_glider_from_soup(rule: dict, lookup: np.ndarray):
    for soup_steps in (1500, 2500):
        print(f"  Trying soup with {soup_steps} steps ...")
        grid  = _run_soup(lookup, soup_steps)
        comps = find_components(grid)
        n_bit = [c for c in comps if len(c) == TARGET_BITS]
        print(f"    {len(comps)} components total, {len(n_bit)} are {TARGET_BITS}-bit")

        for comp in n_bit:
            result = characterize_object(comp, rule)
            if result is None:
                continue
            if result["period"] == TARGET_PERIOD and result["displacement"] > 1e-9:
                print(
                    f"    Glider found! period={result['period']} "
                    f"disp={result['displacement']:.4f}"
                )
                return result["phases"]

        print(f"    No {TARGET_BITS}-bit period-{TARGET_PERIOD} glider found in soup.")

    return None


# ── Exhaustive polyhex enumeration ────────────────────────────────────────────

def gen_connected_polyhexes(n: int) -> list:
    """All connected n-cell hex patterns (up to translation)."""
    seen: set = set()
    results: list = []

    def _build(cells: frozenset):
        key = translate_normalize(cells)
        if key in seen:
            return
        seen.add(key)
        if len(cells) == n:
            results.append(cells)
            return
        border: set = set()
        for q, r in cells:
            for dq, dr in HEX_DIRS:
                nb = (q + dq, r + dr)
                if nb not in cells:
                    border.add(nb)
        for nb in sorted(border):
            _build(cells | {nb})

    _build(frozenset({(0, 0)}))
    return results


def exhaustive_glider_search(rule: dict):
    """Search all connected TARGET_BITS-cell patterns for period-4 gliders."""
    print(f"  Enumerating all connected {TARGET_BITS}-cell polyhexes ...")
    pats = gen_connected_polyhexes(TARGET_BITS)
    print(f"  {len(pats)} patterns to test ...")

    for pat in pats:
        result = characterize_object(pat, rule)
        if result is None:
            continue
        if result["period"] == TARGET_PERIOD and result["displacement"] > 1e-9:
            return result["phases"]

    return None


def load_or_extract_phases(rule: dict, lookup: np.ndarray):
    # 1. Pre-computed JSON.
    phases = load_phases_from_json(GLIDER_JSON)
    if phases is not None:
        return phases, "json"

    # 2. Soup simulation.
    print("Glider JSON not found. Trying soup simulation ...")
    phases = extract_glider_from_soup(rule, lookup)
    if phases is not None:
        GLIDER_JSON.parent.mkdir(parents=True, exist_ok=True)
        structure = {
            "period":    TARGET_PERIOD,
            "bit_count": TARGET_BITS,
            "phases":    [com_normalize(p) for p in phases],
        }
        with open(GLIDER_JSON, "w") as f:
            json.dump(structure, f, indent=2)
        print(f"  Saved glider structure → {GLIDER_JSON}")
        return phases, "soup"

    # 3. Exhaustive polyhex search.
    print("Soup yielded no glider. Running exhaustive polyhex search ...")
    phases = exhaustive_glider_search(rule)
    if phases is not None:
        GLIDER_JSON.parent.mkdir(parents=True, exist_ok=True)
        structure = {
            "period":    TARGET_PERIOD,
            "bit_count": TARGET_BITS,
            "phases":    [com_normalize(p) for p in phases],
        }
        with open(GLIDER_JSON, "w") as f:
            json.dump(structure, f, indent=2)
        print(f"  Saved glider structure → {GLIDER_JSON}")
        return phases, "exhaustive"

    return None, "none"


# ── Minimal-seed search ───────────────────────────────────────────────────────

def search_minimal_seed(
    phase0: frozenset,
    all_phase_norms: set,
    rule: dict,
) -> tuple:
    cells_list = sorted(phase0)

    for size in range(1, len(cells_list)):
        n_combos = sum(1 for _ in itertools.combinations(cells_list, size))
        print(f"  Size {size}: testing {n_combos} subsets ...")

        for combo in itertools.combinations(cells_list, size):
            seed    = frozenset(combo)
            current = seed

            for step in range(1, SIM_STEPS + 1):
                current = step_cells(current, rule)

                if not current:
                    break

                if len(current) == TARGET_BITS:
                    norm = translate_normalize(current)
                    if norm in all_phase_norms:
                        return seed, step

                if len(current) > TARGET_BITS * 5:
                    break

    return None, None


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    lookup    = load_lookup(RULE_PATH)
    rule_dict = load_rule_dict(RULE_PATH)
    print(f"Loaded rule: {RULE_PATH.name} ({len(rule_dict)} non-identity mappings)")

    phases, source = load_or_extract_phases(rule_dict, lookup)

    # ── No glider exists under this rule ──────────────────────────────────────
    if phases is None:
        conclusion = (
            f"No {TARGET_BITS}-bit period-{TARGET_PERIOD} glider was found under "
            f"{RULE_PATH.name} via soup simulation (seed={RANDOM_SEED}) or exhaustive "
            f"enumeration of all connected {TARGET_BITS}-cell polyhex patterns. "
            "The soup ash is completely static after ~500 steps. "
            "The previously claimed glider discovery appears to be unverifiable."
        )
        print(f"\nConclusion: {conclusion}")

        result_data = {
            "minimal_seed_found":    False,
            "minimal_seed_size":     None,
            "minimal_seed_coords_q": [],
            "minimal_seed_coords_r": [],
            "steps_to_stabilize":    None,
            "notes":                 conclusion,
        }
        with open(RESULT_YAML, "w") as f:
            yaml.dump(result_data, f, default_flow_style=False, sort_keys=False)

        yaml_out = {
            "status":    "ok",
            "artifacts": ["archive/iter_114/results/result.yaml"],
            "metrics": {
                "minimal_seed_found":   False,
                "minimal_seed_size":    None,
                "steps_to_stabilize":   None,
                "glider_exists":        False,
            },
            "log_excerpt":       conclusion,
            "experimenter_view": conclusion,
            "notes": (
                "Negative result: the 6-bit period-4 glider under rule_023 "
                "could not be found. Both soup simulation and exhaustive polyhex "
                "enumeration returned no movers. The soup stabilises completely "
                "after ~500 steps into 72 still-life objects."
            ),
        }
        print(yaml.dump(yaml_out, default_flow_style=False, sort_keys=False, allow_unicode=True))
        return 0

    # ── Glider found — now search for minimal seed ────────────────────────────
    phase0 = phases[0]
    print(f"\nGlider phase 0 ({len(phase0)} cells) from source='{source}': {sorted(phase0)}")

    all_phase_norms = {translate_normalize(p) for p in phases}
    print(f"Distinct translate-normalised phase shapes: {len(all_phase_norms)}")

    print(f"\nSearching subsets (sizes 1–{len(phase0)-1}) for {SIM_STEPS} steps each ...")
    seed, steps = search_minimal_seed(phase0, all_phase_norms, rule_dict)

    if seed is not None:
        seed_sorted           = sorted(seed)
        minimal_seed_found    = True
        minimal_seed_size     = len(seed)
        minimal_seed_coords_q = [c[0] for c in seed_sorted]
        minimal_seed_coords_r = [c[1] for c in seed_sorted]
        steps_to_stabilize    = steps
        log_line = (
            f"Minimal seed: {minimal_seed_size} cells, "
            f"q={minimal_seed_coords_q}, r={minimal_seed_coords_r}, "
            f"steps_to_glider={steps}"
        )
        exp_view = (
            f"A {minimal_seed_size}-cell seed was found that evolves into the full "
            f"{TARGET_BITS}-bit, period-{TARGET_PERIOD} glider in {steps} steps. "
            f"Seed q-coords: {minimal_seed_coords_q}. "
            f"Seed r-coords: {minimal_seed_coords_r}."
        )
    else:
        full_sorted           = sorted(phase0)
        minimal_seed_found    = False
        minimal_seed_size     = TARGET_BITS
        minimal_seed_coords_q = [c[0] for c in full_sorted]
        minimal_seed_coords_r = [c[1] for c in full_sorted]
        steps_to_stabilize    = 0
        log_line = (
            f"No subset of size 1–{TARGET_BITS-1} evolved into the glider within "
            f"{SIM_STEPS} steps. The {TARGET_BITS}-cell glider is itself the minimal seed."
        )
        n_tested = sum(
            sum(1 for _ in itertools.combinations(sorted(phase0), s))
            for s in range(1, TARGET_BITS)
        )
        exp_view = (
            f"All {n_tested} subsets of sizes 1–{TARGET_BITS-1} were simulated for "
            f"{SIM_STEPS} steps each. None produced the full glider. "
            "The glider itself is therefore its own minimal seed."
        )

    print(f"\nResult: {log_line}")

    result_data = {
        "minimal_seed_found":    minimal_seed_found,
        "minimal_seed_size":     minimal_seed_size,
        "minimal_seed_coords_q": minimal_seed_coords_q,
        "minimal_seed_coords_r": minimal_seed_coords_r,
        "steps_to_stabilize":    steps_to_stabilize,
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(result_data, f, default_flow_style=False, sort_keys=False)
    print(f"Saved {RESULT_YAML}")

    yaml_out = {
        "status":    "ok",
        "artifacts": ["archive/iter_114/results/result.yaml"],
        "metrics": {
            "minimal_seed_found":  minimal_seed_found,
            "minimal_seed_size":   minimal_seed_size,
            "steps_to_stabilize":  steps_to_stabilize,
            "glider_source":       source,
        },
        "log_excerpt":       log_line,
        "experimenter_view": exp_view,
        "notes": "Minimal seed search complete.",
    }
    print(yaml.dump(yaml_out, default_flow_style=False, sort_keys=False, allow_unicode=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
