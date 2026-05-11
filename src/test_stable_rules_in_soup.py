#!/usr/bin/env python3
"""
test_stable_rules_in_soup.py  (iter_098)

Hypothesis: soup-stability – a rule known to produce only still-lifes / decay
from small seeds will resolve a chaotic soup into a low-density state of
persistent objects.

Steps
-----
1. Load the iter_095 multi-seed CSV to get the list of 100 C2-symmetric rules.
2. Re-evaluate each rule across the full 21-seed suite, tracking every per-seed
   outcome.  A rule is "stably boring" if EVERY seed produces only 'decayed'
   or 'still_life' (oscillators, explosions, and no-cycle outcomes exclude it).
3. Run each stably-boring candidate on a 150×150 toroidal soup for 1000 steps
   (numpy grid, seed=42, 25% density – same as iter_097).
4. Classify DEAD / INTERESTING / CHAOTIC and write result.yaml +
   interesting_rules.txt.
"""

import csv
import json
import math
import sys
from itertools import combinations
from pathlib import Path

import numpy as np
import yaml

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
POP_DIR      = PROJECT_ROOT / "archive" / "iter_095" / "population"
SCORES_CSV   = PROJECT_ROOT / "archive" / "iter_095" / "results" / "c2_random_multiseed_scores.csv"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_098" / "results"
RESULT_YAML  = PROJECT_ROOT / "archive" / "iter_098" / "result.yaml"

# ── Parameters ────────────────────────────────────────────────────────────────
SEED_EVAL_STEPS = 500
MAX_CELLS       = 3000

GRID_SIZE         = 150
SOUP_DENSITY      = 0.25
SOUP_RANDOM_SEED  = 42
SOUP_STEPS        = 1000
DEAD_THRESHOLD    = 20
CHAOTIC_THRESHOLD = 1000

HEX_DIRS = [
    ( 1,  0),   # E
    ( 1, -1),   # SE
    ( 0, -1),   # SW
    (-1,  0),   # W
    (-1,  1),   # NW
    ( 0,  1),   # NE
]

# ── Standard 21-seed suite (from iter_095 / run_c2_motion_evolution_gen1.py) ──

def _apply_rotation(q, r, t):
    if t == 0: return ( q,       r      )
    if t == 1: return (-r,       q + r  )
    if t == 2: return (-(q + r), q      )
    if t == 3: return (-q,      -r      )
    if t == 4: return ( r,      -(q + r))
    if t == 5: return ( q + r,  -q      )
    raise ValueError(t)


def _translate_norm(cells) -> frozenset:
    sc = sorted(cells)
    q0, r0 = sc[0]
    return frozenset((q - q0, r - r0) for q, r in sc)


def _rotation_norm(cells) -> frozenset:
    best = None
    for t in range(6):
        norm = _translate_norm([_apply_rotation(q, r, t) for q, r in cells])
        if best is None or sorted(norm) < sorted(best):
            best = norm
    return best


def _is_connected(cells) -> bool:
    cs = set(cells)
    start = next(iter(cs))
    visited = {start}
    stack = [start]
    while stack:
        q, r = stack.pop()
        for dq, dr in HEX_DIRS:
            nb = (q + dq, r + dr)
            if nb in cs and nb not in visited:
                visited.add(nb)
                stack.append(nb)
    return len(visited) == len(cs)


def _build_trihex_seeds():
    coord_range = range(-3, 4)
    all_cells = [(q, r) for q in coord_range for r in coord_range]
    seen: set = set()
    seeds = []
    for combo in combinations(all_cells, 3):
        if not _is_connected(combo):
            continue
        cf = _translate_norm(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(cf)
    return seeds


def _build_tetrahex_seeds():
    coord_range = range(-4, 5)
    all_cells = [(q, r) for q in coord_range for r in coord_range]
    seen: set = set()
    seeds = []
    for combo in combinations(all_cells, 4):
        if not _is_connected(combo):
            continue
        cf = _rotation_norm(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(_translate_norm(combo))
    return seeds


def build_seed_suite() -> dict:
    trihexes   = _build_trihex_seeds()
    tetrahexes = _build_tetrahex_seeds()
    suite = {}
    for i, s in enumerate(trihexes,   1): suite[f"3bit_{i:02d}"] = s
    for i, s in enumerate(tetrahexes, 1): suite[f"4bit_{i:02d}"] = s
    return suite


ALL_SEEDS: dict = build_seed_suite()

# ── Sparse hex CA (for small-seed evaluation) ─────────────────────────────────

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
    if n == 0:
        return (0.0, 0.0)
    return (sum(q for q, _ in cells) / n, sum(r for _, r in cells) / n)


def evaluate_seed(rule: dict, seed: frozenset) -> str:
    """Return the outcome kind for this seed: decayed, still_life, oscillator, exploded, glider, no_cycle."""
    current    = seed
    init_shape = _translate_normalize(current)
    init_com   = _center_of_mass(current)
    history: dict = {init_shape: (0, init_com)}

    for t in range(SEED_EVAL_STEPS):
        current = step_cells(current, rule)

        if len(current) == 0:
            return "decayed"

        if len(current) > MAX_CELLS:
            return "exploded"

        shape = _translate_normalize(current)
        com   = _center_of_mass(current)

        if shape in history:
            prev_t, prev_com = history[shape]
            period       = (t + 1) - prev_t
            dq           = com[0] - prev_com[0]
            dr           = com[1] - prev_com[1]
            displacement = math.sqrt(dq * dq + dr * dr)
            if displacement > 1e-9:
                return "glider"
            if period == 1:
                return "still_life"
            return "oscillator"

        history[shape] = (t + 1, com)

    return "no_cycle"


STABLE_KINDS = {"decayed", "still_life"}


def is_stably_boring(rule: dict) -> tuple[bool, dict]:
    """Return (stably_boring, per_seed_outcomes)."""
    outcomes = {}
    for seed_name, seed_cells in ALL_SEEDS.items():
        kind = evaluate_seed(rule, seed_cells)
        outcomes[seed_name] = kind
    all_stable = all(k in STABLE_KINDS for k in outcomes.values())
    return all_stable, outcomes

# ── Dense numpy grid (for soup evaluation) ────────────────────────────────────

def build_lookup(rule_dict: dict) -> np.ndarray:
    lookup_output = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lookup_output[int(k)] = int(v)
    return ((lookup_output >> 6) & 1).astype(np.uint8)


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


def classify(count: int) -> str:
    if count < DEAD_THRESHOLD:
        return "DEAD"
    if count > CHAOTIC_THRESHOLD:
        return "CHAOTIC"
    return "INTERESTING"


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load rule IDs from iter_095 CSV ───────────────────────────────
    print(f"Loading iter_095 scores from: {SCORES_CSV}")
    rule_ids = []
    with open(SCORES_CSV, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule_ids.append(row["rule_id"])
    print(f"  Loaded {len(rule_ids)} rule IDs from CSV\n")

    # ── Step 2: Per-seed evaluation to find stably-boring candidates ──────────
    n_tri = sum(1 for k in ALL_SEEDS if k.startswith("3bit"))
    n_tet = sum(1 for k in ALL_SEEDS if k.startswith("4bit"))
    print(f"Seed suite: {len(ALL_SEEDS)} seeds ({n_tri} trihexes + {n_tet} tetrahexes)")
    print(f"Evaluating {len(rule_ids)} rules for stability (only still_life / decayed allowed)...\n")

    candidates = []
    for rule_id in rule_ids:
        rule_path = POP_DIR / rule_id
        with open(rule_path) as f:
            rule_dict = {int(k): v for k, v in json.load(f).items()}

        boring, outcomes = is_stably_boring(rule_dict)
        outcome_summary  = ", ".join(f"{n}={k}" for n, k in sorted(outcomes.items()))
        marker = "  [CANDIDATE]" if boring else ""
        # Count non-stable seeds for diagnostics
        non_stable = [k for k in outcomes.values() if k not in STABLE_KINDS]
        print(f"  {rule_id}: {len(non_stable)} non-stable seeds{marker}")
        if boring:
            candidates.append({"rule_id": rule_id, "rule_dict": rule_dict})

    print(f"\n==> Found {len(candidates)} stably-boring candidates\n")

    if not candidates:
        print("No candidates found — writing zero-count result.yaml and exiting.")
        yaml_result = {
            "candidates_found":       0,
            "dead_rules_count":       0,
            "chaotic_rules_count":    0,
            "interesting_rules_count": 0,
        }
        with open(RESULT_YAML, "w") as f:
            yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)
        interesting_txt = RESULTS_DIR / "interesting_rules.txt"
        interesting_txt.write_text("")
        return 1

    # ── Step 3: Soup evaluation ───────────────────────────────────────────────
    rng  = np.random.default_rng(SOUP_RANDOM_SEED)
    soup = (rng.random((GRID_SIZE, GRID_SIZE)) < SOUP_DENSITY).astype(np.uint8)
    initial_count = int(soup.sum())
    print(f"Initial soup: {initial_count} live cells "
          f"({GRID_SIZE}x{GRID_SIZE} grid, {SOUP_DENSITY*100:.0f}% density, seed={SOUP_RANDOM_SEED})")
    print(f"Simulating {SOUP_STEPS} steps per candidate ...\n")

    counts = {"DEAD": 0, "CHAOTIC": 0, "INTERESTING": 0}
    interesting_files: list[str] = []

    for entry in candidates:
        rule_id   = entry["rule_id"]
        rule_dict = {str(k): v for k, v in entry["rule_dict"].items()}

        lookup = build_lookup(rule_dict)
        grid   = soup.copy()

        for _ in range(SOUP_STEPS):
            grid = step_grid(grid, lookup)

        final_count = int(grid.sum())
        cat         = classify(final_count)
        counts[cat] += 1

        if cat == "INTERESTING":
            interesting_files.append(rule_id)

        marker = "  <-- INTERESTING" if cat == "INTERESTING" else ""
        print(f"  {rule_id}: final_count={final_count:6d}  [{cat}]{marker}")

    # ── Step 4: Write results ─────────────────────────────────────────────────
    interesting_txt = RESULTS_DIR / "interesting_rules.txt"
    with open(interesting_txt, "w") as f:
        if interesting_files:
            f.write("\n".join(interesting_files) + "\n")

    yaml_result = {
        "candidates_found":        len(candidates),
        "dead_rules_count":        counts["DEAD"],
        "chaotic_rules_count":     counts["CHAOTIC"],
        "interesting_rules_count": counts["INTERESTING"],
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)

    print("\n=== Summary ===")
    print(f"  Candidates (stably boring):  {len(candidates)}")
    print(f"  Total rules evaluated:       {len(rule_ids)}")
    print(f"  DEAD        (< {DEAD_THRESHOLD}):    {counts['DEAD']}")
    print(f"  CHAOTIC     (> {CHAOTIC_THRESHOLD}): {counts['CHAOTIC']}")
    print(f"  INTERESTING ({DEAD_THRESHOLD}–{CHAOTIC_THRESHOLD}): {counts['INTERESTING']}")
    print(f"\n  Saved YAML: {RESULT_YAML}")
    print(f"  Saved list: {interesting_txt}")

    return 0 if counts["INTERESTING"] >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
