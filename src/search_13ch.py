#!/usr/bin/env python3
"""
search_13ch.py — 13-channel FCC LGCA search with cooperative-trapping LUTs.
OPTIMIZED: Sparse COM, sparse torus bounding box, uint8/uint16 throughout.
"""

from __future__ import annotations
import json
import sys
import time
import numpy as np
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(SCRIPT_DIR))

from fcc_engine_13ch import stream_13, collide_13
from cooperative_lut_13ch import generate_all_lut_variants

L = 24
STEPS = 300
REST_CHANNEL = 12


def center_of_mass_circular_sparse(grid):
    """Sparse circular-mean COM for toroidal grid. Grid shape (L,L,L,C)."""
    coords = np.argwhere(grid)  # shape (N, 4)
    if len(coords) == 0:
        return 0.0, 0.0, 0.0
    
    theta = 2 * np.pi / L
    coms = np.zeros(3)
    for axis in range(3):
        vals = coords[:, axis]
        x = np.cos(vals * theta).sum()
        y = np.sin(vals * theta).sum()
        coms[axis] = (L * np.arctan2(y, x) / (2 * np.pi)) % L
    return float(coms[0]), float(coms[1]), float(coms[2])


def bounding_extent_sparse(grid):
    """Mathematically exact sparse torus bounding box."""
    coords = np.argwhere(grid)
    if len(coords) == 0:
        return 0, 0, 0
    extents = []
    for axis in range(3):
        unique_vals = np.unique(coords[:, axis])
        if len(unique_vals) <= 1:
            extents.append(0)
            continue
        unique_vals = np.sort(unique_vals)
        gaps = np.diff(unique_vals)
        wrap_gap = L - (unique_vals[-1] - unique_vals[0])
        max_gap = max(gaps.max(), wrap_gap)
        extents.append(L - max_gap)
    return tuple(extents)


# ─── Seed definitions ───────────────────────────────────────────────────────

def build_seeds():
    seeds = []
    cat1 = [
        [(12, 12, 12, 0), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 1), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 2), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 4), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 6), (12, 12, 12, REST_CHANNEL)],
    ]
    cat2 = [
        [(12, 12, 12, 0), (12, 12, 12, 4)],
        [(12, 12, 12, 0), (12, 12, 12, 1)],
        [(12, 12, 12, 2), (12, 12, 12, 4)],
        [(12, 12, 12, 6), (12, 12, 12, 7)],
        [(12, 12, 12, 8), (12, 12, 12, 2)],
    ]
    cat3 = [
        [(12, 12, 12, 0), (12, 12, 12, 4), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 1), (12, 12, 12, 5), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 2), (12, 12, 12, 6), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 0), (12, 12, 12, 2), (12, 12, 12, REST_CHANNEL)],
        [(12, 12, 12, 6), (12, 12, 12, 7), (12, 12, 12, REST_CHANNEL)],
    ]
    cat4 = [
        [(12, 12, 12, 0), (12, 12, 12, 4), (12, 12, 12, 7)],
        [(12, 12, 12, 1), (12, 12, 12, 5), (12, 12, 12, 10)],
        [(12, 12, 12, 2), (12, 12, 12, 5), (12, 12, 12, 8)],
        [(12, 12, 12, 0), (12, 12, 12, 6), (12, 12, 12, 8)],
        [(12, 12, 12, 4), (12, 12, 12, 7), (12, 12, 12, 11)],
    ]
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


def unwrap_delta(old_com, new_com):
    delta = np.array(new_com) - np.array(old_com)
    for i in range(3):
        if delta[i] > L / 2:
            delta[i] -= L
        elif delta[i] < -L / 2:
            delta[i] += L
    return delta


# Pre-build seed grids to avoid repeated initialization
def prebuild_seed_grids(all_seeds):
    """Build seed grids ahead of time. Returns list of (name, grid, initial_bits, cat)."""
    prebuilt = []
    for seed_name, seed_bits, cat_name in all_seeds:
        grid = np.zeros((L, L, L, 13), dtype=np.uint8)
        initial_bits = 0
        for r, c, l, ch in seed_bits:
            grid[r % L, c % L, l % L, ch] = 1
            initial_bits += 1
        prebuilt.append((seed_name, grid, initial_bits, cat_name))
    return prebuilt


def run_simulation(lut, seed_grid, initial_bits, steps=STEPS):
    grid = seed_grid.copy()
    
    old_com = center_of_mass_circular_sparse(grid)
    total_displacement = np.zeros(3, dtype=np.float64)

    rest_occupied_count = 0
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

        # Rest channel occupancy using sparse check
        rest_occ = int(grid[:, :, :, REST_CHANNEL].sum())
        if rest_occ > 0:
            rest_occupied_count += 1

        new_com = center_of_mass_circular_sparse(grid)
        delta = unwrap_delta(old_com, new_com)
        total_displacement += delta
        old_com = new_com

        ext = bounding_extent_sparse(grid)
        if ext[0] > max_extent[0]:
            max_extent = ext
        if ext[1] > max_extent[1]:
            max_extent = (max_extent[0], ext[1], max_extent[2])
        if ext[2] > max_extent[2]:
            max_extent = (max_extent[0], max_extent[1], ext[2])

    final_bits = int(grid.sum())
    disp_norm = float(np.linalg.norm(total_displacement))
    bit_stability = 1.0 if final_bits == initial_bits else 0.0
    score = disp_norm * bit_stability
    rest_empty_count = steps - rest_occupied_count

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
    print("[search_13ch] Starting 13-channel optimized search...")

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
    
    # Prebuild seed grids
    prebuilt = prebuild_seed_grids(all_seeds)
    print(f"[search_13ch] Prebuilt {len(prebuilt)} seed grids.")
    sys.stdout.flush()

    total_runs = len(sampled_luts) * len(prebuilt)
    print(f"[search_13ch] Total runs: {total_runs}")
    sys.stdout.flush()

    results = []
    successful_runs = 0
    nonzero_score_runs = 0
    propagating_runs = []

    run_start = time.time()

    for li, lut in enumerate(sampled_luts):
        lut_cfg = sampled_configs[li]
        for si, (seed_name, seed_grid, initial_bits, cat_name) in enumerate(prebuilt):
            run_idx = li * len(prebuilt) + si
            if run_idx % 500 == 0:
                elapsed = time.time() - run_start
                rate = elapsed / max(run_idx, 1)
                remaining = total_runs - run_idx
                eta = rate * remaining
                print(f"[search_13ch] Run {run_idx}/{total_runs} | {elapsed:.1f}s | ETA={eta:.1f}s")
                sys.stdout.flush()

            result = run_simulation(lut, seed_grid, initial_bits, steps=STEPS)
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
    print(f"  Total seeds:          {len(prebuilt)}")
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

    output = {
        "search_type": "13_channel_cooperative_trapping",
        "grid_size": L,
        "steps": STEPS,
        "n_luts_tested": len(sampled_luts),
        "n_seeds": len(prebuilt),
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

    for cat_name in ["2adj_with_rest", "2adj_both_prop", "3adj_with_rest", "3adj_all_prop", "nonadjacent"]:
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

    return propagating_runs, results


if __name__ == "__main__":
    main()
