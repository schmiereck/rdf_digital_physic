#!/usr/bin/env python3
"""
run_targeted_soup_search.py  (iter_099)

Generates 100 "targeted sparse" C2-symmetric rules where every active kernel
pair is drawn exclusively from the high-density neighborhood pool (Hamming
weight >= 4).  Each rule uses exactly 4 input pairs that expand via C2-closure
to 8 bidirectional kernel swaps / 16 directed rule entries.

Each rule is then evaluated on a 150x150 soup (25% density, seed=42, 1000
steps) and classified:
  DEAD        -- final_bit_count < 20
  CHAOTIC     -- final_bit_count > 1000
  INTERESTING -- 20 <= final_bit_count <= 1000
"""

import json
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
POP_DIR      = PROJECT_ROOT / "archive" / "iter_099" / "population"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_099" / "results"
RESULT_YAML  = PROJECT_ROOT / "archive" / "iter_099" / "result.yaml"

POPULATION_SIZE   = 100
GRID_SIZE         = 150
DENSITY           = 0.25
STEPS             = 1000
RANDOM_SEED       = 42
DEAD_THRESHOLD    = 20
CHAOTIC_THRESHOLD = 1000

# 4 input pairs → 8 bidirectional kernel swaps → 16 directed rule entries
N_INPUT_PAIRS = 4
MAX_GEN_ATTEMPTS = 5000


# ── High-density state pool (Hamming weight 4-7, 64 states) ───────────────────

HIGH_DENSITY_POOL: list[int] = [
    s for s in range(1, 128) if bin(s).count("1") >= 4
]


# ── C2 rotation (MSB encoding: center=bit6, E=5, SE=4, SW=3, W=2, NW=1, NE=0) ─

def rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1  # E
    b2 = (state >> 4) & 1  # SE
    b3 = (state >> 3) & 1  # SW
    b4 = (state >> 2) & 1  # W
    b5 = (state >> 1) & 1  # NW
    b6 = (state >> 0) & 1  # NE
    return c * 64 + b6 * 32 + b1 * 16 + b2 * 8 + b3 * 4 + b4 * 2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


# ── Targeted rule generation ──────────────────────────────────────────────────

def generate_targeted_c2_rule(rng: random.Random) -> dict | None:
    """
    Generate one C2-symmetric rule using exactly N_INPUT_PAIRS (A, B) pairs
    drawn from HIGH_DENSITY_POOL.

    Each pair (A, B) expands via C2-closure to 4 directed entries:
        A → B,  B → A,  rotate_c2(A) → rotate_c2(B),  rotate_c2(B) → rotate_c2(A)

    N_INPUT_PAIRS=4 yields 8 bidirectional kernel swaps / 16 directed entries.

    Rotation preserves Hamming weight, so all rotated states remain in the
    high-density pool automatically.
    """
    pool = HIGH_DENSITY_POOL

    for _ in range(MAX_GEN_ATTEMPTS):
        used: set[int] = set()
        rule: dict[int, int] = {}
        pairs_found = 0

        for _ in range(N_INPUT_PAIRS):
            found = False
            for _ in range(800):
                a = rng.choice(pool)
                b = rng.choice(pool)
                if a == b or a in used or b in used:
                    continue
                ra = rotate_c2(a)
                rb = rotate_c2(b)
                if ra in used or rb in used:
                    continue
                if len({a, b, ra, rb}) != 4:
                    continue
                # Conflict-free: since used tracks all committed states, no
                # two pairs share any state, so there can be no rule conflict.
                rule[a]  = b;  rule[b]  = a
                rule[ra] = rb; rule[rb] = ra
                used.update({a, b, ra, rb})
                pairs_found += 1
                found = True
                break
            if not found:
                break

        if pairs_found == N_INPUT_PAIRS:
            return rule

    return None


# ── Grid simulation (toroidal hex, vectorised numpy) ──────────────────────────

def build_lookup(rule_dict: dict) -> np.ndarray:
    """128-element uint8 array: lookup[state] = new center bit."""
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
        | ne.astype(np.uint16)
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
    POP_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"High-density pool: {len(HIGH_DENSITY_POOL)} states (Hamming weight >= 4)")
    print(f"Rule design: {N_INPUT_PAIRS} input pairs"
          f" -> {N_INPUT_PAIRS * 2} bidirectional kernel swaps"
          f" -> {N_INPUT_PAIRS * 4} directed rule entries")
    print(f"Generating {POPULATION_SIZE} targeted C2-symmetric rules ...\n")

    rng = random.Random(99)
    rules = []
    gen_failures = 0

    for i in range(1, POPULATION_SIZE + 1):
        rule_dict = generate_targeted_c2_rule(rng)
        if rule_dict is None:
            print(f"  WARNING: failed to generate rule {i}", file=sys.stderr)
            gen_failures += 1
            continue
        rule_id  = f"rule_{i:03d}"
        out_path = POP_DIR / f"{rule_id}.json"
        with open(out_path, "w") as f:
            json.dump({str(k): v for k, v in rule_dict.items()}, f,
                      sort_keys=True, indent=2)
        rules.append({"rule_id": rule_id, "rule_dict": rule_dict, "path": out_path})
        if i % 20 == 0:
            print(f"  Generated {i}/{POPULATION_SIZE} ...")

    n_generated = len(rules)
    print(f"\nGenerated {n_generated} rules "
          f"({gen_failures} generation failures).")

    # Fixed initial soup — same seed used in iter_097 and iter_098
    rng_np = np.random.default_rng(RANDOM_SEED)
    soup   = (rng_np.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
    print(f"\nInitial soup: {int(soup.sum())} live cells "
          f"({GRID_SIZE}x{GRID_SIZE}, {DENSITY*100:.0f}% density, "
          f"seed={RANDOM_SEED})")
    print(f"Simulating {STEPS} steps per rule ...\n")

    counts: dict[str, int] = {"DEAD": 0, "CHAOTIC": 0, "INTERESTING": 0}
    interesting_files: list[str] = []

    for idx, entry in enumerate(rules, 1):
        lookup = build_lookup(entry["rule_dict"])
        grid   = soup.copy()

        for _ in range(STEPS):
            grid = step_grid(grid, lookup)

        final_count = int(grid.sum())
        cat         = classify(final_count)
        counts[cat] += 1

        if cat == "INTERESTING":
            interesting_files.append(entry["path"].name)

        marker = "  <-- INTERESTING" if cat == "INTERESTING" else ""
        print(f"  {entry['rule_id']}: final_count={final_count:6d}  [{cat}]{marker}")

        if idx % 20 == 0:
            print(f"  --- {idx}/{n_generated} rules done ---")

    # ── Write results ──────────────────────────────────────────────────────────
    interesting_txt = RESULTS_DIR / "interesting_rules.txt"
    with open(interesting_txt, "w") as f:
        if interesting_files:
            f.write("\n".join(interesting_files) + "\n")

    yaml_result = {
        "dead_rules_count":        counts["DEAD"],
        "chaotic_rules_count":     counts["CHAOTIC"],
        "interesting_rules_count": counts["INTERESTING"],
    }
    with open(RESULT_YAML, "w") as f:
        yaml.dump(yaml_result, f, default_flow_style=False, sort_keys=False)

    print("\n=== Summary ===")
    print(f"  Total rules evaluated:  {n_generated}")
    print(f"  DEAD        (< {DEAD_THRESHOLD}):    {counts['DEAD']}")
    print(f"  CHAOTIC     (> {CHAOTIC_THRESHOLD}): {counts['CHAOTIC']}")
    print(f"  INTERESTING ({DEAD_THRESHOLD}-{CHAOTIC_THRESHOLD}): {counts['INTERESTING']}")
    print(f"\n  Saved population: {POP_DIR}")
    print(f"  Saved YAML:       {RESULT_YAML}")
    print(f"  Saved list:       {interesting_txt}")

    return 0 if counts["INTERESTING"] >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
