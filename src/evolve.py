#!/usr/bin/env python3
"""
evolve.py

Evolutionary algorithm driver for C2-symmetric CA rules with the composite
fitness metric: total_displacement / (1 + std_dev).

Usage:
  python src/evolve.py --generation 2 \
      --input_population archive/iter_151/results/rules_and_fitness.csv \
      --output_dir archive/iter_152/results/ \
      --elite_fraction 0.1

The script re-derives the Gen-1 rule dictionaries by re-running the same
deterministic rule generator (seed=150) that measure_baseline.py used,
then matches each rule to its CSV row by rule_id.
"""

import argparse
import csv
import math
import random
import sys
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(Path(__file__).parent))

# ── Simulation constants (must match measure_baseline.py) ─────────────────────
GRID_SIZE        = 150
SOUP_DENSITY     = 0.25
SOUP_SEED        = 42
GEN1_RULE_SEED   = 150
KERNEL_PAIRS     = 8
STEPS_PER_WINDOW = 400
NUM_WINDOWS      = 4
MAX_ATTEMPTS     = 50000
MAX_BREED        = 500
POPULATION_SIZE  = 100


# ── HEX / C2 rule helpers (copied from measure_baseline.py) ───────────────────

def _rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
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
            for _ in range(300):
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


# ── Kernel pair extraction / genetic operators ─────────────────────────────────

def _canonical_c2_pair(a: int, b: int) -> tuple:
    ra = _rotate_c2(a)
    rb = _rotate_c2(b)
    return min((a, b), (b, a), (ra, rb), (rb, ra))


def extract_kernel_pairs(rule_dict: dict) -> list:
    seen = set()
    pairs = []
    for a_str, b in rule_dict.items():
        a = int(a_str)
        b = int(b)
        if a == b:
            continue
        canon = _canonical_c2_pair(a, b)
        if canon not in seen:
            seen.add(canon)
            pairs.append((a, b))
    return pairs


def _dedup_kernels(kernels: list) -> list:
    seen = set()
    result = []
    for a, b in kernels:
        if a == b or not _is_valid_c2_pair(a, b):
            continue
        canon = _canonical_c2_pair(a, b)
        if canon not in seen:
            seen.add(canon)
            result.append((a, b))
    return result


def crossover(p1: list, p2: list, rng: random.Random) -> list:
    a = p1.copy(); rng.shuffle(a)
    b = p2.copy(); rng.shuffle(b)
    n1 = max(1, len(a) // 2)
    n2 = max(1, len(b) // 2)
    return a[:n1] + b[:n2]


def mutate(kernels: list, rng: random.Random, prob: float = 0.3) -> list:
    if rng.random() >= prob:
        return kernels
    kernels = kernels.copy()
    choice = rng.choice(["add", "delete", "flip"])
    if choice == "add":
        for _ in range(500):
            a = rng.randint(1, 127)
            b = rng.randint(1, 127)
            if _is_valid_c2_pair(a, b):
                kernels.append((a, b))
                break
    elif choice == "delete":
        if len(kernels) > 2:
            kernels.pop(rng.randrange(len(kernels)))
    else:
        if kernels:
            idx = rng.randrange(len(kernels))
            a, b = kernels[idx]
            for _ in range(100):
                if rng.random() < 0.5:
                    na = max(1, (a ^ (1 << rng.randrange(7))) & 127)
                    if _is_valid_c2_pair(na, b):
                        kernels[idx] = (na, b)
                        break
                else:
                    nb = max(1, (b ^ (1 << rng.randrange(7))) & 127)
                    if _is_valid_c2_pair(a, nb):
                        kernels[idx] = (a, nb)
                        break
    return kernels


def breed_child(p1_kernels: list, p2_kernels: list,
                rng: random.Random) -> dict | None:
    for _ in range(MAX_BREED):
        child = crossover(p1_kernels, p2_kernels, rng)
        child = mutate(child, rng)
        child = _dedup_kernels(child)
        if not child:
            continue
        rule = _try_build_c2_rule(child)
        if rule is not None:
            return rule
    return None


# ── Fitness evaluation ─────────────────────────────────────────────────────────

def _rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def _step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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
    return lut[state]


def _center_of_mass(grid: np.ndarray) -> tuple:
    xs, ys = np.where(grid > 0)
    if len(xs) == 0:
        return (0.0, 0.0)
    return (float(np.mean(xs)), float(np.mean(ys)))


def evaluate_composite(rule_dict: dict, soup: np.ndarray) -> dict:
    """Evaluate using composite fitness: total_displacement / (1 + std_dev)."""
    lut  = _rule_to_lut(rule_dict)
    grid = np.copy(soup)

    checkpoints = [_center_of_mass(grid)]
    for _ in range(NUM_WINDOWS):
        for __ in range(STEPS_PER_WINDOW):
            grid = _step_grid(grid, lut)
        checkpoints.append(_center_of_mass(grid))

    velocities = []
    for i in range(NUM_WINDOWS):
        sq, sr = checkpoints[i]
        eq, er = checkpoints[i + 1]
        velocities.append(math.sqrt((eq - sq)**2 + (er - sr)**2))

    total_disp = sum(velocities)
    std_dev    = float(np.std(velocities))

    if total_disp < 1e-9:
        composite = 0.0
    else:
        composite = total_disp / (1.0 + std_dev)

    return {
        "composite_fitness": round(composite, 8),
        "total_displacement": round(total_disp, 6),
        "std_dev": round(std_dev, 8),
        "velocities": ";".join(f"{v:.4f}" for v in velocities),
        "annihilated": 1 if total_disp < 1e-9 else 0,
    }


# ── Soup ──────────────────────────────────────────────────────────────────────

def make_soup() -> np.ndarray:
    rng = np.random.default_rng(SOUP_SEED)
    return (rng.random((GRID_SIZE, GRID_SIZE)) < SOUP_DENSITY).astype(np.uint8)


# ── Gen-1 rule regeneration ───────────────────────────────────────────────────

def regenerate_gen1_rules() -> dict[str, dict]:
    """Reproduce the Gen-1 rule dicts from measure_baseline.py (seed=150)."""
    rng = random.Random(GEN1_RULE_SEED)
    rules = {}
    for i in range(1, POPULATION_SIZE + 1):
        rule_id   = f"rule_{i:03d}"
        rule_dict = generate_random_c2_rule(rng)
        rules[rule_id] = rule_dict
    return rules


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generation",        type=int,   default=2)
    parser.add_argument("--input_population",  type=str,
                        default="archive/iter_151/results/rules_and_fitness.csv")
    parser.add_argument("--output_dir",        type=str,
                        default="archive/iter_152/results/")
    parser.add_argument("--elite_fraction",    type=float, default=0.1)
    args = parser.parse_args()

    input_csv  = PROJECT_ROOT / args.input_population
    output_dir = PROJECT_ROOT / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Load Gen-1 CSV ────────────────────────────────────────────────
    # The iter_151 CSV may not exist yet; fall back to iter_150 fitness_scores.
    fallback_csv = PROJECT_ROOT / "archive" / "iter_150" / "results" / "fitness_scores.csv"

    if not input_csv.exists():
        print(f"[warn] {input_csv} not found — will create it from iter_150 data.")
        src_csv = fallback_csv
    else:
        src_csv = input_csv

    print(f"Loading Gen-1 population from {src_csv} ...")
    gen1_rows = []
    with open(src_csv) as f:
        reader = csv.DictReader(f)
        for row in reader:
            td  = float(row.get("total_displacement", 0.0))
            sd  = float(row.get("std_dev", 0.0))
            fit = td / (1.0 + sd) if td > 1e-9 else 0.0
            gen1_rows.append({
                "rule_id":            row["rule_id"],
                "total_displacement": td,
                "std_dev":            sd,
                "composite_fitness":  round(fit, 8),
                "velocities":         row.get("velocities", ""),
                "annihilated":        int(row.get("annihilated", 0)),
            })

    # Write rules_and_fitness.csv to iter_151/results/ if it didn't exist
    if not input_csv.exists():
        input_csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = ["rule_id", "composite_fitness", "total_displacement",
                      "std_dev", "velocities", "annihilated"]
        with open(input_csv, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows([{k: r[k] for k in fieldnames} for r in gen1_rows])
        print(f"  Created: {input_csv}")

    print(f"  Loaded {len(gen1_rows)} Gen-1 rules.")
    scores = [r["composite_fitness"] for r in gen1_rows]
    print(f"  Gen-1 composite fitness — mean: {np.mean(scores):.6f}  "
          f"median: {np.median(scores):.6f}  max: {np.max(scores):.6f}")

    # ── Step 2: Select elites ─────────────────────────────────────────────────
    elite_count = max(1, int(len(gen1_rows) * args.elite_fraction))
    gen1_sorted = sorted(gen1_rows, key=lambda r: r["composite_fitness"], reverse=True)
    elites      = gen1_sorted[:elite_count]
    print(f"\nSelected top {elite_count} elites (elite_fraction={args.elite_fraction}):")
    for e in elites:
        print(f"  {e['rule_id']}: composite_fitness={e['composite_fitness']:.6f}  "
              f"total_displacement={e['total_displacement']:.6f}  std_dev={e['std_dev']:.6f}")

    # ── Step 3: Regenerate Gen-1 rule dicts (deterministic, seed=150) ─────────
    print("\nRegenerating Gen-1 rule dictionaries (seed=150) ...")
    all_gen1_rule_dicts = regenerate_gen1_rules()
    elite_rule_dicts = {e["rule_id"]: all_gen1_rule_dicts[e["rule_id"]] for e in elites}

    # Extract kernel pairs
    elite_info = []
    for e in elites:
        rule_dict = elite_rule_dicts[e["rule_id"]]
        pairs     = extract_kernel_pairs(rule_dict)
        elite_info.append({
            "rule_id":   e["rule_id"],
            "rule_dict": rule_dict,
            "pairs":     pairs,
            "fitness":   e["composite_fitness"],
        })
        print(f"  {e['rule_id']}: {len(pairs)} kernel pairs")

    # ── Step 4: Breed Gen-2 population ────────────────────────────────────────
    breed_rng = random.Random(152)
    print(f"\nBreeding {POPULATION_SIZE} Gen-2 rules ...")

    gen2_rules: list[tuple[str, dict]] = []
    failed = 0
    carried = 0

    # Carry top-2 elites directly
    for rank, info in enumerate(elite_info[:2]):
        rule_id = f"rule_{rank + 1:03d}"
        gen2_rules.append((rule_id, info["rule_dict"]))
        print(f"  [carry] {rule_id} from {info['rule_id']} "
              f"(fitness={info['fitness']:.6f})")
        carried += 1

    # Breed remaining
    while len(gen2_rules) < POPULATION_SIZE:
        p1, p2 = breed_rng.sample(elite_info, 2)
        child  = breed_child(p1["pairs"], p2["pairs"], breed_rng)
        if child is None:
            failed += 1
            continue
        rule_id = f"rule_{len(gen2_rules) + 1:03d}"
        gen2_rules.append((rule_id, child))
        if len(gen2_rules) % 10 == 0:
            print(f"  Bred {len(gen2_rules)}/{POPULATION_SIZE} ...")

    print(f"  Carried: {carried}  Bred: {len(gen2_rules)-carried}  Failed attempts: {failed}")

    # ── Step 5: Evaluate Gen-2 ────────────────────────────────────────────────
    soup = make_soup()
    print(f"\nEvaluating {len(gen2_rules)} Gen-2 rules "
          f"({NUM_WINDOWS} windows × {STEPS_PER_WINDOW} steps = "
          f"{NUM_WINDOWS * STEPS_PER_WINDOW} total steps on "
          f"{GRID_SIZE}×{GRID_SIZE} soup) ...")

    gen2_rows = []
    for rule_id, rule_dict in gen2_rules:
        metrics = evaluate_composite(rule_dict, soup)
        print(f"  {rule_id}: composite={metrics['composite_fitness']:.6f}  "
              f"total_disp={metrics['total_displacement']:.4f}  "
              f"std={metrics['std_dev']:.4f}")
        gen2_rows.append({"rule_id": rule_id, **metrics})

    # ── Step 6: Save CSV ──────────────────────────────────────────────────────
    out_csv = output_dir / "gen_2_rules_and_fitness.csv"
    fieldnames = ["rule_id", "composite_fitness", "total_displacement",
                  "std_dev", "velocities", "annihilated"]
    with open(out_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{k: r[k] for k in fieldnames} for r in gen2_rows])
    print(f"\nSaved: {out_csv}")

    # ── Step 7: Summary statistics ────────────────────────────────────────────
    gen2_scores  = np.array([r["composite_fitness"] for r in gen2_rows])
    gen2_mean    = float(np.mean(gen2_scores))
    gen2_median  = float(np.median(gen2_scores))
    gen2_max     = float(np.max(gen2_scores))
    gen1_mean    = float(np.mean(scores))
    pct_change   = (gen2_mean - gen1_mean) / gen1_mean * 100.0 if gen1_mean > 0 else 0.0

    print("\n=== Gen-2 Summary ===")
    print(f"  gen1_mean_fitness:  {gen1_mean:.6f}")
    print(f"  gen2_mean_fitness:  {gen2_mean:.6f}")
    print(f"  gen2_median_fitness:{gen2_median:.6f}")
    print(f"  gen2_max_fitness:   {gen2_max:.6f}")
    print(f"  improvement:        {pct_change:+.2f}%")

    yaml_block = {
        "status": "ok",
        "artifacts": [
            str(input_csv.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            str(out_csv.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        ],
        "metrics": {
            "gen1_mean_fitness":   round(gen1_mean,   6),
            "gen2_mean_fitness":   round(gen2_mean,   6),
            "gen2_median_fitness": round(gen2_median, 6),
            "gen2_max_fitness":    round(gen2_max,    6),
            "improvement_pct":     round(pct_change,  2),
            "elite_count":         elite_count,
            "population_size":     POPULATION_SIZE,
        },
        "log_excerpt": (
            f"  Gen-1 mean composite fitness:  {gen1_mean:.6f}\n"
            f"  Gen-2 mean composite fitness:  {gen2_mean:.6f}\n"
            f"  Gen-2 median composite fitness:{gen2_median:.6f}\n"
            f"  Gen-2 max composite fitness:   {gen2_max:.6f}\n"
            f"  Improvement over Gen-1:        {pct_change:+.2f}%\n"
            f"  Failed breed attempts:          {failed}\n"
            f"  Saved: {out_csv}\n"
        ),
        "experimenter_view": (
            f"Gen-2 evolution using composite metric total_displacement / (1 + std_dev). "
            f"Selected top {elite_count}/{POPULATION_SIZE} Gen-1 rules as elite parents. "
            f"Bred {POPULATION_SIZE} offspring via crossover + mutation of C2-symmetric "
            f"kernel pairs. Evaluated on 150×150 soup (25% density, seed=42), "
            f"4 windows × 400 steps. "
            f"Gen-1 mean={gen1_mean:.4f}, Gen-2 mean={gen2_mean:.4f} "
            f"({pct_change:+.1f}% change). "
            f"Max Gen-2 fitness={gen2_max:.4f}."
        ),
        "notes": f"Gen-2 evolution with composite fitness; improvement={pct_change:+.2f}%",
    }

    yaml_str = yaml.dump(yaml_block, default_flow_style=False, sort_keys=False,
                         allow_unicode=True)
    print("\n---\n")
    print(yaml_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
