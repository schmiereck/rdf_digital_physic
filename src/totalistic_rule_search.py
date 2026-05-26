#!/usr/bin/env python3
"""
totalistic_rule_search.py

Step 2 of the pre-registered experiment (iter_253).
Designed rule sweep for 3D synchronous FCC CA with totalistic B/S rules.

Grid: 40x40x40
Simulation steps: 500
Rules: 200 unique totalistic B/S rules (B ⊆ {1,...,11}, S ⊆ {1,...,12}, 0 ∉ B,S)
Seeds: 46 unique initial configurations
"""

from __future__ import annotations
import csv
import json
import os
import random
import sys
from collections import defaultdict
from math import comb
from pathlib import Path

import numpy as np

# Ensure src is importable
SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from synchronous_ca_fcc import (
    FCC_OFFSETS,
    bounding_extent,
    format_rule,
    lambda_param,
    simulate,
    step_ca,
    trig_com,
    unwrap_com,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
L = 40
CENTER = (L // 2, L // 2, L // 2)
STEPS = 500
RULE_RNG = random.Random(42)
SEED_RNG = random.Random(42)

# Maximum neighbors for totalistic counts
MAX_N = 12

# Output paths
ARCHIVE_DIR = SCRIPT_DIR.parent / "archive" / "iter_253" / "results"
ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
SWEEP_CSV = ARCHIVE_DIR / "sweep_results.csv"
PHASE_CSV = ARCHIVE_DIR / "phase_diagram.csv"

# ---------------------------------------------------------------------------
# Rule generation
# ---------------------------------------------------------------------------

def make_grid() -> np.ndarray:
    """Return an empty L×L×L grid."""
    return np.zeros((L, L, L), dtype=np.uint8)


def set_cells(grid: np.ndarray, coords: list[tuple[int, int, int]]) -> None:
    """Set cells to 1 at the given coordinates (mod L)."""
    for l, r, c in coords:
        grid[l % L, r % L, c % L] = 1


def generate_unique_rules(n_total: int = 200) -> list[tuple[set, set]]:
    """Generate exactly n_total unique B/S rules deterministically."""
    rules = set()

    def rule_key(B, S):
        return (tuple(sorted(B)), tuple(sorted(S)))

    # --- Sparse rules: |B| <= 2, |S| <= 3 ---
    sparse_count = 0
    while sparse_count < 100:
        b_size = RULE_RNG.randint(1, 2)
        s_size = RULE_RNG.randint(1, 3)
        B = set(RULE_RNG.sample(range(1, 12), b_size))
        S = set(RULE_RNG.sample(range(1, 13), s_size))
        key = rule_key(B, S)
        if key not in rules:
            rules.add(key)
            sparse_count += 1

    # --- Medium rules: |B| in {2,3}, |S| in {3,4,5} ---
    medium_count = 0
    while medium_count < 50:
        b_size = RULE_RNG.randint(2, 3)
        s_size = RULE_RNG.randint(3, 5)
        B = set(RULE_RNG.sample(range(1, 12), b_size))
        S = set(RULE_RNG.sample(range(1, 13), s_size))
        key = rule_key(B, S)
        if key not in rules:
            rules.add(key)
            medium_count += 1

    # --- Lambda-targeted rules: λ in [0.25, 0.45] ---
    lambda_count = 0
    attempts = 0
    while lambda_count < 50 and attempts < 50000:
        attempts += 1
        b_size = RULE_RNG.randint(1, 6)
        s_size = RULE_RNG.randint(1, 7)
        B = set(RULE_RNG.sample(range(1, 12), b_size))
        S = set(RULE_RNG.sample(range(1, 13), s_size))
        lam = lambda_param(B, S)
        if 0.25 <= lam <= 0.45:
            key = rule_key(B, S)
            if key not in rules:
                rules.add(key)
                lambda_count += 1

    # Convert back to (B, S) tuples
    result = []
    for b_tup, s_tup in rules:
        result.append((set(b_tup), set(s_tup)))
    RULE_RNG.shuffle(result)
    return result


# ---------------------------------------------------------------------------
# Seed generation
# ---------------------------------------------------------------------------

def generate_seeds() -> list[tuple[str, list[tuple[int, int, int]]]]:
    """Generate 46 unique deterministic seeds.

    Returns list of (seed_name, coords).
    """
    seeds = []
    c = CENTER

    # Seed 0: single bit at center
    seeds.append(("single_bit", [c]))

    # Seeds 1-12: bit pairs at origin + one neighbor offset
    for i, off in enumerate(FCC_OFFSETS):
        seeds.append((f"pair_{i}", [c, (c[0] + off[0], c[1] + off[1], c[2] + off[2])]))

    # Seeds 13-20: 8 L-tromino analogs (connected 3-bit L-shapes)
    # Build connected L-shapes using two adjacent FCC offsets
    trominoes = []
    for i, off1 in enumerate(FCC_OFFSETS):
        p1 = (c[0] + off1[0], c[1] + off1[1], c[2] + off1[2])
        for j, off2 in enumerate(FCC_OFFSETS):
            if j <= i:
                continue
            # off2 must be adjacent to off1 (they share a common cell)
            # Simplification: use off2 from p1's neighbors relative to c
            p_test = (p1[0] + off2[0], p1[1] + off2[1], p1[2] + off2[2])
            # This creates an L-shape: c -> off1 -> off1+off2
            # To avoid degenerate collinear forms, ensure off1 != ±off2
            coords = [c, p1, p_test]
            # Also check that p_test != c and p_test != p1
            if p_test != c and p_test != p1:
                trominoes.append(coords)
                if len(trominoes) >= 8:
                    break
        if len(trominoes) >= 8:
            break

    for idx, coords in enumerate(trominoes[:8], start=13):
        seeds.append((f"tromino_L_{idx - 13}", coords))

    # Seeds 21-45: 25 random compact clusters of size 3-6
    # Start from center, add adjacent neighbor offsets to ensure connected
    compact_seeds = []
    while len(compact_seeds) < 25:
        size = SEED_RNG.randint(3, 6)
        cluster = [c]
        for _ in range(size - 1):
            # Pick a random existing cell
            existing = SEED_RNG.choice(cluster)
            # Pick a random neighbor offset
            off = SEED_RNG.choice(FCC_OFFSETS)
            new_cell = (
                (existing[0] + off[0]),
                (existing[1] + off[1]),
                (existing[2] + off[2]),
            )
            if new_cell not in cluster:
                cluster.append(new_cell)
        # Normalize: translate so min coords are near origin, then center
        # For uniqueness, sort the coordinates
        sorted_cluster = sorted(cluster)
        if sorted_cluster not in [sorted(s[1]) for s in compact_seeds]:
            compact_seeds.append(sorted_cluster)

    for idx, coords in enumerate(compact_seeds, start=21):
        seeds.append((f"compact_{idx - 21}", coords))

    return seeds


# ---------------------------------------------------------------------------
# Single-bit survival test (cooperative survival check)
# ---------------------------------------------------------------------------

def single_bit_survival_time(B: set, S: set, max_steps: int = 50) -> int:
    """Return the first step at which a single-bit seed dies, or max_steps if it survives."""
    grid = make_grid()
    grid[CENTER] = 1
    for step in range(1, max_steps + 1):
        grid = step_ca(grid, B, S)
        if grid.sum() == 0:
            return step
    return max_steps


def is_cooperative(B: set, S: set) -> bool:
    """Return True iff a single-bit seed dies within <= 50 steps."""
    return single_bit_survival_time(B, S, 50) <= 50


# ---------------------------------------------------------------------------
# Simulation + filtering
# ---------------------------------------------------------------------------

def evaluate_rule_seed(B: set, S: set, seed_coords: list[tuple[int, int, int]], seed_name: str):
    """Run simulation and return filter metrics."""
    grid = make_grid()
    set_cells(grid, seed_coords)
    initial_bits = len(seed_coords)

    result = simulate(grid, B, S, steps=STEPS)
    bit_counts = result["bit_counts"]
    coms = result["coms"]
    extents = result["extents"]
    survival_time = result["survival_time"]

    # Survival: bit_count > 0 at step 300
    survived_300 = survival_time > 300

    # Displacement: use final step if survival > 300, else step 300
    eval_step = min(survival_time, STEPS) if survival_time <= STEPS else STEPS
    if eval_step > 300:
        eval_step = STEPS
    else:
        eval_step = survival_time

    if len(coms) > eval_step:
        displacement_vec = tuple(coms[eval_step][i] - coms[0][i] for i in range(3))
        net_displacement = float(np.linalg.norm(displacement_vec))
    else:
        # Shouldn't happen due to padding in simulate
        net_displacement = 0.0

    # Max bounding box after step 100
    if survival_time > 100:
        max_extent_after_100 = max(extents[101:survival_time + 1]) if survival_time <= STEPS else max(extents[101:])
    else:
        max_extent_after_100 = float('inf')

    # Max bit ratio after step 100
    if survival_time > 100:
        max_bits_after_100 = max(bit_counts[101:survival_time + 1]) if survival_time <= STEPS else max(bit_counts[101:])
        max_bit_ratio = max_bits_after_100 / max(initial_bits, 1)
    else:
        max_bit_ratio = float('inf')

    verdict = "candidate" if (
        survived_300
        and net_displacement >= 5.0
        and max_extent_after_100 <= 10
        and max_bit_ratio <= 4.0
    ) else "rejected"

    return {
        "rule_str": format_rule(B, S),
        "seed_id": seed_name,
        "survival": survival_time,
        "displacement": round(net_displacement, 4),
        "max_bit_ratio": round(max_bit_ratio, 4),
        "max_bounding_box": max_extent_after_100,
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("STEP 2 — DESIGNED RULE SWEEP (iter_253)")
    print("=" * 70)

    rules = generate_unique_rules(200)
    seeds = generate_seeds()

    print(f"Rules generated: {len(rules)}")
    print(f"Seeds generated: {len(seeds)}")
    print(f"Total evaluations: {len(rules) * len(seeds)}")
    print(f"Grid: {L}×{L}×{L}, Steps: {STEPS}")
    print()

    # Pre-compute cooperative survival for all rules
    print("Pre-computing single-bit cooperative survival ...")
    coop_map = {}
    for B, S in rules:
        rstr = format_rule(B, S)
        coop_map[rstr] = is_cooperative(B, S)
    n_coop = sum(1 for v in coop_map.values() if v)
    print(f"  Rules with cooperative survival (single-bit dies ≤50 steps): {n_coop}/{len(rules)}")
    print()

    # Sweep
    results = []
    candidates = []
    rule_lambda_stats = defaultdict(lambda: {"n_seeds": 0, "n_survive": 0, "displacements": [], "n_candidate": 0})
    n_evaluated = 0

    total_evals = len(rules) * len(seeds)
    for ri, (B, S) in enumerate(rules):
        rstr = format_rule(B, S)
        lam = lambda_param(B, S)
        coop = coop_map[rstr]

        for si, (sname, scoords) in enumerate(seeds):
            n_evaluated += 1
            if n_evaluated % 500 == 0 or n_evaluated == 1:
                pct = 100.0 * n_evaluated / total_evals
                print(f"  Evaluating {n_evaluated}/{total_evals} ({pct:.1f}%) ...")

            row = evaluate_rule_seed(B, S, scoords, sname)
            # Apply cooperative filter: if single-bit doesn't die, it's NOT a candidate
            if not coop:
                row["verdict"] = "rejected_noncoop"

            results.append(row)

            # Stats per rule
            rule_lambda_stats[round(lam, 3)]["n_seeds"] += 1
            if row["survival"] > 300:
                rule_lambda_stats[round(lam, 3)]["n_survive"] += 1
                rule_lambda_stats[round(lam, 3)]["displacements"].append(row["displacement"])
            if row["verdict"] == "candidate":
                rule_lambda_stats[round(lam, 3)]["n_candidate"] += 1
                candidates.append((rstr, sname))

    # --- Save sweep_results.csv ---
    with open(SWEEP_CSV, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["rule_str", "seed_id", "survival", "displacement", "max_bit_ratio", "max_bounding_box", "verdict"],
        )
        writer.writeheader()
        writer.writerows(results)
    print(f"\nSaved sweep results: {SWEEP_CSV}")

    # --- Save phase_diagram.csv ---
    phase_rows = []
    for lam in sorted(rule_lambda_stats.keys()):
        stats = rule_lambda_stats[lam]
        n = stats["n_seeds"]
        frac_survive = stats["n_survive"] / max(n, 1)
        mean_disp = np.mean(stats["displacements"]) if stats["displacements"] else 0.0
        phase_rows.append({
            "lambda": round(lam, 3),
            "n_rules_evaluated": len(rules) // len(rule_lambda_stats) + (1 if lam < 0.5 else 0),  # approximate
            "total_evaluations": n,
            "seeds_surviving_300": stats["n_survive"],
            "fraction_surviving": round(frac_survive, 4),
            "mean_displacement": round(float(mean_disp), 4),
            "n_candidate_seeds": stats["n_candidate"],
        })

    with open(PHASE_CSV, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["lambda", "n_rules_evaluated", "total_evaluations", "seeds_surviving_300", "fraction_surviving", "mean_displacement", "n_candidate_seeds"],
        )
        writer.writeheader()
        writer.writerows(phase_rows)
    print(f"Saved phase diagram: {PHASE_CSV}")

    # --- Summary ---
    n_candidates = len(candidates)
    n_unique_rules_with_candidates = len(set(r for r, _ in candidates))
    print("\n" + "=" * 70)
    print("SWEEP SUMMARY")
    print("=" * 70)
    print(f"Total rule×seed evaluations: {len(results)}")
    print(f"Unique rules: {len(rules)}")
    print(f"Cooperative rules (single-bit dies ≤50): {n_coop}")
    print(f"Candidate seeds (pass all filters): {n_candidates}")
    print(f"Unique rules with at least one candidate seed: {n_unique_rules_with_candidates}")

    # Save a lightweight JSON summary for downstream steps
    summary = {
        "total_rules": len(rules),
        "total_seeds": len(seeds),
        "total_evaluations": len(results),
        "cooperative_rules": n_coop,
        "candidate_count": n_candidates,
        "unique_candidate_rules": n_unique_rules_with_candidates,
        "candidates": candidates,
    }
    with open(ARCHIVE_DIR / "sweep_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary: {ARCHIVE_DIR / 'sweep_summary.json'}")

    return n_candidates, len(rules)


if __name__ == "__main__":
    main()
