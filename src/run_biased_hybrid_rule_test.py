#!/usr/bin/env python3
"""
run_biased_hybrid_rule_test.py  (iter_117)

Generate one 'biased hybrid' CA rule (6 cooling + 2 birth kernel pairs) and
evaluate it on soup resolution and motion fitness.

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
RULE_DIR     = PROJECT_ROOT / "archive" / "iter_117" / "rule"
RULE_JSON    = RULE_DIR / "biased_hybrid_rule.json"

GRID_SIZE    = 150
DENSITY      = 0.25
SOUP_STEPS   = 1000
SOUP_SEED    = 42

GLIDER_STEPS = 500
MAX_CELLS    = 500
DISP_EPSILON = 1e-9

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
    # 60° CW: E->SE, SE->SW, SW->W, W->NW, NW->NE, NE->E
    return c * 64 + b6 * 32 + b1 * 16 + b2 * 8 + b3 * 4 + b4 * 2 + b5


def rotate_c2(state: int) -> int:
    return rotate60_msb(rotate60_msb(rotate60_msb(state)))


def hamming_weight(state: int) -> int:
    return bin(state).count('1')


# ── Rule generation ───────────────────────────────────────────────────────────

def _try_add_kernel_pair(a: int, b: int, mapped: dict) -> bool:
    """Add reversible C2-symmetric kernel pair (a, b) to mapped dict."""
    if a == b:
        return False

    c2_a = rotate_c2(a)
    c2_b = rotate_c2(b)

    # C2 fixed-point consistency: if a is its own C2 image, b must be too
    if (c2_a == a) != (c2_b == b):
        return False

    if c2_a == a:
        new_mappings = [(a, b), (b, a)]
    else:
        new_mappings = [(a, b), (b, a), (c2_a, c2_b), (c2_b, c2_a)]

    for src, dst in new_mappings:
        if src in mapped and mapped[src] != dst:
            return False

    if not any(src != dst and src not in mapped for src, dst in new_mappings):
        return False

    for src, dst in new_mappings:
        mapped[src] = dst
    return True


def generate_biased_hybrid_rule() -> dict:
    """
    Generate a C2-symmetric, reversible (involution) rule with:
      6 cooling kernel pairs: HW(A) >= 3, HW(B) < 3
      2 birth kernel pairs:   HW(A) <= 2, HW(B) > HW(A), A % 2 == B % 2
    Uses random.seed(117) for reproducibility.
    """
    random.seed(117)

    cooling_src_pool = [s for s in range(128) if hamming_weight(s) >= 3]
    cooling_tgt_pool = [s for s in range(128) if hamming_weight(s) < 3]
    birth_src_pool   = [s for s in range(128) if hamming_weight(s) <= 2]

    # Precompute birth target pools indexed by (hw_a, parity) for speed
    birth_tgt_by_hw_parity: dict[tuple, list] = {}
    for hw_a in range(3):
        for parity in (0, 1):
            birth_tgt_by_hw_parity[(hw_a, parity)] = [
                s for s in range(128)
                if hamming_weight(s) > hw_a and s % 2 == parity
            ]

    while True:
        mapped: dict[int, int] = {}

        # --- 6 cooling kernel pairs ---
        cooling_found = 0
        for _ in range(500_000):
            if cooling_found >= 6:
                break
            a = random.choice(cooling_src_pool)
            b = random.choice(cooling_tgt_pool)
            if hamming_weight(a) <= hamming_weight(b):
                continue
            if _try_add_kernel_pair(a, b, mapped):
                cooling_found += 1

        if cooling_found < 6:
            continue

        # --- 2 birth kernel pairs (center bit preserved: A % 2 == B % 2) ---
        birth_found = 0
        for _ in range(500_000):
            if birth_found >= 2:
                break
            a    = random.choice(birth_src_pool)
            hw_a = hamming_weight(a)
            tgt  = birth_tgt_by_hw_parity.get((hw_a, a % 2), [])
            if not tgt:
                continue
            b = random.choice(tgt)
            if _try_add_kernel_pair(a, b, mapped):
                birth_found += 1

        if birth_found < 2:
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
    sc = sorted(cells)
    q0, r0 = sc[0]
    return frozenset((q - q0, r - r0) for q, r in sc)


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
    cells   = frozenset(map(tuple, seed_cells))
    norm    = translate_normalize(cells)
    c       = centroid(cells)
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
            period  = t - prev_t
            dq      = c[0] - prev_c[0]
            dr      = c[1] - prev_c[1]
            disp    = math.hypot(dq, dr)
            fitness = disp / (1.0 + n) if disp > DISP_EPSILON else 0.0
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
    log_lines: list[str] = []

    def log(msg: str):
        print(msg, flush=True)
        log_lines.append(msg)

    metrics = {
        "soup_resolved":        0,
        "final_soup_bit_count": 0,
        "glider_found":         0,
        "motion_fitness":       0.0,
        "cooling_pairs":        6,
        "birth_pairs":          2,
    }
    status = "code_error"

    try:
        RULE_DIR.mkdir(parents=True, exist_ok=True)

        # ── Part 1: Generate biased hybrid rule ───────────────────────────────
        log("Generating biased hybrid rule (6 cooling + 2 birth kernel pairs)...")
        rule_dict = generate_biased_hybrid_rule()
        rule      = {int(k): int(v) for k, v in rule_dict.items()}
        log(f"  Non-identity entries: {len(rule_dict)}")

        with open(RULE_JSON, "w") as f:
            json.dump(rule_dict, f, sort_keys=True, indent=2)
        log(f"  Saved -> {RULE_JSON}")

        violations = sum(1 for k, v in rule.items() if rule.get(v, v) != k)
        log(f"  Involution violations: {violations}")

        # ── Part 2A: Soup resolution ──────────────────────────────────────────
        log(f"\nSoup test: {GRID_SIZE}x{GRID_SIZE}, "
            f"{DENSITY*100:.0f}% density, {SOUP_STEPS} steps...")
        np.random.seed(SOUP_SEED)
        soup = (np.random.random((GRID_SIZE, GRID_SIZE)) < DENSITY).astype(np.uint8)
        log(f"  Initial live cells: {int(soup.sum())}")

        lookup = build_lookup(rule_dict)
        grid   = soup.copy()
        for step in range(SOUP_STEPS):
            grid = step_grid(grid, lookup)
            if (step + 1) % 200 == 0:
                log(f"  step {step+1:4d}: {int(grid.sum())} live cells")

        final_bit_count = int(grid.sum())
        soup_resolved   = 1 if final_bit_count <= 1000 else 0
        log(f"  Final live cells: {final_bit_count}  "
            f"soup_resolved={bool(soup_resolved)}")

        metrics["soup_resolved"]        = soup_resolved
        metrics["final_soup_bit_count"] = final_bit_count

        # ── Part 2B: Motion test ──────────────────────────────────────────────
        log(f"\nMotion test: 21 seeds, {GLIDER_STEPS} steps each...")
        seeds_3bit = get_contiguous_3bit_seeds()
        seeds_4bit = get_contiguous_4bit_seeds()
        log(f"  Seeds: {len(seeds_3bit)} trihex + {len(seeds_4bit)} tetrahex "
            f"= {len(seeds_3bit)+len(seeds_4bit)} total")

        best_fitness = 0.0
        best_info    = ""

        all_seeds = (
            [("3-bit", i, s) for i, s in enumerate(seeds_3bit)]
            + [("4-bit", i, s) for i, s in enumerate(seeds_4bit)]
        )

        for label, idx, seed in all_seeds:
            res     = scan_seed_for_motion(seed, rule)
            fitness = res["motion_fitness"]
            log(f"  [{label} #{idx+1:2d}] {res['kind']:<12s} "
                f"fitness={fitness:.6f}  period={res['period']}  "
                f"vel={res['velocity']}  bits={res['final_bit_count']}")
            if fitness > best_fitness:
                best_fitness = fitness
                best_info    = (f"{label} seed #{idx+1} kind={res['kind']} "
                                f"period={res['period']} vel={res['velocity']} "
                                f"bits={res['final_bit_count']}")

        glider_found = 1 if best_fitness > 0.0 else 0
        log(f"\n  max motion_fitness={best_fitness:.8f}  "
            f"glider_found={bool(glider_found)}")
        if glider_found:
            log(f"  Best: {best_info}")

        metrics["glider_found"]   = glider_found
        metrics["motion_fitness"] = round(float(best_fitness), 8)
        status = "ok"

    except Exception:
        traceback.print_exc()
        status = "code_error"

    # ── Final YAML output ─────────────────────────────────────────────────────
    log_excerpt = "\n".join(log_lines[-20:])

    soup_label   = "resolved" if metrics["soup_resolved"] else "NOT resolved"
    glider_label = "glider found" if metrics["glider_found"] else "no glider"
    experimenter_view = (
        f"Biased hybrid rule (6 cooling + 2 birth kernel pairs, seed=117). "
        f"Soup final bit count: {metrics['final_soup_bit_count']} ({soup_label}). "
        f"Motion fitness: {metrics['motion_fitness']:.8f} ({glider_label})."
    )

    yaml_out = {
        "status":    status,
        "artifacts": ["archive/iter_117/rule/biased_hybrid_rule.json"],
        "metrics":   metrics,
        "log_excerpt":       log_excerpt,
        "experimenter_view": experimenter_view,
        "notes": "Biased hybrid rule generation and evaluation complete.",
    }

    print("\n" + yaml.dump(yaml_out, default_flow_style=False, sort_keys=False,
                           allow_unicode=True))

    return 0 if status == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
