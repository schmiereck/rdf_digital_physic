#!/usr/bin/env python3
"""
measure_baseline.py

Establishes a performance baseline for the velocity-stability fitness metric
by evaluating 100 random C2-symmetric rules on a standard 'soup' initial condition.

Methodology:
  - 100 C2-symmetric rules, each with 8 kernel pairs (medium density)
  - Fixed random seed for reproducibility
  - 150x150 toroidal hex grid, 25% random noise soup (seed=42)
  - 4 windows x 400 steps = 1600 total steps per rule
  - Annihilation check: if total displacement across all windows is zero,
    assign fitness 0.0 (prevents rewarding rules that erase everything)
"""

import csv
import random
import sys
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parent))
from fitness import calculate_velocity_stability

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_150" / "results"
RESULT_CSV   = RESULTS_DIR / "fitness_scores.csv"

POPULATION_SIZE  = 100
GRID_SIZE        = 150
SOUP_DENSITY     = 0.25
SOUP_SEED        = 42
RULE_SEED        = 150
KERNEL_PAIRS     = 8
STEPS_PER_WINDOW = 400
NUM_WINDOWS      = 4   # 4 * 400 = 1600 total steps
MAX_ATTEMPTS     = 50000


# ── C2-symmetric rule helpers (MSB encoding: bit6=center, bits5-0=E,SE,SW,W,NW,NE) ──

def _rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1  # E
    b2 = (state >> 4) & 1  # SE
    b3 = (state >> 3) & 1  # SW
    b4 = (state >> 2) & 1  # W
    b5 = (state >> 1) & 1  # NW
    b6 = (state >> 0) & 1  # NE
    return c*64 + b6*32 + b1*16 + b2*8 + b3*4 + b4*2 + b5


def _rotate_c2(state: int) -> int:
    return _rotate60_msb(_rotate60_msb(_rotate60_msb(state)))


def _is_valid_c2_pair(a: int, b: int) -> bool:
    if a == b or a == 0 or b == 0:
        return False
    ra = _rotate_c2(a)
    rb = _rotate_c2(b)
    return len({a, b, ra, rb}) == 4


def _try_build_c2_rule(pairs: list) -> dict | None:
    rule: dict = {}
    for a, b in pairs:
        ra = _rotate_c2(a)
        rb = _rotate_c2(b)
        for src, dst in [(a, b), (b, a), (ra, rb), (rb, ra)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule


def generate_random_c2_rule(rng: random.Random, n_pairs: int = KERNEL_PAIRS) -> dict:
    for _ in range(MAX_ATTEMPTS):
        pairs = []
        ok = True
        for _ in range(n_pairs):
            found = False
            for _attempt in range(300):
                a = rng.randint(1, 127)
                b = rng.randint(1, 127)
                if _is_valid_c2_pair(a, b):
                    pairs.append((a, b))
                    found = True
                    break
            if not found:
                ok = False
                break
        if not ok:
            continue
        rule = _try_build_c2_rule(pairs)
        if rule is not None:
            return rule
    raise RuntimeError(f"Failed to generate valid C2 rule with {n_pairs} pairs")


# ── Soup initial condition ────────────────────────────────────────────────────

def make_soup() -> np.ndarray:
    rng = np.random.default_rng(SOUP_SEED)
    return (rng.random((GRID_SIZE, GRID_SIZE)) < SOUP_DENSITY).astype(np.uint8)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    soup = make_soup()
    live = int(soup.sum())
    total_steps = NUM_WINDOWS * STEPS_PER_WINDOW
    print(f"Initial soup: {live} live cells "
          f"({GRID_SIZE}x{GRID_SIZE}, density={SOUP_DENSITY:.0%}, seed={SOUP_SEED})")
    print(f"Simulation:   {NUM_WINDOWS} windows x {STEPS_PER_WINDOW} steps = {total_steps} total steps")
    print(f"Population:   {POPULATION_SIZE} C2-symmetric rules, {KERNEL_PAIRS} kernel pairs each")
    print(f"Rule seed:    {RULE_SEED}\n")

    rng = random.Random(RULE_SEED)
    rows = []
    annihilation_count = 0

    for i in range(1, POPULATION_SIZE + 1):
        rule_dict = generate_random_c2_rule(rng)

        fitness, velocities, std_dev = calculate_velocity_stability(
            rule_dict,
            soup,
            steps_per_window=STEPS_PER_WINDOW,
            num_windows=NUM_WINDOWS,
        )

        total_displacement = sum(velocities)
        if total_displacement < 1e-9:
            fitness = 0.0
            annihilation_count += 1
            tag = " [ANNIHILATION]"
        else:
            tag = ""

        print(f"  rule_{i:03d}: fitness={fitness:.6f}  "
              f"vel={[round(v, 3) for v in velocities]}  "
              f"std={std_dev:.4f}{tag}", flush=True)

        rows.append({
            "rule_id":            f"rule_{i:03d}",
            "fitness":            round(fitness, 8),
            "std_dev":            round(std_dev, 8),
            "total_displacement": round(total_displacement, 6),
            "velocities":         ";".join(f"{v:.4f}" for v in velocities),
            "annihilated":        1 if total_displacement < 1e-9 else 0,
        })

    # ── Save CSV ─────────────────────────────────────────────────────────────
    fieldnames = ["rule_id", "fitness", "std_dev", "total_displacement", "velocities", "annihilated"]
    with open(RESULT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nSaved: {RESULT_CSV}")

    # ── Statistics ───────────────────────────────────────────────────────────
    scores = [r["fitness"] for r in rows]
    mean_fitness    = float(np.mean(scores))
    median_fitness  = float(np.median(scores))
    max_fitness     = float(np.max(scores))
    std_dev_fitness = float(np.std(scores))

    print("\n=== Baseline Statistics ===")
    print(f"  population_size:    {POPULATION_SIZE}")
    print(f"  annihilation_count: {annihilation_count}")
    print(f"  mean_fitness:       {mean_fitness:.6f}")
    print(f"  median_fitness:     {median_fitness:.6f}")
    print(f"  max_fitness:        {max_fitness:.6f}")
    print(f"  std_dev_fitness:    {std_dev_fitness:.6f}")

    yaml_block = {
        "status": "ok",
        "artifacts": ["archive/iter_150/results/fitness_scores.csv"],
        "metrics": {
            "mean_fitness":       round(mean_fitness, 6),
            "median_fitness":     round(median_fitness, 6),
            "max_fitness":        round(max_fitness, 6),
            "std_dev_fitness":    round(std_dev_fitness, 6),
            "annihilation_count": annihilation_count,
            "population_size":    POPULATION_SIZE,
        },
        "log_excerpt": (
            f"  rule_001..rule_{POPULATION_SIZE:03d} evaluated\n"
            f"  annihilation_count={annihilation_count}\n"
            f"  mean_fitness={mean_fitness:.6f}\n"
            f"  median_fitness={median_fitness:.6f}\n"
            f"  max_fitness={max_fitness:.6f}\n"
            f"  std_dev_fitness={std_dev_fitness:.6f}\n"
            f"  Saved: archive/iter_150/results/fitness_scores.csv\n"
        ),
        "experimenter_view": (
            f"Baseline over {POPULATION_SIZE} random C2-symmetric rules with {KERNEL_PAIRS} kernel pairs "
            f"each. Soup: {GRID_SIZE}x{GRID_SIZE}, {SOUP_DENSITY:.0%} density. "
            f"Evaluation: {total_steps} steps ({NUM_WINDOWS} windows x {STEPS_PER_WINDOW}). "
            f"Annihilation (total displacement=0) observed in {annihilation_count}/{POPULATION_SIZE} rules. "
            f"Max fitness={max_fitness:.4f} indicates the best naturally occurring "
            f"velocity-stable behaviour in a random sample; mean={mean_fitness:.4f} "
            f"sets the floor for evolution to beat."
        ),
        "notes": "Baseline measurement for velocity-stability metric.",
    }

    print("\n---\n")
    print(yaml.dump(yaml_block, default_flow_style=False, sort_keys=False, allow_unicode=True))

    return 0


if __name__ == "__main__":
    sys.exit(main())
