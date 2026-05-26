#!/usr/bin/env python3
"""
search_13ch.py — 13-channel FCC LGCA search with cooperative-trapping LUTs.

Steps:
1. Load/generate 500 LUT variants, sample every 5th (100 total).
2. Define 30 seeds on L=24 FCC toroidal grid in 5 categories.
3. Run 300 steps per (LUT, seed) pair.
4. Track displacement, bit stability, bounding extent, rest-channel activity.
5. Score by displacement_norm * bit_stability.
6. Save results to archive/iter_251/results/search_results.json.
"""

from __future__ import annotations
import json
import sys
import time
import numpy as np

SCRIPT_DIR = __import__("pathlib").Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from fcc_engine_13ch import stream_13, collide_13
from cooperative_lut_13ch import generate_all_lut_variants

L = 24
STEPS = 300
REST_CHANNEL = 12

# ─── Seed definitions ───────────────────────────────────────────────────────

def build_seeds():
    seeds = []
    # Category 1: 2 adjacent bits including 1 rest bit
    cat1 = [
        [(12, 12, 12, 0), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 1), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 2), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 4), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 6), (12, 12, 12, REST_CHANNEL)],
    ]
    # Category 2: 2 adjacent bits both prop
    cat2 = [
        [(12, 12, 12, 0), (12, 12, 12, 4)],
        [(12, 12, 12, 0), (12, 12, 12, 1)],
        [(12, 12, 12, 2), (12, 12, 12, 4)],
        [(12, 12, 12, 6), (12, 12, 12, 7)],
        [(12, 12, 12, 8), (12, 12, 12, 2)],
    ]
    # Category 3: 3 adjacent bits including rest
    cat3 = [
        [(12, 12, 12, 0), (12, 12, 12, 4), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 1), (12, 12, 12, 5), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 2), (12, 12, 12, 6), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 0), (12, 12, 12, 2), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 6), (12, 12, 12, 7), (12, 12, 12, REST_CHANNEL)],
    ]
    # Category 4: 3 adjacent bits all prop
    cat4 = [
        [(12, 12, 12, 0), (12, 12, 12, 4), (12, 12, 12, 7)],
        [(12, 12, 12, 1), (12, 12, 12, 5), (12, 12, 12, 10)],
        [(12, 12, 12, 2), (12, 12, 12, 5), (12, 12, 12, 8)],
        [(12, 12, 12, 0), (12, 12, 12, 6), (12, 12, 12, 8)],
        [(12, 12, 12, 4), (12, 12, 12, 7), (12, 12, 12, 11)],
    ]
    # Category 5: 2-3 bits at non-adjacent cells
    cat5 = [
        [(12, 12, 12, 0), (12, 13, 13, 1)],
        [(10, 10, 10, 6), (14, 14, 14, 9)],
        [(11, 11, 11, 0), (11, 11, 11, 4), (13, 13, 13, 1)],
        [(12, 10, 10, 2), (12, 14, 14, 3)],
        [(12, 12, 12, 0), (12, 12, 12, 1), (14, 14, 14, 2)],
    ]
    all_categories = [
        ("2adj_with_rest", cat1),
        ("2adj_both_prop", cat2),
        ("3adj_with_rest", cat3),
        ("3adj_all_prop", cat4),
        ("nonadjacent", cat5),
    ]
    return all_categories


def place_seed(grid, seed):
    for r, c, l, ch in seed:
        grid[r % L, c % L, l % L, ch] = 1


def center_of_mass_vectorized(grid):
    """Vectorized COM: grid shape (L,L,L,13) -> (com_l, com_r, com_c)."""
    counts = grid.sum(axis=3)  # (L,L,L)
    total = counts.sum()
    if total == 0:
        return 0.0, 0.0, 0.0
    l_arr = np.arange(L, dtype=np.float64).reshape(L, 1, 1)
    r_arr = np.arange(L, dtype=np.float64).reshape(1, L, 1)
    c_arr = np.arange(L, dtype=np.float64).reshape(1, 1, L)
    com_l = np.sum(counts * l_arr) / total
    com_r = np.sum(counts * r_arr) / total
    com_c = np.sum(counts * c_arr) / total
    return float(com_l), float(com_r), float(com_c)


def unwrap_delta(old_com, new_com):
    delta = np.array(new_com) - np.array(old_com)
    for i in range(3):
        if delta[i] > L / 2:
            delta[i] -= L
        elif delta[i] < -L / 2:
            delta[i] += L
    return delta


def bounding_extent_fast(grid):
    """Fast bounding extent using np.any and argwhere."""
    occupied = grid.sum(axis=3) > 0
    if not np.any(occupied):
        return 0, 0, 0
    coords = np.argwhere(occupied)
    return (int(coords[:, 0].max() - coords[:, 0].min()),
            int(coords[:, 1].max() - coords[:, 1].min()),
            int(coords[:, 2].max() - coords[:, 2].min()))


def run_simulation(lut, seed_bits, steps=STEPS):
    grid = np.zeros((L, L, L, 13), dtype=np.uint8)
    initial_bits = 0
    for r, c, l, ch in seed_bits:
        grid[r % L, c % L, l % L, ch] = 1
        initial_bits += 1

    old_com = center_of_mass_vectorized(grid)
    total_displacement = np.zeros(3, dtype=np.float64)

    rest_occupied_count = 0
    rest_empty_count = 0
    max_extent = (0, 0, 0)

    min_bits = initial_bits
    max_bits = initial_bits

    for _ in range(steps):
        grid = stream_13(grid)
        grid = collide_13(grid, lut)

        bc = int(grid.sum())
        if bc < min_bits:
            min_bits = bc
        if bc > max_bits:
            max_bits = bc

        # Rest channel occupancy (fast: sum the whole channel slice)
        rest_occ = int(grid[:, :, :, REST_CHANNEL].sum())
        if rest_occ > 0:
            rest_occupied_count += 1
        else:
            rest_empty_count += 1

        new_com = center_of_mass_vectorized(grid)
        delta = unwrap_delta(old_com, new_com)
        total_displacement += delta
        old_com = new_com

        ext = bounding_extent_fast(grid)
        if ext[0] > max_extent[0]:
            max_extent = ext

    final_bits = int(grid.sum())
    disp_norm = float(np.linalg.norm(total_displacement))
    bit_stability = 1.0 if final_bits == initial_bits else 0.0
    score = disp_norm * bit_stability

    return {
        "initial_bits": initial_bits,
        "final_bits": final_bits,
        "min_bits": min_bits,
        "max_bits": max_bits,
        "displacement_xyz": total_displacement.tolist(),
        "displacement_norm": disp_norm,
        "bit_stability": bit_stability,
        "score": score,
        "max_extent": list(max_extent),
        "rest_occupied_steps": rest_occupied_count,
        "rest_empty_steps": rest_empty_count,
        "rest_occupancy_fraction": rest_occupied_count / steps if steps > 0 else 0.0,
    }


def main():
    t_start = time.time()
    print("[search_13ch] Starting 13-channel search...")

    print("[search_13ch] Generating LUT variants...")
    sys.stdout.flush()
    all_luts, all_configs, meta = generate_all_lut_variants(
        max_variants=500, w3plus_seeds=2, verbose=False
    )
    print(f"[search_13ch] Generated {len(all_luts)} LUT variants in {time.time()-t_start:.1f}s")
    sys.stdout.flush()

    lut_indices = list(range(0, len(all_luts), 5))
    sampled_luts = [all_luts[i] for i in lut_indices]
    sampled_configs = [all_configs[i] for i in lut_indices]
    print(f"[search_13ch] Sampled {len(sampled_luts)} LUTs (every 5th).")
    sys.stdout.flush()

    categories = build_seeds()
    all_seeds = []
    for cat_name, cat_seeds in categories:
        for seed_idx, seed in enumerate(cat_seeds):
            seed_name = f"{cat_name}_s{seed_idx}"
            all_seeds.append((seed_name, seed, cat_name))
    print(f"[search_13ch] Defined {len(all_seeds)} seeds in {len(categories)} categories.")
    sys.stdout.flush()

    total_runs = len(sampled_luts) * len(all_seeds)
    print(f"[search_13ch] Total runs: {total_runs}")
    sys.stdout.flush()

    results = []
    successful_runs = 0
    nonzero_score_runs = 0
    propagating_runs = []

    run_start = time.time()

    for li, lut in enumerate(sampled_luts):
        lut_cfg = sampled_configs[li]
        for si, (seed_name, seed_bits, cat_name) in enumerate(all_seeds):
            run_idx = li * len(all_seeds) + si
            if run_idx % 500 == 0:
                elapsed = time.time() - run_start
                rate = elapsed / max(run_idx, 1)
                remaining = total_runs - run_idx
                eta = rate * remaining
                print(f"[search_13ch] Run {run_idx}/{total_runs} | {elapsed:.1f}s | ETA={eta:.1f}s")
                sys.stdout.flush()

            result = run_simulation(lut, seed_bits, steps=STEPS)
            result["lut_index"] = lut_indices[li]
            result["lut_config_variant"] = lut_cfg.get("variant_id", lut_indices[li])
            result["seed_name"] = seed_name
            result["category"] = cat_name

            if result["bit_stability"] > 0:
                successful_runs += 1
                if result["score"] > 0:
                    nonzero_score_runs += 1
                    propagating_runs.append({
                        "lut_index": lut_indices[li],
                        "seed_name": seed_name,
                        "score": result["score"],
                        "displacement_norm": result["displacement_norm"],
                        "displacement_xyz": result["displacement_xyz"],
                        "bits": result["final_bits"],
                    })

            results.append(result)

    total_time = time.time() - t_start

    propagating_runs.sort(key=lambda x: x["score"], reverse=True)

    print(f"\n[search_13ch] === SUMMARY ===")
    print(f"  Total LUTs tested:    {len(sampled_luts)}")
    print(f"  Total seeds:          {len(all_seeds)}")
    print(f"  Total runs:           {total_runs}")
    print(f"  Successful (stable):  {successful_runs}")
    print(f"  Non-zero score:       {nonzero_score_runs}")
    print(f"  Total time:           {total_time:.1f}s")
    sys.stdout.flush()

    if propagating_runs:
        print(f"\n  Top 5 propagating structures:")
        for r in propagating_runs[:5]:
            print(f"    LUT={r['lut_index']} seed={r['seed_name']} "
                  f"score={r['score']:.4f} disp={r['displacement_norm']:.4f} "
                  f"bits={r['bits']}")
    else:
        print("\n  No propagating structures discovered.")
    sys.stdout.flush()

    # Save results
    output = {
        "search_type": "13_channel_cooperative_trapping",
        "grid_size": L,
        "steps": STEPS,
        "n_luts_tested": len(sampled_luts),
        "n_seeds": len(all_seeds),
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "nonzero_score_runs": nonzero_score_runs,
        "total_time_seconds": total_time,
        "lut_generation_metadata": {
            "n_valid": meta.get("n_valid", 0),
            "n_attempted": meta.get("n_attempted", 0),
            "audit_pass_rate": meta.get("audit_pass_rate", 0),
            "generation_time_seconds": meta.get("generation_time_seconds", 0),
        },
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
    with open(out_dir / "search_results.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n[search_13ch] Results saved to {out_dir / 'search_results.json'}")
    sys.stdout.flush()


if __name__ == "__main__":
    main()
