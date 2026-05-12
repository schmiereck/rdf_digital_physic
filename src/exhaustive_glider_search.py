#!/usr/bin/env python3
"""
exhaustive_glider_search.py  (iter_115)

Exhaustive search for small gliders under the four 'interesting' cooling rules
from iter_105 (rule_023, rule_029, rule_055, rule_081).

For each rule and each seed size n in {3,4,5,6,7}:
  1. Generate every canonical connected n-cell polyhex (dedup by translation + C2).
  2. Simulate each seed for up to 1000 steps with a sparse representation
     (equivalent to a 200x200 grid; nothing wraps because we use an infinite plane).
  3. Detect cycles by hashing the translate-normalised set of live cells.
  4. If a cycle is found and the centre-of-mass shifts by > 1e-6 cells over one
     full cycle, declare a glider and terminate immediately.

Hex neighbourhood encoding (MSB = centre):
  state = centre*64 + b1*32 + b2*16 + b3*8 + b4*4 + b5*2 + b6
  b1=E, b2=SE, b3=SW, b4=W, b5=NW, b6=NE
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).parent.parent
RULES_DIR    = PROJECT_ROOT / "archive" / "iter_105" / "population"
RULE_FILES   = ["rule_023.json", "rule_029.json", "rule_055.json", "rule_081.json"]
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_115" / "results"
RESULT_YAML  = RESULTS_DIR / "result.yaml"

MIN_SEED_BITS = 3
MAX_SEED_BITS = 7
MAX_STEPS     = 1000
MAX_CELLS     = 50          # explosion cap (skip patterns that grow huge)
DISP_EPSILON  = 1e-6

HEX_DIRS = [
    ( 1,  0),  # b1 E
    ( 1, -1),  # b2 SE
    ( 0, -1),  # b3 SW
    (-1,  0),  # b4 W
    (-1,  1),  # b5 NW
    ( 0,  1),  # b6 NE
]


# ── Rule I/O ──────────────────────────────────────────────────────────────────

def load_rule(path: Path) -> dict:
    with open(path) as f:
        raw = json.load(f)
    return {int(k): int(v) for k, v in raw.items()}


# ── Sparse CA step (infinite plane) ───────────────────────────────────────────

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


# ── Geometric helpers ─────────────────────────────────────────────────────────

def translate_normalize(cells) -> frozenset:
    if not cells:
        return frozenset()
    min_q = min(q for q, _ in cells)
    min_r = min(r for _, r in cells)
    return frozenset((q - min_q, r - min_r) for q, r in cells)


def c2_rotate(cells) -> frozenset:
    """180° rotation in axial hex coords: (q, r) -> (-q, -r)."""
    return frozenset((-q, -r) for q, r in cells)


def canonical_key(cells) -> tuple:
    """Canonical key under translation + C2 (the rule's actual symmetry group)."""
    a = tuple(sorted(translate_normalize(cells)))
    b = tuple(sorted(translate_normalize(c2_rotate(cells))))
    return min(a, b)


def centroid(cells) -> tuple:
    n = len(cells)
    return (sum(q for q, _ in cells) / n,
            sum(r for _, r in cells) / n)


# ── Polyhex enumeration ───────────────────────────────────────────────────────

def generate_canonical_polyhexes(max_n: int) -> dict:
    """
    Return {n: list_of_frozensets} for n=1..max_n.

    Iterative breadth-first: at each step, take every canonical k-polyhex,
    enumerate its empty neighbours, build (k+1)-polyhexes, and canonicalise.
    The canonical form dedupes equivalent shapes under translation + C2 rotation.
    """
    by_size: dict = {}
    start = frozenset({(0, 0)})
    current_keys = {canonical_key(start)}
    by_size[1] = [start]

    for k in range(1, max_n):
        next_keys: set = set()
        for prev_key in current_keys:
            cells = frozenset(prev_key)
            border: set = set()
            for q, r in cells:
                for dq, dr in HEX_DIRS:
                    nb = (q + dq, r + dr)
                    if nb not in cells:
                        border.add(nb)
            for nb in border:
                new_cells = cells | {nb}
                next_keys.add(canonical_key(new_cells))

        by_size[k + 1] = [frozenset(key) for key in next_keys]
        current_keys = next_keys

    return by_size


# ── Cycle detection / glider scan ─────────────────────────────────────────────

def simulate_for_cycle(seed: frozenset, rule: dict):
    """
    Simulate `seed` under `rule` (sparse, infinite plane) for up to MAX_STEPS.

    Cycle detection hashes the translate-normalised set of live cells.  When a
    repeat is found we measure the centre-of-mass displacement between the two
    matching steps to distinguish stationary oscillators from gliders.

    Returns dict with cycle info, or None if the pattern dies / explodes /
    fails to repeat within MAX_STEPS.
    """
    cells = seed
    norm  = translate_normalize(cells)
    c     = centroid(cells)
    history = {norm: (0, c)}

    for t in range(1, MAX_STEPS + 1):
        cells = step_cells(cells, rule)
        n = len(cells)
        if n == 0:
            return None
        if n > MAX_CELLS:
            return None

        norm = translate_normalize(cells)
        c    = centroid(cells)

        if norm in history:
            prev_t, prev_c = history[norm]
            period = t - prev_t
            dq     = c[0] - prev_c[0]
            dr     = c[1] - prev_c[1]
            disp   = math.hypot(dq, dr)
            return {
                "period":           period,
                "final_cells":      cells,
                "final_bit_count":  n,
                "displacement":     disp,
                "velocity_dq":      dq / period,
                "velocity_dr":      dr / period,
                "cycle_first_step": prev_t,
            }
        history[norm] = (t, c)

    return None


# ── Main search loop ──────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # ── 1. Generate all canonical seeds up front ──────────────────────────────
    print(f"Generating canonical polyhexes for n={MIN_SEED_BITS}..{MAX_SEED_BITS} "
          "(dedup: translation + C2 rotation) ...")
    seeds_by_size = generate_canonical_polyhexes(MAX_SEED_BITS)
    seed_counts   = {n: len(seeds_by_size[n]) for n in range(MIN_SEED_BITS, MAX_SEED_BITS + 1)}
    total_per_rule = sum(seed_counts.values())
    print("Canonical seed counts per size:")
    for n in range(MIN_SEED_BITS, MAX_SEED_BITS + 1):
        print(f"  n={n}: {seed_counts[n]:>5d}")
    print(f"Total per rule: {total_per_rule}")
    print(f"Total across {len(RULE_FILES)} rules: {total_per_rule * len(RULE_FILES)}")

    # ── 2. Search each rule × each size × each canonical seed ─────────────────
    total_tested  = 0
    found_glider  = None
    per_rule_counts: dict = {}

    for rule_name in RULE_FILES:
        rule_path = RULES_DIR / rule_name
        rule      = load_rule(rule_path)
        print(f"\n=== {rule_name} ({len(rule)} non-identity mappings) ===")

        rule_tested = 0
        for n in range(MIN_SEED_BITS, MAX_SEED_BITS + 1):
            seeds = seeds_by_size[n]
            print(f"  n={n}: {len(seeds)} canonical seeds ...", end="", flush=True)
            tested_at_size = 0
            t_start = time.time()
            for seed in seeds:
                total_tested += 1
                rule_tested  += 1
                tested_at_size += 1
                cycle = simulate_for_cycle(seed, rule)
                if cycle is None:
                    continue
                if cycle["displacement"] > DISP_EPSILON:
                    # GLIDER!
                    found_glider = {
                        "rule_filename":          rule_name,
                        "seed_bit_count":         n,
                        "seed_coords":            sorted(
                            [int(q), int(r)] for q, r in translate_normalize(seed)
                        ),
                        "glider_period":          int(cycle["period"]),
                        "glider_final_bit_count": int(cycle["final_bit_count"]),
                        "glider_velocity_hex":    [
                            float(cycle["velocity_dq"]),
                            float(cycle["velocity_dr"]),
                        ],
                        "glider_displacement_per_period": float(cycle["displacement"]),
                        "total_seeds_tested":     total_tested,
                    }
                    print(f"\n    *** GLIDER FOUND ***")
                    print(f"    rule={rule_name}  n={n}  period={cycle['period']}")
                    print(f"    velocity (per step) = "
                          f"({cycle['velocity_dq']:.6f}, {cycle['velocity_dr']:.6f})")
                    print(f"    final bit count = {cycle['final_bit_count']}")
                    print(f"    seed coords = {found_glider['seed_coords']}")
                    break
            elapsed = time.time() - t_start
            print(f" done ({tested_at_size} in {elapsed:.1f}s)")
            if found_glider is not None:
                break
        per_rule_counts[rule_name] = rule_tested
        if found_glider is not None:
            break

    elapsed_total = time.time() - t0
    print(f"\nTotal seeds simulated: {total_tested}")
    print(f"Elapsed: {elapsed_total:.1f}s")

    # ── 3. Write result.yaml ──────────────────────────────────────────────────
    if found_glider is None:
        result = {
            "glider_found":            False,
            "rule_filename":           None,
            "seed_bit_count":          None,
            "seed_coords":             None,
            "glider_period":           None,
            "glider_final_bit_count":  None,
            "glider_velocity_hex":     None,
            "total_seeds_tested":      total_tested,
            "seeds_tested_per_rule":   per_rule_counts,
            "seeds_per_size":          seed_counts,
            "rules_tested":            RULE_FILES,
            "elapsed_seconds":         round(elapsed_total, 2),
            "notes": (
                f"Exhaustively tested every canonical connected polyhex of size "
                f"{MIN_SEED_BITS}..{MAX_SEED_BITS} (dedup: translation + C2) under "
                f"all {len(RULE_FILES)} interesting cooling rules from iter_105. "
                "No moving cyclic object (glider) was discovered."
            ),
        }
    else:
        result = {
            "glider_found":           True,
            "rule_filename":          found_glider["rule_filename"],
            "seed_bit_count":         found_glider["seed_bit_count"],
            "seed_coords":            found_glider["seed_coords"],
            "glider_period":          found_glider["glider_period"],
            "glider_final_bit_count": found_glider["glider_final_bit_count"],
            "glider_velocity_hex":    found_glider["glider_velocity_hex"],
            "glider_displacement_per_period":
                                      found_glider["glider_displacement_per_period"],
            "total_seeds_tested":     found_glider["total_seeds_tested"],
            "elapsed_seconds":        round(elapsed_total, 2),
            "notes": (
                "First glider found; search terminated immediately as required. "
                f"Rule={found_glider['rule_filename']}, "
                f"seed_size={found_glider['seed_bit_count']}, "
                f"period={found_glider['glider_period']}."
            ),
        }

    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWrote {RESULT_YAML}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
