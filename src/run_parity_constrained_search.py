#!/usr/bin/env python3
"""
run_parity_constrained_search.py

Generates and evaluates a population of C2-symmetric rules that satisfy a
bit-count parity-conservation constraint: each kernel pair (A, B) must have
HammingWeight(A) % 2 == HammingWeight(B) % 2.

Uses the medium-density configuration (8 kernel pairs) from iter_129, evaluated
on the ash pattern with the quadratic fitness penalty from iter_136:
  fitness = displacement / (1 + (bit_ratio - 1)^2)
"""

import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT     = Path(__file__).parent.parent
ASH_PATTERN_PATH = Path(__file__).parent / "ash_pattern.json"
ITER_DIR         = PROJECT_ROOT / "archive" / "iter_138"
POPULATION_DIR   = ITER_DIR / "population"
RESULTS_DIR      = ITER_DIR / "results"
SUMMARY_YAML     = RESULTS_DIR / "summary.yaml"

POPULATION_SIZE          = 100
STEPS                    = 200
LATE_START               = 100
INITIAL_BITS             = 325
N_PAIRS                  = 8        # medium-density from iter_129
SEED_BASE                = 4000     # distinct from iter_129/136/137 seed ranges
MAX_ATTEMPTS             = 50000
MAX_PAIR_TRIES           = 2000

VIABLE_FITNESS_THRESHOLD = 0.01
VIABLE_BIT_RATIO_MAX     = 3.0


# ── C2-symmetric rule helpers ─────────────────────────────────────────────────

def rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


def is_valid_c2_pair(a: int, b: int) -> bool:
    if a == b or a == 0 or b == 0:
        return False
    ra = rotate_c2(a)
    rb = rotate_c2(b)
    return len({a, b, ra, rb}) == 4


def is_parity_conserving_pair(a: int, b: int) -> bool:
    """True iff HammingWeight(A) % 2 == HammingWeight(B) % 2."""
    return bin(a).count('1') % 2 == bin(b).count('1') % 2


def is_nonconserving(pairs: list) -> bool:
    return any(bin(a).count('1') != bin(b).count('1') for a, b in pairs)


def try_build_c2_rule(pairs: list) -> dict | None:
    rule: dict = {}
    for a, b in pairs:
        ra = rotate_c2(a)
        rb = rotate_c2(b)
        for src, dst in [(a, b), (b, a), (ra, rb), (rb, ra)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule


def generate_parity_constrained_c2_rule(seed: int) -> dict:
    """Generate a C2-symmetric rule with N_PAIRS pairs, each satisfying parity conservation."""
    rng = random.Random(seed)
    for _ in range(MAX_ATTEMPTS):
        pairs: list      = []
        used_states: set = set()
        ok = True
        for _ in range(N_PAIRS):
            found = False
            for _ in range(MAX_PAIR_TRIES):
                a = rng.randint(1, 127)
                b = rng.randint(1, 127)
                if not is_valid_c2_pair(a, b):
                    continue
                if not is_parity_conserving_pair(a, b):
                    continue
                ra = rotate_c2(a)
                rb = rotate_c2(b)
                states = {a, b, ra, rb}
                if states & used_states:
                    continue
                pairs.append((a, b))
                used_states.update(states)
                found = True
                break
            if not found:
                ok = False
                break
        if not ok:
            continue
        if not is_nonconserving(pairs):
            continue
        rule = try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(
        f"Failed to generate parity-constrained C2 rule after {MAX_ATTEMPTS} attempts "
        f"(seed={seed})"
    )


# ── Grid simulation ───────────────────────────────────────────────────────────

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


def center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def evaluate_rule(rule_dict: dict, ash_grid: np.ndarray) -> dict:
    lut  = rule_to_lut(rule_dict)
    grid = ash_grid.copy()

    for _ in range(LATE_START):
        grid = step_grid(grid, lut)

    com_100 = center_of_mass(grid)

    for _ in range(STEPS - LATE_START):
        grid = step_grid(grid, lut)

    com_200    = center_of_mass(grid)
    final_bits = int(grid.sum())

    dq           = com_200[0] - com_100[0]
    dr           = com_200[1] - com_100[1]
    displacement = math.sqrt(dq * dq + dr * dr)
    bit_ratio    = final_bits / INITIAL_BITS
    fitness      = displacement / (1.0 + (bit_ratio - 1.0) ** 2)

    return {
        "displacement": displacement,
        "final_bits":   final_bits,
        "bit_ratio":    bit_ratio,
        "fitness":      fitness,
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    POPULATION_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading ash pattern ...", flush=True)
    with open(ASH_PATTERN_PATH) as f:
        ash_data = json.load(f)
    grid_size = ash_data["grid_size"]
    ash_grid  = np.zeros((grid_size, grid_size), dtype=np.uint8)
    for q, r in ash_data["cells"]:
        ash_grid[q, r] = 1
    print(f"  {int(ash_grid.sum())} bits on {grid_size}x{grid_size} grid", flush=True)

    print(
        f"\nGenerating and evaluating {POPULATION_SIZE} parity-constrained C2 rules "
        f"(n_pairs={N_PAIRS}, 32 non-identity mappings) ...",
        flush=True,
    )

    results = []
    for i in range(POPULATION_SIZE):
        seed    = SEED_BASE + i
        rule_id = f"rule_{i:03d}"
        try:
            rule_dict = generate_parity_constrained_c2_rule(seed)
        except RuntimeError as e:
            print(f"  {rule_id}: GENERATION FAILED — {e}", flush=True)
            continue

        rule_path = POPULATION_DIR / f"{rule_id}.json"
        with open(rule_path, "w") as f:
            json.dump({str(k): v for k, v in rule_dict.items()}, f)

        res       = evaluate_rule(rule_dict, ash_grid)
        is_viable = (
            res["fitness"] > VIABLE_FITNESS_THRESHOLD
            and res["bit_ratio"] < VIABLE_BIT_RATIO_MAX
        )

        results.append({
            "rule_id":      rule_id,
            "fitness":      res["fitness"],
            "displacement": res["displacement"],
            "final_bits":   res["final_bits"],
            "bit_ratio":    res["bit_ratio"],
            "viable":       is_viable,
        })

        if (i + 1) % 10 == 0 or is_viable:
            tag = "  *** VIABLE ***" if is_viable else ""
            print(
                f"  {rule_id}  fitness={res['fitness']:.6f}  "
                f"disp={res['displacement']:.4f}  "
                f"bit_ratio={res['bit_ratio']:.3f}{tag}",
                flush=True,
            )

    if not results:
        print("ERROR: No rules were generated or evaluated.", flush=True)
        return 1

    viable_founders = [r for r in results if r["viable"]]
    best            = max(results, key=lambda r: r["fitness"])

    summary = {
        "viable_founder_count":  len(viable_founders),
        "top_fitness_score":     round(best["fitness"], 8),
        "top_fitness_bit_ratio": round(best["bit_ratio"], 4),
        "top_fitness_rule_id":   f"{best['rule_id']}.json",
    }

    with open(SUMMARY_YAML, "w") as f:
        yaml.dump(summary, f, default_flow_style=False, sort_keys=False)
    print(f"\nSaved summary: {SUMMARY_YAML}", flush=True)

    print("\n=== Final Summary ===", flush=True)
    print(f"  viable_founder_count : {summary['viable_founder_count']}", flush=True)
    print(f"  top_fitness_score    : {summary['top_fitness_score']:.8f}", flush=True)
    print(f"  top_fitness_bit_ratio: {summary['top_fitness_bit_ratio']:.4f}", flush=True)
    print(f"  top_fitness_rule_id  : {summary['top_fitness_rule_id']}", flush=True)

    if viable_founders:
        print("\n  Viable founders:", flush=True)
        for r in sorted(viable_founders, key=lambda x: x["fitness"], reverse=True):
            print(
                f"    {r['rule_id']}  fitness={r['fitness']:.6f}  "
                f"bit_ratio={r['bit_ratio']:.3f}",
                flush=True,
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
