#!/usr/bin/env python3
"""
generate_and_test_hybrid_rule.py  (iter_116)

Two-phase experiment:
  Part 1 – Generate a single C2-symmetric, reversible, non-conserving rule
            from two distinct kernel-pair pools (cooling + glider/birth).
  Part 2 – Evaluate that rule on (A) soup resolution and (B) glider search.
  Part 3 – Write archive/iter_116/result.yaml.

MSB encoding: center=bit6, E=bit5, SE=bit4, SW=bit3, W=bit2, NW=bit1, NE=bit0
"""

from __future__ import annotations

import json
import math
import random
import sys
import traceback
from itertools import combinations
from pathlib import Path

import numpy as np
import yaml

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS_DIR  = PROJECT_ROOT / "archive" / "iter_116" / "results"
RULE_JSON    = RESULTS_DIR / "hybrid_rule.json"
RESULT_YAML  = PROJECT_ROOT / "archive" / "iter_116" / "result.yaml"

GRID_SIZE    = 150
DENSITY      = 0.25
SOUP_STEPS   = 1000
RANDOM_SEED  = 42

GLIDER_STEPS = 500
MAX_CELLS    = 500
DISP_EPSILON = 1e-6

HEX_DIRS = [
    ( 1,  0),  # E  bit5
    ( 1, -1),  # SE bit4
    ( 0, -1),  # SW bit3
    (-1,  0),  # W  bit2
    (-1,  1),  # NW bit1
    ( 0,  1),  # NE bit0
]


# ── C2 symmetry helpers ───────────────────────────────────────────────────────

def rotate60_msb(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1  # E
    b2 = (state >> 4) & 1  # SE
    b3 = (state >> 3) & 1  # SW
    b4 = (state >> 2) & 1  # W
    b5 = (state >> 1) & 1  # NW
    b6 = (state >> 0) & 1  # NE
    # 60° CW rotation: E->SE, SE->SW, SW->W, W->NW, NW->NE, NE->E
    return c * 64 + b6 * 32 + b1 * 16 + b2 * 8 + b3 * 4 + b4 * 2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


def hamming_weight(state: int) -> int:
    return bin(state).count('1')


# ── Rule generation ───────────────────────────────────────────────────────────

def _try_add_kernel_pair(a: int, b: int, mapped: dict) -> bool:
    """
    Add reversible C2-symmetric kernel pair (a, b) to mapped dict.
    Adds: a->b, b->a, C2(a)->C2(b), C2(b)->C2(a).
    Returns False on any conflict, True on success.
    """
    if a == b:
        return False

    c2_a = rotate_c2(a)
    c2_b = rotate_c2(b)

    # C2 fixed-point consistency: if a is its own C2 image, b must be too
    if (c2_a == a) != (c2_b == b):
        return False

    # Build the complete set of new mappings
    if c2_a == a:
        new_mappings = [(a, b), (b, a)]
    else:
        new_mappings = [(a, b), (b, a), (c2_a, c2_b), (c2_b, c2_a)]

    # Check for conflicts with existing mappings
    for src, dst in new_mappings:
        if src in mapped and mapped[src] != dst:
            return False

    # Require at least one new non-identity mapping
    if not any(src != dst and src not in mapped for src, dst in new_mappings):
        return False

    for src, dst in new_mappings:
        mapped[src] = dst
    return True


def generate_hybrid_rule(rng: random.Random) -> dict:
    """
    Generate hybrid rule: 4 cooling pairs (HW_A >= 3, HW_B < 3)
    and 4 glider/birth pairs (HW_C <= 2, HW_D > HW_C).
    Rule is reversible (involution) and C2-symmetric.
    """
    cooling_src_pool = [s for s in range(128) if hamming_weight(s) >= 3]
    cooling_tgt_pool = [s for s in range(128) if hamming_weight(s) < 3]
    glider_src_pool  = [s for s in range(128) if hamming_weight(s) <= 2]

    # Precompute target pools indexed by minimum HW threshold
    higher_hw_pool: dict[int, list] = {}
    for hw in range(7):
        higher_hw_pool[hw] = [s for s in range(128) if hamming_weight(s) > hw]

    while True:
        mapped: dict[int, int] = {}

        # --- 4 cooling kernel pairs ---
        cooling_found = 0
        for _ in range(300_000):
            if cooling_found >= 4:
                break
            a = rng.choice(cooling_src_pool)
            b = rng.choice(cooling_tgt_pool)
            if hamming_weight(a) <= hamming_weight(b):
                continue
            if _try_add_kernel_pair(a, b, mapped):
                cooling_found += 1

        if cooling_found < 4:
            continue

        # --- 4 glider/birth kernel pairs ---
        glider_found = 0
        for _ in range(300_000):
            if glider_found >= 4:
                break
            c = rng.choice(glider_src_pool)
            hw_c = hamming_weight(c)
            tgt = higher_hw_pool.get(hw_c)
            if not tgt:
                continue
            d = rng.choice(tgt)
            if _try_add_kernel_pair(c, d, mapped):
                glider_found += 1

        if glider_found < 4:
            continue

        return {str(k): v for k, v in mapped.items() if k != v}


# ── Dense grid simulation (soup test) ────────────────────────────────────────

def build_lookup(rule_dict: dict) -> np.ndarray:
    lookup = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lookup[int(k)] = int(v)
    return ((lookup >> 6) & 1).astype(np.uint8)


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


# ── Sparse CA step (glider test, infinite plane) ──────────────────────────────

def _nbr_state(cells: frozenset, q: int, r: int) -> int:
    val = (1 if (q, r) in cells else 0) << 6
    for i, (dq, dr) in enumerate(HEX_DIRS):
        val |= (1 if (q + dq, r + dr) in cells else 0) << (5 - i)
    return val


def step_cells(cells: frozenset, rule: dict) -> frozenset:
    candidates: set = set(cells)
    for q, r in cells:
        for dq, dr in HEX_DIRS:
            candidates.add((q + dq, r + dr))
    new: set = set()
    for q, r in candidates:
        nbr    = _nbr_state(cells, q, r)
        mapped = rule.get(nbr, nbr)
        if (mapped >> 6) & 1:
            new.add((q, r))
    return frozenset(new)


def translate_normalize(cells) -> frozenset:
    if not cells:
        return frozenset()
    min_q = min(q for q, _ in cells)
    min_r = min(r for _, r in cells)
    return frozenset((q - min_q, r - min_r) for q, r in cells)


def centroid(cells):
    n = len(cells)
    return (sum(q for q, _ in cells) / n, sum(r for _, r in cells) / n)


# ── Seed generation (21 standard contiguous seeds) ───────────────────────────

def _apply_rotation(q, r, t):
    if t == 0: return ( q,       r      )
    if t == 1: return (-r,       q + r  )
    if t == 2: return (-(q + r), q      )
    if t == 3: return (-q,      -r      )
    if t == 4: return ( r,      -(q + r))
    if t == 5: return ( q + r,  -q      )
    raise ValueError(t)


def _tl_norm(cells):
    sc = sorted(cells)
    q0, r0 = sc[0]
    return frozenset((q - q0, r - r0) for q, r in sc)


def _rot_norm(cells) -> frozenset:
    best = None
    for t in range(6):
        rot  = [_apply_rotation(q, r, t) for q, r in cells]
        norm = _tl_norm(rot)
        if best is None or sorted(norm) < sorted(best):
            best = norm
    return best


def _is_connected(cells) -> bool:
    cs = set(cells)
    start = next(iter(cs))
    visited = {start}
    stack = [start]
    while stack:
        q, r = stack.pop()
        for dq, dr in HEX_DIRS:
            nb = (q + dq, r + dr)
            if nb in cs and nb not in visited:
                visited.add(nb)
                stack.append(nb)
    return len(visited) == len(cs)


def get_contiguous_3bit_seeds():
    """11 fixed trihex seeds (unique under translation only)."""
    all_cells = [(q, r) for q in range(-3, 4) for r in range(-3, 4)]
    seen: set = set()
    seeds = []
    for combo in combinations(all_cells, 3):
        if not _is_connected(combo):
            continue
        cf = _tl_norm(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(sorted(cf))
    return seeds


def get_contiguous_4bit_seeds():
    """10 one-sided tetrahex seeds (unique under C6 rotation)."""
    all_cells = [(q, r) for q in range(-4, 5) for r in range(-4, 5)]
    seen: set = set()
    seeds = []
    for combo in combinations(all_cells, 4):
        if not _is_connected(combo):
            continue
        cf = _rot_norm(combo)
        if cf in seen:
            continue
        seen.add(cf)
        seeds.append(sorted(cf))
    return seeds


# ── Motion fitness (single seed) ──────────────────────────────────────────────

def scan_seed_for_motion(seed_cells, rule: dict) -> dict:
    cells = frozenset(map(tuple, seed_cells))
    norm  = translate_normalize(cells)
    c     = centroid(cells)
    history = {norm: (0, c)}

    for t in range(1, GLIDER_STEPS + 1):
        cells = step_cells(cells, rule)
        n = len(cells)
        if n == 0:
            return {"motion_fitness": 0.0, "period": 0, "velocity": (0, 0),
                    "final_bit_count": 0, "kind": "decayed"}
        if n > MAX_CELLS:
            return {"motion_fitness": 0.0, "period": 0, "velocity": (0, 0),
                    "final_bit_count": n, "kind": "exploded"}

        norm = translate_normalize(cells)
        c    = centroid(cells)

        if norm in history:
            prev_t, prev_c = history[norm]
            period = t - prev_t
            dq     = c[0] - prev_c[0]
            dr     = c[1] - prev_c[1]
            disp   = math.hypot(dq, dr)
            fitness = disp / (1.0 + n)
            kind = "glider" if disp > DISP_EPSILON else (
                "still_life" if period == 1 else "oscillator"
            )
            return {
                "motion_fitness":  fitness,
                "period":          period,
                "velocity":        (round(dq), round(dr)),
                "final_bit_count": n,
                "kind":            kind,
            }
        history[norm] = (t, c)

    return {"motion_fitness": 0.0, "period": 0, "velocity": (0, 0),
            "final_bit_count": len(cells), "kind": "no_cycle"}


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> int:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    result = {
        "status":              "experiment_failed",
        "soup_resolved":       False,
        "final_soup_bit_count": 0,
        "glider_found":        False,
        "motion_fitness":      0.0,
        "glider_seed_info":    "",
        "glider_period":       0,
        "glider_velocity":     [0, 0],
    }

    try:
        # ── Part 1: Generate hybrid rule ──────────────────────────────────────
        print("Generating hybrid rule (4 cooling + 4 glider/birth kernel pairs) ...")
        rng       = random.Random(7)
        rule_dict = generate_hybrid_rule(rng)
        rule      = {int(k): int(v) for k, v in rule_dict.items()}
        print(f"  {len(rule_dict)} non-identity entries")

        with open(RULE_JSON, "w") as f:
            json.dump(rule_dict, f, sort_keys=True, indent=2)
        print(f"  Saved rule -> {RULE_JSON}")

        # Verify involution
        violations = sum(
            1 for k, v in rule.items() if rule.get(v, v) != k
        )
        print(f"  Involution violations: {violations}")

        # ── Part 2A: Soup resolution ──────────────────────────────────────────
        print(f"\nTest A: soup {GRID_SIZE}x{GRID_SIZE}, "
              f"{DENSITY*100:.0f}% density, {SOUP_STEPS} steps ...")
        np_rng = np.random.default_rng(RANDOM_SEED)
        soup   = (np_rng.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
        print(f"  Initial live cells: {int(soup.sum())}")

        lookup = build_lookup(rule_dict)
        grid   = soup.copy()
        for step in range(SOUP_STEPS):
            grid = step_grid(grid, lookup)
            if (step + 1) % 200 == 0:
                print(f"  step {step+1:4d}: {int(grid.sum())} live cells")

        final_bit_count = int(grid.sum())
        soup_resolved   = 20 <= final_bit_count <= 1000
        print(f"  Final live cells: {final_bit_count}  soup_resolved={soup_resolved}")

        result["soup_resolved"]        = bool(soup_resolved)
        result["final_soup_bit_count"] = final_bit_count

        # ── Part 2B: Glider search ────────────────────────────────────────────
        print(f"\nTest B: glider search (21 seeds, {GLIDER_STEPS} steps each) ...")
        seeds_3bit = get_contiguous_3bit_seeds()
        seeds_4bit = get_contiguous_4bit_seeds()
        print(f"  Seeds: {len(seeds_3bit)} trihex + {len(seeds_4bit)} tetrahex "
              f"= {len(seeds_3bit)+len(seeds_4bit)} total")

        best_fitness   = 0.0
        best_seed_info = ""
        best_period    = 0
        best_velocity  = (0, 0)

        all_seeds = (
            [("3-bit", i, s) for i, s in enumerate(seeds_3bit)]
            + [("4-bit", i, s) for i, s in enumerate(seeds_4bit)]
        )

        for label, idx, seed in all_seeds:
            res     = scan_seed_for_motion(seed, rule)
            fitness = res["motion_fitness"]
            print(f"  [{label} #{idx+1:2d}] {res['kind']:<12s} "
                  f"fitness={fitness:.6f}  period={res['period']}  "
                  f"vel={res['velocity']}  bits={res['final_bit_count']}")
            if fitness > best_fitness:
                best_fitness   = fitness
                best_seed_info = f"{label} seed #{idx+1} coords={seed[:4]}..."
                best_period    = res["period"]
                best_velocity  = res["velocity"]

        glider_found = best_fitness > 0.0
        print(f"\n  max motion_fitness={best_fitness:.8f}  glider_found={glider_found}")
        if glider_found:
            print(f"  Best: {best_seed_info}  period={best_period}  vel={best_velocity}")

        result.update({
            "status":           "ok",
            "glider_found":     bool(glider_found),
            "motion_fitness":   round(float(best_fitness), 8),
            "glider_seed_info": best_seed_info,
            "glider_period":    int(best_period),
            "glider_velocity":  list(best_velocity),
        })

    except Exception:
        traceback.print_exc()
        result["status"] = "experiment_failed"

    # ── Part 3: Write result.yaml ─────────────────────────────────────────────
    RESULT_YAML.parent.mkdir(parents=True, exist_ok=True)
    with open(RESULT_YAML, "w") as f:
        yaml.dump(result, f, default_flow_style=False, sort_keys=False)
    print(f"\nWrote {RESULT_YAML}")
    print(yaml.dump(result, default_flow_style=False, sort_keys=False))

    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
