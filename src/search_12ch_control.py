#!/usr/bin/env python3
"""
search_12ch_control.py — 12-channel FCC LGCA control search.

Mirrors the 13-channel search but uses the 12-channel engine and LUTs.
Maps ch12 (rest) to unused propagation channels to maintain equivalent
bit counts and spatial configurations.
"""

from __future__ import annotations
import json
import sys
import time
import numpy as np

SCRIPT_DIR = __import__("pathlib").Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from engine_3d import stream, collide
from non_additive_lut_v2 import build_randomized_w3plus_lut

L = 24
STEPS = 300

# ─── LUT generation ───────────────────────────────────────────────────────────

def generate_control_luts(n_luts=100):
    """Generate 100 12-channel O_h-equivariant LUTs.
    
    Uses build_randomized_w3plus_lut(w2_cfg, seed) where:
    - w2_cfg = i % 128
    - seed = i // 128
    """
    luts = []
    configs = []
    for i in range(n_luts):
        w2_cfg = i % 128
        seed = i // 128
        lut = build_randomized_w3plus_lut(w2_cfg, seed)
        luts.append(lut)
        configs.append({"w2_config": w2_cfg, "w3plus_seed": seed, "index": i})
    return luts, configs


# ─── Seed definitions (adapted from 13ch) ─────────────────────────────────────

# For seeds with ch12 (rest), map ch12 to an unused propagation channel.
# We use channel 3 as the replacement (it's a propagation channel and typically
# unused in the seed bit patterns).

def build_seeds():
    """Build 30 seeds in 5 categories, identical to the 13-channel search
    but with ch12 mapped to ch3 (unused propagation channel).
    
    Returns list of (category_name, seed_list) tuples.
    """
    REST_REPLACEMENT = 3  # Map ch12 -> ch3 for 12-channel simulation

    def adapt_seed(seed_13ch):
        """Convert 13ch seed (with ch12) to 12ch seed (ch12 -> ch3)."""
        result = []
        for r, c, l, ch in seed_13ch:
            actual_ch = REST_REPLACEMENT if ch == 12 else ch
            result.append((r, c, l, actual_ch))
        return result

    # Category 1: 2 adjacent bits including 1 rest bit
    cat1_13ch = [
        [(12, 12, 12, 0), (12, 12, 12, 12)],
        [(12, 12, 12, 1), (12, 12, 12, 12)],
        [(12, 12, 12, 2), (12, 12, 12, 12)],
        [(12, 12, 12, 4), (12, 12, 12, 12)],
        [(12, 12, 12, 6), (12, 12, 12, 12)],
    ]

    # Category 2: 2 adjacent bits both prop (identical in both engines)
    cat2 = [
        [(12, 12, 12, 0), (12, 12, 12, 4)],
        [(12, 12, 12, 0), (12, 12, 12, 1)],
        [(12, 12, 12, 2), (12, 12, 12, 4)],
        [(12, 12, 12, 6), (12, 12, 12, 7)],
        [(12, 12, 12, 8), (12, 12, 12, 2)],
    ]

    # Category 3: 3 adjacent bits including rest
    cat3_13ch = [
        [(12, 12, 12, 0), (12, 12, 12, 4), (12, 12, 12, 12)],
        [(12, 12, 12, 1), (12, 12, 12, 5), (12, 12, 12, 12)],
        [(12, 12, 12, 2), (12, 12, 12, 6), (12, 12, 12, 12)],
        [(12, 12, 12, 0), (12, 12, 12, 2), (12, 12, 12, 12)],
        [(12, 12, 12, 6), (12, 12, 12, 7), (12, 12, 12, 12)],
    ]

    # Category 4: 3 adjacent bits all prop (identical)
    cat4 = [
        [(12, 12, 12, 0), (12, 12, 12, 4), (12, 12, 12, 7)],
        [(12, 12, 12, 1), (12, 12, 12, 5), (12, 12, 12, 10)],
        [(12, 12, 12, 2), (12, 12, 12, 5), (12, 12, 12, 8)],
        [(12, 12, 12, 0), (12, 12, 12, 6), (12, 12, 12, 8)],
        [(12, 12, 12, 4), (12, 12, 12, 7), (12, 12, 12, 11)],
    ]

    # Category 5: 2-3 bits at non-adjacent cells (identical)
    cat5 = [
        [(12, 12, 12, 0), (12, 13, 13, 1)],
        [(10, 10, 10, 6), (14, 14, 14, 9)],
        [(11, 11, 11, 0), (11, 11, 11, 4), (13, 13, 13, 1)],
        [(12, 10, 10, 2), (12, 14, 14, 3)],
        [(12, 12, 12, 0), (12, 12, 12, 1), (14, 14, 14, 2)],
    ]

    all_categories = [
        ("2adj_with_rest", [adapt_seed(s) for s in cat1_13ch]),
        ("2adj_both_prop", cat2),
        ("3adj_with_rest", [adapt_seed(s) for s in cat3_13ch]),
        ("3adj_all_prop", cat4),
        ("nonadjacent", cat5),
    ]
    return all_categories


def place_seed(grid, seed):
    """Place a seed onto a grid of shape (L,L,L,12)."""
    for r, c, l, ch in seed:
        grid[r % L, c % L, l % L, ch] = 1


def count_bits(grid):
    return int(grid.sum())


def center_of_mass(grid):
    """Return weighted center of mass (l, r, c) as floats."""
    total = 0.0
    com_l = 0.0
    com_r = 0.0
    com_c = 0.0
    for l in range(L):
        for r in range(L):
            for c in range(L):
                cell = int(grid[l, r, c, :].sum())
                if cell > 0:
                    com_l += cell * l
                    com_r += cell * r
                    com_c += cell * c
                    total += cell
    if total == 0:
        return 0.0, 0.0, 0.0
    return com_l / total, com_r / total, com_c / total


def unwrap_delta(old_com, new_com):
    """Compute unwrapped delta, handling torus wrapping."""
    delta = np.array(new_com) - np.array(old_com)
    for i in range(3):
        if delta[i] > L / 2:
            delta[i] -= L
        elif delta[i] < -L / 2:
            delta[i] += L
    return delta


def bounding_extent(grid):
    """Return (dl, dr, dc) of the bounding box of occupied cells."""
    occupied = np.argwhere(grid.sum(axis=3) > 0)
    if len(occupied) == 0:
        return 0, 0, 0
    mins = occupied.min(axis=0)
    maxs = occupied.max(axis=0)
    return int(maxs[0] - mins[0]), int(maxs[1] - mins[1]), int(maxs[2] - mins[2])


def run_simulation(lut, seed_bits, steps=STEPS):
    """Run a simulation for a given LUT and seed configuration."""
    grid = np.zeros((L, L, L, 12), dtype=np.uint8)

    initial_bits = 0
    for r, c, l, ch in seed_bits:
        grid[r % L, c % L, l % L, ch] = 1
        initial_bits += 1

    old_com = center_of_mass(grid)
    total_displacement = np.zeros(3, dtype=np.float64)

    max_extent = (0, 0, 0)
    min_bit_count = initial_bits
    max_bit_count = initial_bits

    for step in range(steps):
        grid = stream(grid)
        grid = collide(grid, lut)

        bc = count_bits(grid)
        min_bit_count = min(min_bit_count, bc)
        max_bit_count = max(max_bit_count, bc)

        # COM tracking
        new_com = center_of_mass(grid)
        delta = unwrap_delta(old_com, new_com)
        total_displacement += delta
        old_com = new_com

        # Bounding extent
        ext = bounding_extent(grid)
        max_extent = tuple(max(a, b) for a, b in zip(max_extent, ext))

    final_bits = count_bits(grid)
    disp_norm = float(np.linalg.norm(total_displacement))
    bit_stability = 1.0 if final_bits == initial_bits else 0.0
    score = disp_norm * bit_stability

    return {
        "initial_bits": initial_bits,
        "final_bits": final_bits,
        "min_bits": min_bit_count,
        "max_bits": max_bit_count,
        "displacement_xyz": total_displacement.tolist(),
        "displacement_norm": disp_norm,
        "bit_stability": bit_stability,
        "score": score,
        "max_extent": list(max_extent),
    }


def main():
    t_start = time.time()
    print("[search_12ch_control] Starting 12-channel control search...")

    # 1. Generate LUTs
    print("[search_12ch_control] Generating 100 LUTs...")
    all_luts, all_configs = generate_control_luts(n_luts=100)
    print(f"[search_12ch_control] Generated {len(all_luts)} LUTs.")

    # 2. Build seeds
    categories = build_seeds()
    all_seeds = []
    for cat_name, cat_seeds in categories:
        for seed_idx, seed in enumerate(cat_seeds):
            seed_name = f"{cat_name}_s{seed_idx}"
            all_seeds.append((seed_name, seed, cat_name))
    print(f"[search_12ch_control] Defined {len(all_seeds)} seeds in {len(categories)} categories.")

    # 3. Run simulations
    total_runs = len(all_luts) * len(all_seeds)
    print(f"[search_12ch_control] Total runs: {total_runs}")

    results = []
    successful_runs = 0
    nonzero_score_runs = 0
    propagating_runs = []

    run_start = time.time()

    for li, lut in enumerate(all_luts):
        lut_cfg = all_configs[li]
        for si, (seed_name, seed_bits, cat_name) in enumerate(all_seeds):
            run_idx = li * len(all_seeds) + si
            if run_idx % 500 == 0:
                elapsed = time.time() - run_start
                rate = elapsed / max(run_idx, 1)
                eta = rate * (total_runs - run_idx)
                print(f"[search_12ch_control] Run {run_idx}/{total_runs} | elapsed={elapsed:.1f}s | ETA={eta:.1f}s")

            result = run_simulation(lut, seed_bits, steps=STEPS)
            result["lut_index"] = lut_cfg["index"]
            result["lut_w2_config"] = lut_cfg["w2_config"]
            result["lut_w3plus_seed"] = lut_cfg["w3plus_seed"]
            result["seed_name"] = seed_name
            result["category"] = cat_name

            if result["bit_stability"] > 0:
                successful_runs += 1
                if result["score"] > 0:
                    nonzero_score_runs += 1
                    propagating_runs.append({
                        "lut_index": result["lut_index"],
                        "lut_w2_config": lut_cfg["w2_config"],
                        "lut_w3plus_seed": lut_cfg["w3plus_seed"],
                        "seed_name": seed_name,
                        "score": result["score"],
                        "displacement_norm": result["displacement_norm"],
                        "displacement_xyz": result["displacement_xyz"],
                        "bits": result["final_bits"],
                    })

            results.append(result)

    total_time = time.time() - t_start

    propagating_runs.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n[search_12ch_control] === SUMMARY ===")
    print(f"  Total LUTs tested:    {len(all_luts)}")
    print(f"  Total seeds:          {len(all_seeds)}")
    print(f"  Total runs:           {total_runs}")
    print(f"  Successful (stable):  {successful_runs}")
    print(f"  Non-zero score:       {nonzero_score_runs}")
    print(f"  Total time:           {total_time:.1f}s")

    if propagating_runs:
        print(f"\n  Top 5 propagating structures:")
        for r in propagating_runs[:5]:
            print(f"    LUT={r['lut_index']} seed={r['seed_name']} "
                  f"score={r['score']:.4f} disp={r['displacement_norm']:.4f} "
                  f"bits={r['bits']}")
    else:
        print("\n  No propagating structures discovered.")

    # Save
    output = {
        "search_type": "12_channel_control",
        "grid_size": L,
        "steps": STEPS,
        "n_luts_tested": len(all_luts),
        "n_seeds": len(all_seeds),
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "nonzero_score_runs": nonzero_score_runs,
        "total_time_seconds": total_time,
        "top_propagating_runs": propagating_runs[:20],
        "category_summaries": {},
        "results": results,
    }

    for cat_name, _ in categories:
        cat_results = [r for r in results if r["category"] == cat_name]
        if cat_results:
            scores = [r["score"] for r in cat_results]
            output["category_summaries"][cat_name] = {
                "n_runs": len(cat_results),
                "mean_score": float(np.mean(scores)),
                "max_score": float(np.max(scores)),
                "median_score": float(np.median(scores)),
                "nonzero_count": sum(1 for s in scores if s > 0),
            }

    out_dir = SCRIPT_DIR.parent / "archive" / "iter_251" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "control_results.json", "w") as f:
        json_results = json.loads(json.dumps(output, default=str))
        json.dump(json_results, f, indent=2)

    print(f"\n[search_12ch_control] Results saved to {out_dir / 'control_results.json'}")


if __name__ == "__main__":
    main()
