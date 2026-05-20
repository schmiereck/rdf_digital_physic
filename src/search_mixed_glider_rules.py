#!/usr/bin/env python3
"""
iter_223 mixed-glider search.

Scans a curated set of evolved-rule JSON files for hex CA rules that support
BOTH a sub-light glider (v<c) AND a light-speed glider (v=1c).

Per-seed criteria (200-step simulation on a 128x128 hex grid):
  1. Bit count conserved: |final_bit_count - initial_bit_count| <= 1.
  2. Stable period detected and <= 20 (via detect_period over t in [150, 200]).
  3. Consistent velocity: std-dev of speed across 5 windows of length 40 < 0.05.
  4. Classification:
       - v<c glider:  0.1 <= mean_speed <= 0.9
       - v=1c glider: mean_speed > 0.9

Per-rule supports BOTH if at least one seed gives a v<c glider and at least
one (possibly different) seed gives a v=1c glider.

For each matching rule, head-on / intersecting collisions between a chosen
v<c glider and a chosen v=1c glider are run on a 128x128 grid for 300 steps
with row/column offsets in {-2,-1,0,1,2} (Glider 2's anchor). Bit counts
are tracked and the collision outcome is classified.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from probe_gliders_223 import (  # noqa: E402
    GRID_SIZE,
    STEPS,
    WINDOWS,
    WINDOW_LEN,
    STABLE_START,
    STABLE_END,
    MAX_PERIOD,
    canonical_active_cells,
    detect_period,
    generate_contiguous_seeds,
    rule_to_lut,
    step_grid,
    trigonometric_com_and_bits,
    unwrap_coms,
)


SOURCE_FILES = [
    "archive/iter_215/results/champion_rule.json",
    "archive/iter_215/results/final_population.json",
    "archive/iter_215/results/warm_start_population.json",
    "archive/iter_218/results/champion_rule.json",
    "archive/iter_218/results/champion_vc_rule.json",
    "archive/iter_221/results/champion_rule.json",
    "archive/iter_221/results/champion_rule_perfect.json",
    "archive/iter_221/results/champion_rule_unwrapped.json",
    "archive/iter_221/results/champion_vc_rule.json",
    "archive/iter_222/results/champion_rule_perfect.json",
]

RESULTS_DIR = PROJECT_ROOT / "archive" / "iter_223" / "results"
FOUND_PATH = RESULTS_DIR / "found_mixed_rules.json"
COLLISION_PATH = RESULTS_DIR / "mixed_collision_results.json"

VC_MIN = 0.1
VC_MAX = 0.9
C_MIN = 0.9  # strict > 0.9 in classification
VEL_STD_MAX = 0.05
BIT_TOL = 1
COLLISION_STEPS = 300
COLLISION_OFFSETS = [-2, -1, 0, 1, 2]
COLLISION_T = 60  # used to place the second glider so a meeting happens around t=T


# ---------------------------------------------------------------------------
# Rule extraction & standardization
# ---------------------------------------------------------------------------

def standardize_rule(rd: dict) -> dict[int, int]:
    """Standardize a rule_dict to {i: int} for i in 0..127, default identity."""
    out = {i: i for i in range(128)}
    for k, v in rd.items():
        ki = int(k)
        if 0 <= ki < 128:
            out[ki] = int(v)
    return out


def _walk_rule_dicts(obj):
    """Yield every dict that looks like a rule_dict (str(int)->int) inside obj."""
    if isinstance(obj, dict):
        # If this dict itself looks like a rule_dict, yield it.
        looks_like_rule = bool(obj) and all(
            (isinstance(k, str) and k.lstrip("-").isdigit()) or isinstance(k, int)
            for k in obj.keys()
        ) and all(isinstance(v, (int, float)) for v in obj.values())
        if looks_like_rule:
            yield obj
            return
        # Otherwise look for a rule_dict field, else recurse into values.
        if "rule_dict" in obj and isinstance(obj["rule_dict"], dict):
            yield obj["rule_dict"]
        # Also recurse to find nested rule_dicts in containers.
        for v in obj.values():
            yield from _walk_rule_dicts(v)
    elif isinstance(obj, list):
        for it in obj:
            yield from _walk_rule_dicts(it)


def load_rules_from_file(path: Path) -> list[dict[int, int]]:
    with open(path) as f:
        data = json.load(f)
    rules = []
    seen_local = set()
    for rd in _walk_rule_dicts(data):
        std = standardize_rule(rd)
        key = tuple(std[i] for i in range(128))
        if key in seen_local:
            continue
        seen_local.add(key)
        rules.append(std)
    return rules


def collect_all_rules(source_files: list[str]):
    """Returns (unique_rules, sources_per_rule) where the latter maps
    rule_key -> sorted list of source files where it was found."""
    sources_for_key: dict[tuple, list[str]] = {}
    rules_by_key: dict[tuple, dict[int, int]] = {}
    for rel in source_files:
        p = PROJECT_ROOT / rel
        if not p.exists():
            print(f"  [warn] missing file: {rel}")
            continue
        rs = load_rules_from_file(p)
        for r in rs:
            key = tuple(r[i] for i in range(128))
            if key not in rules_by_key:
                rules_by_key[key] = r
                sources_for_key[key] = []
            if rel not in sources_for_key[key]:
                sources_for_key[key].append(rel)
        print(f"  {rel}: extracted {len(rs)} unique rules")
    return rules_by_key, sources_for_key


# ---------------------------------------------------------------------------
# Glider classification
# ---------------------------------------------------------------------------

def simulate_seed_detailed(seed_cells, lut):
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in seed_cells:
        grid[(r + 64) % GRID_SIZE, (c + 64) % GRID_SIZE] = 1

    coms = []
    bit_counts = []
    canonical_history = []

    com, bits = trigonometric_com_and_bits(grid)
    coms.append(com)
    bit_counts.append(bits)
    canonical_history.append(canonical_active_cells(grid))

    for _ in range(STEPS):
        grid = step_grid(grid, lut)
        com, bits = trigonometric_com_and_bits(grid)
        coms.append(com)
        bit_counts.append(bits)
        canonical_history.append(canonical_active_cells(grid))

    unwrapped = unwrap_coms(coms)

    window_velocities = []
    for w in range(WINDOWS):
        start = w * WINDOW_LEN
        end = start + WINDOW_LEN
        sr, sc = unwrapped[start]
        er, ec = unwrapped[end]
        dr = er - sr
        dc = ec - sc
        v = float(np.sqrt(dr * dr + dc * dc) / WINDOW_LEN)
        window_velocities.append(v)
    velocity_std = float(np.std(window_velocities))

    net_dr = unwrapped[-1][0] - unwrapped[0][0]
    net_dc = unwrapped[-1][1] - unwrapped[0][1]
    mean_speed = float(np.sqrt(net_dr * net_dr + net_dc * net_dc) / STEPS)
    direction = (float(net_dr / STEPS), float(net_dc / STEPS))

    initial_bits = bit_counts[0]
    final_bits = bit_counts[-1]
    period = detect_period(canonical_history, bit_counts, STABLE_START, STABLE_END)

    is_bit_ok = (final_bits > 0) and (abs(final_bits - initial_bits) <= BIT_TOL)
    is_period_ok = (period is not None) and (period <= MAX_PERIOD)
    is_vel_ok = velocity_std < VEL_STD_MAX

    classification = None
    if is_bit_ok and is_period_ok and is_vel_ok:
        if mean_speed > C_MIN:
            classification = "v=1c glider"
        elif VC_MIN <= mean_speed <= VC_MAX:
            classification = "v<c glider"

    return {
        "initial_cells": [list(c) for c in seed_cells],
        "initial_bit_count": int(initial_bits),
        "final_bit_count": int(final_bits),
        "period": int(period) if period is not None else None,
        "mean_speed": mean_speed,
        "velocity_std": velocity_std,
        "window_velocities": window_velocities,
        "direction": direction,
        "n_cells": len(seed_cells),
        "classification": classification,
    }


def probe_rule(rule_dict, all_seeds):
    lut = rule_to_lut(rule_dict)
    vc_gliders = []
    c_gliders = []
    for seed in all_seeds:
        res = simulate_seed_detailed(seed, lut)
        if res["classification"] == "v<c glider":
            vc_gliders.append(res)
        elif res["classification"] == "v=1c glider":
            c_gliders.append(res)
    return vc_gliders, c_gliders


# ---------------------------------------------------------------------------
# Collision simulation
# ---------------------------------------------------------------------------

def simulate_collision(rule_dict, cells_a, cells_b, anchor_b, steps=COLLISION_STEPS):
    """Place glider A at center (anchor (64,64)) and glider B at anchor_b.
    Returns bit-count trajectory and final grid stats."""
    lut = rule_to_lut(rule_dict)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    ar, ac = 64, 64
    br, bc = anchor_b
    for r, c in cells_a:
        grid[(r + ar) % GRID_SIZE, (c + ac) % GRID_SIZE] = 1
    for r, c in cells_b:
        grid[(r + br) % GRID_SIZE, (c + bc) % GRID_SIZE] = 1

    initial_bits = int(grid.sum())
    bit_counts = [initial_bits]
    max_bits = initial_bits
    min_bits_after_overlap = None

    for t in range(steps):
        grid = step_grid(grid, lut)
        bits = int(grid.sum())
        bit_counts.append(bits)
        if bits > max_bits:
            max_bits = bits
        # tracking minimum once both have likely overlapped
        if t > 30:
            if min_bits_after_overlap is None or bits < min_bits_after_overlap:
                min_bits_after_overlap = bits

    final_bits = bit_counts[-1]
    return {
        "initial_bits": initial_bits,
        "final_bits": int(final_bits),
        "max_bits": int(max_bits),
        "min_bits_after_overlap": int(min_bits_after_overlap)
        if min_bits_after_overlap is not None
        else None,
        "bit_count_trajectory": bit_counts,
    }


def classify_collision(initial_bits, final_bits, max_bits):
    """Best-effort classification of collision outcome."""
    if final_bits == 0:
        return "annihilation"
    if max_bits > 4 * initial_bits:
        return "explosion"
    if final_bits == initial_bits:
        return "elastic_scatter_or_pass_through"
    if abs(final_bits - initial_bits) <= 1:
        return "near_elastic"
    if final_bits < initial_bits:
        return "inelastic_scatter_or_partial_annihilation"
    if final_bits > initial_bits:
        return "merge_growth_or_inelastic_creation"
    return "unknown"


def run_collisions_for_rule(rule_dict, vc_glider, c_glider):
    """Use the recorded direction vectors to position glider 2 so it intersects
    glider 1 near t=T, then sweep over small offsets."""
    cells_vc = [tuple(c) for c in vc_glider["initial_cells"]]
    cells_c = [tuple(c) for c in c_glider["initial_cells"]]

    # Direction = (dr/dt, dc/dt) for each glider at native phase.
    dr_a, dc_a = vc_glider["direction"]
    dr_b, dc_b = c_glider["direction"]

    # We want glider B's anchor to be such that they meet near t=COLLISION_T.
    # Position of glider A at time t: (64 + t*dr_a, 64 + t*dc_a).
    # Glider B starts at anchor_b and moves with (dr_b, dc_b).
    # We want them to meet, so:
    #   64 + T*dr_a ≈ br + T*dr_b  =>  br = 64 + T*(dr_a - dr_b)
    T = COLLISION_T
    br0 = int(round(64 + T * (dr_a - dr_b)))
    bc0 = int(round(64 + T * (dc_a - dc_b)))

    runs = []
    for d_r in COLLISION_OFFSETS:
        for d_c in COLLISION_OFFSETS:
            anchor_b = ((br0 + d_r) % GRID_SIZE, (bc0 + d_c) % GRID_SIZE)
            res = simulate_collision(rule_dict, cells_vc, cells_c, anchor_b)
            cls = classify_collision(res["initial_bits"], res["final_bits"], res["max_bits"])
            runs.append({
                "offset_dr": int(d_r),
                "offset_dc": int(d_c),
                "anchor_a": [64, 64],
                "anchor_b": [int(anchor_b[0]), int(anchor_b[1])],
                "initial_bits": res["initial_bits"],
                "final_bits": res["final_bits"],
                "max_bits": res["max_bits"],
                "min_bits_after_overlap": res["min_bits_after_overlap"],
                "classification": cls,
                # Subsample trajectory for storage (every 5 steps)
                "bit_count_subsample": res["bit_count_trajectory"][::5],
            })
    return runs


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating contiguous seeds...")
    seeds_3 = generate_contiguous_seeds(3)
    seeds_4 = generate_contiguous_seeds(4)
    all_seeds = seeds_3 + seeds_4
    print(f"  3-bit: {len(seeds_3)}, 4-bit: {len(seeds_4)} (total {len(all_seeds)})")

    print("\nLoading rules from sources...")
    rules_by_key, sources_for_key = collect_all_rules(SOURCE_FILES)
    print(f"\nTotal unique rules to probe: {len(rules_by_key)}")

    matches = []
    per_rule_summary = []
    for idx, (key, rule_dict) in enumerate(rules_by_key.items()):
        vc_gliders, c_gliders = probe_rule(rule_dict, all_seeds)
        has_vc = len(vc_gliders) > 0
        has_c = len(c_gliders) > 0
        per_rule_summary.append({
            "rule_idx": idx,
            "sources": sources_for_key[key],
            "n_vc": len(vc_gliders),
            "n_c": len(c_gliders),
            "supports_both": has_vc and has_c,
        })
        if has_vc and has_c:
            # Pick "best" gliders: smallest velocity_std (most stable), then smallest n_cells.
            def sort_key(g):
                return (g["velocity_std"], g["n_cells"])
            vc_sorted = sorted(vc_gliders, key=sort_key)
            c_sorted = sorted(c_gliders, key=sort_key)
            matches.append({
                "rule_idx": idx,
                "rule_dict": {str(k): int(v) for k, v in rule_dict.items()},
                "sources": sources_for_key[key],
                "vc_gliders": vc_gliders,
                "c_gliders": c_gliders,
                "vc_chosen": vc_sorted[0],
                "c_chosen": c_sorted[0],
            })
            print(f"  [MATCH] rule #{idx}  vc={len(vc_gliders)}  c={len(c_gliders)}  "
                  f"sources={sources_for_key[key]}")

    print("\n" + "=" * 70)
    print(f"Rules supporting BOTH v<c AND v=1c gliders: {len(matches)}")
    print("=" * 70)

    # Always write the found-rules file (even empty so downstream sees an artifact).
    found_payload = {
        "criteria": {
            "grid_size": GRID_SIZE,
            "steps": STEPS,
            "bit_count_tolerance": BIT_TOL,
            "max_period": MAX_PERIOD,
            "vel_std_max": VEL_STD_MAX,
            "vc_speed_range": [VC_MIN, VC_MAX],
            "c_speed_min": C_MIN,
        },
        "sources_scanned": SOURCE_FILES,
        "num_unique_rules": len(rules_by_key),
        "num_matches": len(matches),
        "matches": matches,
        "per_rule_summary": per_rule_summary,
    }
    with open(FOUND_PATH, "w") as f:
        json.dump(found_payload, f, indent=2)
    print(f"\nWritten: {FOUND_PATH.relative_to(PROJECT_ROOT)}")

    # ── Detailed match report ───────────────────────────────────────────
    if matches:
        print("\n--- Match details ---")
        for m in matches:
            print(f"\nRule #{m['rule_idx']}")
            print(f"  sources: {m['sources']}")
            vc = m["vc_chosen"]
            cc = m["c_chosen"]
            print(f"  v<c glider chosen: cells={vc['initial_cells']} "
                  f"speed={vc['mean_speed']:.4f} std={vc['velocity_std']:.4f} "
                  f"period={vc['period']} dir={vc['direction']} "
                  f"bits={vc['initial_bit_count']}->{vc['final_bit_count']}")
            print(f"  v=1c glider chosen: cells={cc['initial_cells']} "
                  f"speed={cc['mean_speed']:.4f} std={cc['velocity_std']:.4f} "
                  f"period={cc['period']} dir={cc['direction']} "
                  f"bits={cc['initial_bit_count']}->{cc['final_bit_count']}")
    else:
        print("\n(no rules supporting both glider types found in scanned files)")

    # ── Collisions ──────────────────────────────────────────────────────
    collision_results = []
    if matches:
        print("\n=== Running collisions ===")
        for m in matches:
            rule_dict = {int(k): int(v) for k, v in m["rule_dict"].items()}
            runs = run_collisions_for_rule(rule_dict, m["vc_chosen"], m["c_chosen"])
            collision_results.append({
                "rule_idx": m["rule_idx"],
                "sources": m["sources"],
                "vc_glider": m["vc_chosen"],
                "c_glider": m["c_chosen"],
                "runs": runs,
            })
            cls_counts: dict[str, int] = {}
            for r in runs:
                cls_counts[r["classification"]] = cls_counts.get(r["classification"], 0) + 1
            print(f"\nRule #{m['rule_idx']}  outcome counts over {len(runs)} offsets:")
            for k, v in cls_counts.items():
                print(f"  {k}: {v}")
            # Show one row of details
            print("  sample runs (first 5):")
            for r in runs[:5]:
                print(f"    offs=({r['offset_dr']:+d},{r['offset_dc']:+d}) "
                      f"bits {r['initial_bits']}->{r['final_bits']} "
                      f"max={r['max_bits']} min(t>30)={r['min_bits_after_overlap']} "
                      f"-> {r['classification']}")

    collisions_payload = {
        "criteria": {
            "grid_size": GRID_SIZE,
            "collision_steps": COLLISION_STEPS,
            "offsets": COLLISION_OFFSETS,
            "collision_T": COLLISION_T,
        },
        "num_rules": len(collision_results),
        "results": collision_results,
    }
    with open(COLLISION_PATH, "w") as f:
        json.dump(collisions_payload, f, indent=2)
    print(f"\nWritten: {COLLISION_PATH.relative_to(PROJECT_ROOT)}")

    print("\n=== SUMMARY ===")
    print(f"unique_rules_scanned: {len(rules_by_key)}")
    print(f"rules_with_both_gliders: {len(matches)}")
    if matches:
        for m in matches:
            print(f"  - rule#{m['rule_idx']}  sources={m['sources']}")
    print(f"collision_runs_total: {sum(len(c['runs']) for c in collision_results)}")


if __name__ == "__main__":
    sys.exit(main() or 0)
