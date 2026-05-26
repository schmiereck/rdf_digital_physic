#!/usr/bin/env python3
"""
test_interplane_coupling.py - Inter-plane coupling falsification test.

Implements deterministic integer coupling between [111] hex plane and
inter-plane channels. Tests whether 3D binding emerges while preserving
glider stability, per pre_registration.md Sections 5-6.

Falsification:
- F4a: multi-layer state is non-interacting composite
- F4b: coupled state disperses under localized latency perturbation
- F4c: no stable configuration survives >=300 steps for any alpha > 0
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, LTROMINO_CELLS, center_of_mass
from fcc_engine_embed import embed_step, make_3d_seed

GRID = 32
STEPS = 300
CENTER = GRID // 2
CHAMPION = PROJECT_ROOT / "archive" / "iter_222" / "results" / "champion_rule_perfect.json"
OUTDIR = PROJECT_ROOT / "archive" / "iter_252" / "results"


def load_champion():
    with open(CHAMPION, "r") as f:
        data = json.load(f)
    rule_dict = {int(k): int(v) for k, v in data["rule_dict"].items()}
    return rule_dict_to_lut(rule_dict), data.get("seed_cells", LTROMINO_CELLS)


def com_on_layer(grid, layer):
    bits = grid[layer, :, :, 12]
    ys, xs = np.where(bits > 0)
    if len(ys) == 0:
        return None
    return (float(np.mean(ys)), float(np.mean(xs)))


def unwrap_series(pts, size):
    if not pts or pts[0] is None:
        return []
    u = [[float(pts[0][0]), float(pts[0][1])]]
    for i in range(1, len(pts)):
        if pts[i] is None:
            u.append([u[-1][0], u[-1][1]])
            continue
        dr = float(pts[i][0]) - float(pts[i - 1][0])
        dc = float(pts[i][1]) - float(pts[i - 1][1])
        if dr > size / 2:
            dr -= size
        elif dr < -size / 2:
            dr += size
        if dc > size / 2:
            dc -= size
        elif dc < -size / 2:
            dc += size
        u.append([u[-1][0] + dr, u[-1][1] + dc])
    return u


def run_coupled(hex_lut, seed_cells, alpha, config_id, with_latency=False):
    configs = [
        {"layers": [CENTER], "inter": []},
        {"layers": [CENTER - 1], "inter": []},
        {"layers": [CENTER + 1], "inter": []},
        {"layers": [CENTER - 2], "inter": []},
        {"layers": [CENTER - 1, CENTER + 1], "inter": []},
        {"layers": [CENTER - 2, CENTER + 2], "inter": []},
        {"layers": [CENTER, CENTER - 2], "inter": []},
        {"layers": [CENTER], "inter": [(CENTER, 6)]},
        {"layers": [CENTER], "inter": [(CENTER, 6), (CENTER, 7)]},
        {"layers": [CENTER], "inter": [(CENTER, 6), (CENTER, 7), (CENTER, 8)]},
    ]
    cfg = configs[config_id]
    grid = np.zeros((GRID, GRID, GRID, 13), dtype=np.uint8)
    off_r = CENTER - 64
    off_c = CENTER - 64
    seed_3d = [(r + off_r, c + off_c) for r, c in seed_cells]

    for ly in cfg["layers"]:
        for r, c in seed_3d:
            grid[ly, r, c, 12] = 1
    for ly, ch in cfg["inter"]:
        for r, c in seed_3d[:1]:
            grid[ly, r, c, ch] = 1

    orig_layers = set(cfg["layers"])
    bits_per_layer = []
    coms = []
    max_bits_other = 0
    survived = False

    for step in range(STEPS + 1):
        layer_counts = [int(grid[l, :, :, 12].sum()) for l in range(GRID)]
        bits_per_layer.append(layer_counts)
        other = sum(1 for l in range(GRID) if l not in orig_layers and layer_counts[l] > 0)
        max_bits_other = max(max_bits_other, other)

        dom = max(range(GRID), key=lambda l: layer_counts[l])
        coms.append(com_on_layer(grid, dom))

        if step == STEPS:
            survived = layer_counts[dom] >= 3
            break

        if with_latency:
            new_grid = embed_step(grid, hex_lut, alpha)
            if coms[-1] is not None:
                cy, cx = int(round(coms[-1][0])), int(round(coms[-1][1]))
                ly = dom
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        for dl in (-1, 0, 1):
                            ry = (cy + dy) % GRID
                            rx = (cx + dx) % GRID
                            rl = (ly + dl) % GRID
                            new_grid[rl, ry, rx, 12] = grid[rl, ry, rx, 12]
            grid = new_grid
        else:
            grid = embed_step(grid, hex_lut, alpha)

    uw = unwrap_series(coms, GRID)
    disp = 0.0
    if len(uw) > 1:
        disp = math.hypot(uw[-1][0] - uw[0][0], uw[-1][1] - uw[0][1])

    return {
        "survived": survived,
        "displacement": disp,
        "max_bits_other_layers": max_bits_other,
        "final_bits_dominant_layer": bits_per_layer[-1][dom] if coms[-1] else 0,
        "bits_per_layer": bits_per_layer,
    }


def run_decomposition(hex_lut, seed_cells, config_id):
    if config_id not in (4, 5, 6):
        return None
    layers = [
        [CENTER - 1, CENTER + 1],
        [CENTER - 2, CENTER + 2],
        [CENTER, CENTER - 2],
    ][config_id - 4]
    off_r = CENTER - 64
    off_c = CENTER - 64
    seed_3d = [(r + off_r, c + off_c) for r, c in seed_cells]
    results = []
    for ly in layers:
        grid = np.zeros((GRID, GRID, GRID, 13), dtype=np.uint8)
        for r, c in seed_3d:
            grid[ly, r, c, 12] = 1
        for _ in range(STEPS):
            grid = embed_step(grid, hex_lut, alpha=0)
        final = int(grid[ly, :, :, 12].sum())
        results.append({"layer": ly, "final_bits": final, "survived": final >= 3})
    all_survive = all(r["survived"] for r in results)
    return {"results": results, "all_survive": all_survive, "f4a_triggered": all_survive}


def main():
    print("=" * 70)
    print("ITER 252.3 - INTER-PLANE COUPLING FALSIFICATION TEST")
    print("=" * 70)

    hex_lut, seed_cells = load_champion()
    OUTDIR.mkdir(parents=True, exist_ok=True)

    summary = {"alpha_runs": [], "f4a": False, "f4b": False, "f4c": True}

    for alpha in range(4):
        print(f"\n[alpha={alpha}] Running 10 configurations x {STEPS} steps...")
        alpha_results = []
        any_survived = False

        for cfg in range(10):
            normal = run_coupled(hex_lut, seed_cells, alpha, cfg, with_latency=False)
            latency = None
            if cfg == 0:
                latency = run_coupled(hex_lut, seed_cells, alpha, cfg, with_latency=True)
                if normal["survived"] and not latency["survived"]:
                    summary["f4b"] = True

            decomp = run_decomposition(hex_lut, seed_cells, cfg)
            if decomp and decomp.get("f4a_triggered"):
                summary["f4a"] = True

            if normal["survived"]:
                any_survived = True

            alpha_results.append({
                "config": cfg,
                "normal": normal,
                "latency": latency,
                "decomposition": decomp,
            })
            print(f"  cfg {cfg}: disp={normal['displacement']:.2f} "
                  f"survived={normal['survived']} other_layers={normal['max_bits_other_layers']}")

        summary["alpha_runs"].append({
            "alpha": alpha,
            "any_survived": any_survived,
            "runs": alpha_results,
        })

        if alpha > 0 and any_survived:
            summary["f4c"] = False

    out_path = OUTDIR / "coupling_test.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSaved -> {out_path}")

    print("\n" + "=" * 70)
    print("FALSIFICATION SUMMARY")
    print("=" * 70)
    print(f"  F4a (non-interacting composite): {summary['f4a']}")
    print(f"  F4b (disperses under latency):   {summary['f4b']}")
    print(f"  F4c (no survival for alpha>0):   {summary['f4c']}")
    if summary["f4a"] or summary["f4b"] or summary["f4c"]:
        print("\n  CONCLUSION: Coupling hypothesis REFUTED (at least one F4 criterion holds).")
    else:
        print("\n  CONCLUSION: Coupling hypothesis NOT REFuted by tested criteria.")
    print("  NOTE: This is an anisotropic 2.5D system; any 3D binding is")
    print("  specific to the privileged [111] plane family.")


if __name__ == "__main__":
    main()
