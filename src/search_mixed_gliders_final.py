#!/usr/bin/env python3
import json
import sys
import time
from pathlib import Path
import numpy as np

GRID_SIZE = 128
STEPS = 200
WINDOWS = 5
WINDOW_LEN = STEPS // WINDOWS  # 40
STABLE_START = 150
STABLE_END = 200
MAX_PERIOD = 20

HEX_DIRS = [
    ( 1,  0),  # E
    ( 1, -1),  # SE
    ( 0, -1),  # SW
    (-1,  0),  # W
    (-1,  1),  # NW
    ( 0,  1),  # NE
]


def canonical_translate(cells):
    """Translate cells so that the lexicographically smallest cell is at (0,0)."""
    sorted_cells = sorted(cells)
    r0, c0 = sorted_cells[0]
    return tuple((r - r0, c - c0) for r, c in sorted_cells)


def generate_contiguous_seeds(n_cells: int) -> list[tuple]:
    """All contiguous n-cell hex polyominoes under translation-only canonical form."""
    seeds = {canonical_translate([(0, 0)])}
    for _ in range(n_cells - 1):
        new_seeds = set()
        for shape in seeds:
            shape_set = set(shape)
            for cell in shape:
                for dr, dc in HEX_DIRS:
                    nb = (cell[0] + dr, cell[1] + dc)
                    if nb in shape_set:
                        continue
                    new_shape = list(shape) + [nb]
                    new_seeds.add(canonical_translate(new_shape))
        seeds = new_seeds
    return sorted(seeds)


def trigonometric_com_and_bits(grid: np.ndarray) -> tuple[tuple[float, float], int]:
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    grid_size = GRID_SIZE
    twopi = 2.0 * np.pi
    a_r = twopi * rows.astype(float) / grid_size
    com_r = (np.arctan2(np.sin(a_r).mean(), np.cos(a_r).mean()) % twopi) * grid_size / twopi
    a_c = twopi * cols.astype(float) / grid_size
    com_c = (np.arctan2(np.sin(a_c).mean(), np.cos(a_c).mean()) % twopi) * grid_size / twopi
    return (float(com_r), float(com_c)), int(grid.sum())


def unwrap_coms(coms):
    unwrapped = [coms[0]]
    for i in range(1, len(coms)):
        prev_com = coms[i - 1]
        cur_com = coms[i]
        dx = cur_com[0] - prev_com[0]
        dy = cur_com[1] - prev_com[1]
        if dx > 64:
            dx -= 128.0
        elif dx < -64:
            dx += 128.0
        if dy > 64:
            dy -= 128.0
        elif dy < -64:
            dy += 128.0
        last = unwrapped[-1]
        unwrapped.append((last[0] + dx, last[1] + dy))
    return unwrapped


def canonical_active_cells(grid: np.ndarray) -> tuple:
    """Toroidal canonical form: relative positions to first cell with ±64
    wraparound, then re-translated so the (toroidally) lex-min cell is at (0,0)."""
    rows, cols = np.where(grid > 0)
    if len(rows) == 0:
        return tuple()
    half = GRID_SIZE // 2
    r0_abs = int(rows[0])
    c0_abs = int(cols[0])
    rel = []
    for r, c in zip(rows.tolist(), cols.tolist()):
        dr = int(r) - r0_abs
        if dr > half:
            dr -= GRID_SIZE
        elif dr < -half:
            dr += GRID_SIZE
        dc = int(c) - c0_abs
        if dc > half:
            dc -= GRID_SIZE
        elif dc < -half:
            dc += GRID_SIZE
        rel.append((dr, dc))
    rel.sort()
    rmin, cmin = rel[0]
    return tuple((r - rmin, c - cmin) for r, c in rel)


def detect_period(canonical_history, bit_counts, t_start: int, t_end: int):
    for p in range(1, MAX_PERIOD + 1):
        ok = True
        for t in range(t_start, t_end - p + 1):
            if canonical_history[t] != canonical_history[t + p]:
                ok = False
                break
            if bit_counts[t] != bit_counts[t + p]:
                ok = False
                break
        if ok:
            return p
    return None


def step_grid(grid: np.ndarray, lut: np.ndarray) -> np.ndarray:
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


def rule_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)


def extract_rules_from_json(data):
    rules = []
    if isinstance(data, dict):
        if "rule_dict" in data:
            rules.append(data["rule_dict"])
        for k, v in data.items():
            if k in ["population", "warm_start_population"] and isinstance(v, list):
                for item in v:
                    rules.extend(extract_rules_from_json(item))
            elif isinstance(v, (dict, list)):
                rules.extend(extract_rules_from_json(v))
    elif isinstance(data, list):
        for item in data:
            rules.extend(extract_rules_from_json(item))
    return rules


def standardize_rule(rule_dict: dict) -> dict:
    """Convert rule to a standard dictionary with keys 0..127 and values as integers, defaulting to identity."""
    return {i: int(rule_dict.get(str(i), rule_dict.get(i, i))) for i in range(128)}


def simulate_seed_fast(seed_cells, lut):
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
    for r, c in seed_cells:
        grid[(r + 64) % GRID_SIZE, (c + 64) % GRID_SIZE] = 1

    initial_bits = len(seed_cells)
    
    # 1. Fast check: just step and check bit count
    grids = [grid.copy()]
    for t in range(1, STEPS + 1):
        grid = step_grid(grid, lut)
        if int(grid.sum()) != initial_bits:
            return None
        grids.append(grid.copy())
        
    # 2. If it survives, do the heavy computation
    coms = []
    bit_counts = []
    canonical_history = []
    for g in grids:
        com, bits = trigonometric_com_and_bits(g)
        coms.append(com)
        bit_counts.append(bits)
        canonical_history.append(canonical_active_cells(g))
        
    # If we got here, we have perfect bit conservation!
    unwrapped = unwrap_coms(coms)
    
    # Per-window velocity magnitudes
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

    # Mean speed = |net displacement| / 200
    net_dr = unwrapped[-1][0] - unwrapped[0][0]
    net_dc = unwrapped[-1][1] - unwrapped[0][1]
    mean_speed = float(np.sqrt(net_dr * net_dr + net_dc * net_dc) / STEPS)

    period = detect_period(canonical_history, bit_counts, STABLE_START, STABLE_END)
    
    if period is None:
        return {
            "initial_cells": [list(c) for c in seed_cells],
            "initial_bit_count": initial_bits,
            "final_bit_count": initial_bits,
            "period": None,
            "mean_speed": mean_speed,
            "velocity_std": velocity_std,
            "classification": "chaotic/unstable"
        }
        
    classification = None
    if 0.1 <= mean_speed <= 0.9:
        classification = "v<c glider"
    elif mean_speed >= 0.95:
        classification = "v=1c glider"
    else:
        classification = "other"
        
    return {
        "initial_cells": [list(c) for c in seed_cells],
        "initial_bit_count": initial_bits,
        "final_bit_count": initial_bits,
        "period": period,
        "mean_speed": mean_speed,
        "velocity_std": velocity_std,
        "classification": classification
    }


def main():
    print("========================================================================")
    print("SEARCHING FOR MIXED GLIDER RULES (v<c AND v=1c UNDER SAME RULE)")
    print("========================================================================")
    
    # 1. Scan for JSON files
    archive_dir = Path("archive")
    target_iters = ["iter_215", "iter_218", "iter_221", "iter_222"]
    
    # We will collect files in target directories, and any other results folders under archive.
    target_files = []
    other_files = []
    
    all_results_dirs = sorted(list(archive_dir.glob("**/results")))
    
    for rdir in all_results_dirs:
        # Check if this results dir is in our main targets or not
        is_target = any(t in rdir.parts for t in target_iters)
        json_files = sorted(list(rdir.glob("*.json")))
        if is_target:
            target_files.extend(json_files)
        else:
            other_files.extend(json_files)
            
    all_files_to_scan = target_files + other_files
    # Deduplicate paths (absolute)
    seen_paths = set()
    deduped_files = []
    for f in all_files_to_scan:
        f_res = f.resolve()
        if f_res not in seen_paths:
            seen_paths.add(f_res)
            deduped_files.append(f)
            
    print(f"Total results JSON files discovered: {len(deduped_files)}")
    print(f"  - Target directory files ({', '.join(target_iters)}): {len(target_files)}")
    print(f"  - Other results directories files: {len(deduped_files) - len(target_files)}")
    print("\nList of all scanned files:")
    for i, f in enumerate(deduped_files, 1):
        print(f"  [{i:03d}] {f}")
        
    # 2. Extract and standardize rules
    unique_rules = {}  # tuple_representation -> {"rule_dict": std_dict, "files": set()}
    
    print("\nExtracting and standardizing rules...")
    for f in deduped_files:
        try:
            with open(f) as fh:
                data = json.load(fh)
            extracted = extract_rules_from_json(data)
            for r in extracted:
                std_dict = standardize_rule(r)
                std_tuple = tuple(std_dict[i] for i in range(128))
                if std_tuple not in unique_rules:
                    unique_rules[std_tuple] = {
                        "rule_dict": std_dict,
                        "files": set()
                    }
                unique_rules[std_tuple]["files"].add(str(f))
        except Exception as e:
            print(f"  [ERROR] Failed to read or parse {f}: {e}")
            
    print(f"\nExtracted {len(unique_rules)} unique rules from all files.")
    
    # 3. Generate seeds
    print("\nGenerating contiguous 3-bit and 4-bit seeds...")
    seeds_3 = generate_contiguous_seeds(3)
    seeds_4 = generate_contiguous_seeds(4)
    all_seeds = seeds_3 + seeds_4
    print(f"  -> Generated {len(seeds_3)} 3-bit seeds and {len(seeds_4)} 4-bit seeds. Total = {len(all_seeds)} seeds.")
    
    # 4. Simulate each rule
    print("\nSimulating rules on all seeds with early exit optimization...")
    start_time = time.time()
    
    mixed_rules_found = []
    
    for rule_idx, (std_tuple, rule_info) in enumerate(unique_rules.items(), 1):
        rule_dict = rule_info["rule_dict"]
        lut = rule_to_lut(rule_dict)
        
        vc_gliders = []
        c_gliders = []
        
        for seed in all_seeds:
            res = simulate_seed_fast(seed, lut)
            if res is not None:
                # Valid result with perfect bit conservation
                if res["classification"] == "v<c glider":
                    vc_gliders.append(res)
                elif res["classification"] == "v=1c glider":
                    c_gliders.append(res)
                    
        if len(vc_gliders) > 0 and len(c_gliders) > 0:
            mixed_rules_found.append({
                "rule_tuple": std_tuple,
                "rule_info": rule_info,
                "vc_gliders": vc_gliders,
                "c_gliders": c_gliders
            })
            
    elapsed_time = time.time() - start_time
    print(f"Simulation of all {len(unique_rules)} rules completed in {elapsed_time:.2f} seconds!")
    
    # 5. Summary / Findings Report
    print("\n" + "=" * 80)
    print("FINDINGS SUMMARY")
    print("=" * 80)
    print(f"Total unique rules analyzed: {len(unique_rules)}")
    print(f"Number of rules supporting BOTH v<c and v=1c gliders: {len(mixed_rules_found)}")
    print("-" * 80)
    
    if len(mixed_rules_found) == 0:
        print("No rules supporting both v<c and v=1c gliders were found.")
    else:
        for idx, mr in enumerate(mixed_rules_found, 1):
            rule_info = mr["rule_info"]
            files = sorted(list(rule_info["files"]))
            print(f"\n[Mixed Rule #{idx}]")
            print(f"  Found in files:")
            for f in files:
                print(f"    - {f}")
            
            # Print a compact version of the rule dict or a few representative values
            # (since printing all 128 keys can be long, let's print first 10 mappings and number of total mappings)
            total_non_identity = sum(1 for k, v in rule_info["rule_dict"].items() if k != v)
            print(f"  Rule dict stats: {total_non_identity} non-identity mappings out of 128.")
            print(f"  Standard Rule Tuple (first 16 entries): {mr['rule_tuple'][:16]}...")
            
            print(f"  Stable v<c gliders found ({len(mr['vc_gliders'])} seeds):")
            for g in mr['vc_gliders'][:5]:
                print(f"    - Seed cells: {g['initial_cells']} | Period: {g['period']} | Mean Speed: {g['mean_speed']:.4f} | Volatility Std: {g['velocity_std']:.4f}")
            if len(mr['vc_gliders']) > 5:
                print(f"    - ... and {len(mr['vc_gliders']) - 5} more.")
                
            print(f"  Stable v=1c gliders found ({len(mr['c_gliders'])} seeds):")
            for g in mr['c_gliders'][:5]:
                print(f"    - Seed cells: {g['initial_cells']} | Period: {g['period']} | Mean Speed: {g['mean_speed']:.4f} | Volatility Std: {g['velocity_std']:.4f}")
            if len(mr['c_gliders']) > 5:
                print(f"    - ... and {len(mr['c_gliders']) - 5} more.")
                
    print("\nDone!")


if __name__ == "__main__":
    main()
