#!/usr/bin/env python3
"""
filter_soup_rules.py

Evaluates dense C2-symmetric hex CA rules from iter_096 by running each on a
150x150 toroidal hex grid initialised with 25% random noise ("soup").

After 1000 steps the final live-cell count is recorded and each rule is
classified:
  DEAD        -- final_bit_count < 20
  CHAOTIC     -- final_bit_count > 1000
  INTERESTING -- 20 <= final_bit_count <= 1000
"""

import json
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
POP_DIR      = PROJECT_ROOT / "archive" / "iter_096" / "population"
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_097" / "results"
RESULT_YAML  = PROJECT_ROOT / "archive" / "iter_097" / "result.yaml"

GRID_SIZE          = 150
DENSITY            = 0.25
STEPS              = 1000
RANDOM_SEED        = 42
DEAD_THRESHOLD     = 20
CHAOTIC_THRESHOLD  = 1000

# MSB encoding: center=bit6, E=bit5, SE=bit4, SW=bit3, W=bit2, NW=bit1, NE=bit0


def build_lookup(rule_dict: dict) -> np.ndarray:
    """Return a 128-element uint8 array: lookup[state] = new center bit."""
    # Default: identity (unmapped states map to themselves)
    identity = np.arange(128, dtype=np.uint8)
    lookup_output = identity.copy()
    for k, v in rule_dict.items():
        lookup_output[int(k)] = int(v)
    return ((lookup_output >> 6) & 1).astype(np.uint8)


def step_grid(grid: np.ndarray, lookup: np.ndarray) -> np.ndarray:
    """Single CA step on a toroidal hex grid using axial coordinates."""
    e  = np.roll(grid, -1, axis=0)         # E:  (q+1, r)
    w  = np.roll(grid, 1,  axis=0)         # W:  (q-1, r)
    ne = np.roll(grid, -1, axis=1)         # NE: (q,   r+1)
    sw = np.roll(grid, 1,  axis=1)         # SW: (q,   r-1)
    se = np.roll(e, 1,  axis=1)            # SE: (q+1, r-1)
    nw = np.roll(w, -1, axis=1)            # NW: (q-1, r+1)

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


def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    rule_paths = sorted(POP_DIR.glob("*.json"))
    if not rule_paths:
        print(f"ERROR: No rules found in {POP_DIR}", file=sys.stderr)
        return 1
    print(f"Found {len(rule_paths)} rules in {POP_DIR}")

    # Fixed initial soup (same for every rule)
    rng  = np.random.default_rng(RANDOM_SEED)
    soup = (rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
    print(f"Initial soup: {int(soup.sum())} live cells "
          f"({GRID_SIZE}x{GRID_SIZE} grid, {DENSITY*100:.0f}% density, seed={RANDOM_SEED})")
    print(f"Simulating {STEPS} steps per rule ...\n")

    counts = {"DEAD": 0, "CHAOTIC": 0, "INTERESTING": 0}
    interesting_files: list[str] = []

    for i, path in enumerate(rule_paths, 1):
        with open(path) as f:
            rule_dict = json.load(f)

        lookup = build_lookup(rule_dict)
        grid   = soup.copy()

        for _ in range(STEPS):
            grid = step_grid(grid, lookup)

        final_count = int(grid.sum())
        cat         = classify(final_count)
        counts[cat] += 1

        if cat == "INTERESTING":
            interesting_files.append(path.name)

        marker = " <-- INTERESTING" if cat == "INTERESTING" else ""
        print(f"  {path.name}: final_count={final_count:6d}  [{cat}]{marker}")

        if i % 100 == 0:
            print(f"  --- {i}/{len(rule_paths)} rules done ---")

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
    print(f"  Total rules evaluated:  {len(rule_paths)}")
    print(f"  DEAD        (< {DEAD_THRESHOLD}):    {counts['DEAD']}")
    print(f"  CHAOTIC     (> {CHAOTIC_THRESHOLD}): {counts['CHAOTIC']}")
    print(f"  INTERESTING ({DEAD_THRESHOLD}–{CHAOTIC_THRESHOLD}): {counts['INTERESTING']}")
    print(f"\n  Saved YAML: {RESULT_YAML}")
    print(f"  Saved list: {interesting_txt}")

    return 0 if counts["INTERESTING"] >= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
