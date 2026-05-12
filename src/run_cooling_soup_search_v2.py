#!/usr/bin/env python3
"""
run_cooling_soup_search_v2.py  (iter_105)

Simplified cooling-rules experiment: generate a population of 100 C2-symmetric
rules with a 'HW(A) > HW(B)' bias, evaluate each on a fixed 150x150 soup, and
classify results as DEAD / CHAOTIC / INTERESTING.

Each rule has exactly 8 kernel pairs.  A kernel pair (A, B) contributes two
directed mappings under C2 symmetry:
    A  -> B
    C2(A) -> C2(B)
where HammingWeight(A) > HammingWeight(B) (the cooling constraint).
"""

import json
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT   = Path(__file__).parent.parent
POPULATION_DIR = PROJECT_ROOT / "archive" / "iter_105" / "population"
RESULTS_DIR    = PROJECT_ROOT / "archive" / "iter_105" / "results"
RESULT_YAML    = PROJECT_ROOT / "archive" / "iter_105" / "result.yaml"

GRID_SIZE         = 150
DENSITY           = 0.25
STEPS             = 1000
RANDOM_SEED       = 42
POPULATION_SIZE   = 100
NUM_KERNEL_PAIRS  = 8
DEAD_THRESHOLD    = 20
CHAOTIC_THRESHOLD = 1000

# MSB encoding: center=bit6, E=bit5, SE=bit4, SW=bit3, W=bit2, NW=bit1, NE=bit0


# ── C2-symmetry helpers ────────────────────────────────────────────────────────

def rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1  # E
    b2 = (state >> 4) & 1  # SE
    b3 = (state >> 3) & 1  # SW
    b4 = (state >> 2) & 1  # W
    b5 = (state >> 1) & 1  # NW
    b6 = (state >> 0) & 1  # NE
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


def hamming_weight(state: int) -> int:
    return bin(state).count('1')


# ── Rule generation ────────────────────────────────────────────────────────────

def generate_cooling_rule(rng: random.Random) -> dict:
    """Return a rule dict with exactly NUM_KERNEL_PAIRS cooling kernel pairs.

    A kernel pair (A, B) contributes two directed mappings A->B and C2(A)->C2(B).
    We restrict A to live-cell states (center bit=1) and B to dead-cell states
    (center bit=0) so each mapping actually kills a live cell.  The HW(A)>HW(B)
    cooling constraint is automatically satisfied because center(A)=1 adds 1 to
    HW(A) while center(B)=0 contributes 0.
    """
    live_states = list(range(64, 128))   # center bit = 1
    dead_states = list(range(0, 64))     # center bit = 0

    while True:
        mapped: dict[int, int] = {}
        pairs_found = 0
        attempts = 0

        while pairs_found < NUM_KERNEL_PAIRS and attempts < 50_000:
            attempts += 1
            # Select from live-cell states for source, dead-cell states for target
            a = rng.choice(live_states)
            b = rng.choice(dead_states)

            # Cooling constraint: HW(A) > HW(B)
            if hamming_weight(a) <= hamming_weight(b):
                continue

            c2_a = rotate_c2(a)
            c2_b = rotate_c2(b)

            # C2-symmetric closure: {A->B, C2(A)->C2(B)}
            new_mappings = [(a, b), (c2_a, c2_b)]

            # Conflict check: any source already mapped to a different target?
            conflict = any(
                src in mapped and mapped[src] != dst
                for src, dst in new_mappings
            )
            if conflict:
                continue

            # Skip if this pair adds no new non-identity mapping
            adds_new = any(
                src != dst and src not in mapped
                for src, dst in new_mappings
            )
            if not adds_new:
                continue

            for src, dst in new_mappings:
                mapped[src] = dst

            pairs_found += 1

        if pairs_found == NUM_KERNEL_PAIRS:
            # Only store non-identity entries
            return {str(src): dst for src, dst in mapped.items() if src != dst}

        # Could not fill 8 pairs; retry from scratch


# ── CA simulation ──────────────────────────────────────────────────────────────

def build_lookup(rule_dict: dict) -> np.ndarray:
    """128-element uint8 array: lookup[state] = new center bit."""
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


# ── Main ───────────────────────────────────────────────────────────────────────

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Fixed soup (identical for every rule evaluation)
    np_rng = np.random.default_rng(RANDOM_SEED)
    soup = (np_rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
    print(f"Initial soup: {int(soup.sum())} live cells "
          f"({GRID_SIZE}x{GRID_SIZE}, density={DENSITY}, seed={RANDOM_SEED})")

    # Generate population
    rule_rng = random.Random(12345)
    rule_entries: list[tuple[str, dict]] = []

    print(f"\nGenerating {POPULATION_SIZE} cooling rules ...")
    for i in range(POPULATION_SIZE):
        rule_dict = generate_cooling_rule(rule_rng)
        filename  = f"rule_{i+1:03d}.json"
        with open(POPULATION_DIR / filename, "w") as f:
            json.dump(rule_dict, f, sort_keys=True, indent=2)
        rule_entries.append((filename, rule_dict))
        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{POPULATION_SIZE} rules generated")

    # Evaluate population
    print(f"\nEvaluating {POPULATION_SIZE} rules ({STEPS} steps each) ...")
    counts: dict[str, int] = {"DEAD": 0, "CHAOTIC": 0, "INTERESTING": 0}
    interesting_files: list[str] = []

    for filename, rule_dict in rule_entries:
        lookup = build_lookup(rule_dict)
        grid   = soup.copy()

        for _ in range(STEPS):
            grid = step_grid(grid, lookup)

        final_count = int(grid.sum())
        cat         = classify(final_count)
        counts[cat] += 1

        if cat == "INTERESTING":
            interesting_files.append(filename)

        marker = " <-- INTERESTING" if cat == "INTERESTING" else ""
        print(f"  {filename}: final_count={final_count:6d}  [{cat}]{marker}")

    # Write result.yaml
    yaml_result = {
        "dead_rules_count":        counts["DEAD"],
        "chaotic_rules_count":     counts["CHAOTIC"],
        "interesting_rules_count": counts["INTERESTING"],
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)

    # Write interesting_rules.txt
    interesting_txt = RESULTS_DIR / "interesting_rules.txt"
    with open(interesting_txt, "w") as f:
        if interesting_files:
            f.write("\n".join(interesting_files) + "\n")

    print("\n=== Summary ===")
    print(f"  DEAD        (< {DEAD_THRESHOLD}):    {counts['DEAD']}")
    print(f"  CHAOTIC     (> {CHAOTIC_THRESHOLD}): {counts['CHAOTIC']}")
    print(f"  INTERESTING ({DEAD_THRESHOLD}–{CHAOTIC_THRESHOLD}): {counts['INTERESTING']}")
    print(f"\n  result.yaml:          {RESULT_YAML}")
    print(f"  interesting_rules.txt: {interesting_txt}")

    return 0 if counts["INTERESTING"] >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
