import json
import numpy as np
from pathlib import Path

# Load original rule
champion_path = Path("archive/iter_179/results/champion_rule.json")
with open(champion_path, "r") as f:
    champion = json.load(f)

original_rule_dict = champion["rule_dict"]
original_int = {int(k): int(v) for k, v in original_rule_dict.items()}

# Helper to get LUT from rule dict
def rule_dict_to_lut(rule_dict: dict) -> np.ndarray:
    lut = np.arange(128, dtype=np.uint8)
    for k, v in rule_dict.items():
        lut[int(k)] = int(v)
    return ((lut >> 6) & 1).astype(np.uint8)

def _rotate60(state: int) -> int:
    c  = (state >> 6) & 1
    b1 = (state >> 5) & 1
    b2 = (state >> 4) & 1
    b3 = (state >> 3) & 1
    b4 = (state >> 2) & 1
    b5 = (state >> 1) & 1
    b6 = (state >> 0) & 1
    return c * 64 + b6 * 32 + b1 * 16 + b2 * 8 + b3 * 4 + b4 * 2 + b5

def _rotate_c2(state: int) -> int:
    return _rotate60(_rotate60(_rotate60(state)))

def _try_build_c2_rule(pairs: list) -> dict | None:
    rule = {}
    for a, b in pairs:
        rot_a, rot_b = _rotate_c2(a), _rotate_c2(b)
        for src, dst in [(a, b), (b, a), (rot_a, rot_b), (rot_b, rot_a)]:
            if src in rule:
                if rule[src] != dst:
                    return None
            else:
                rule[src] = dst
    return rule

def extract_generator_pairs(rule_dict: dict) -> list:
    remaining = {(int(k), v) for k, v in rule_dict.items()}
    pairs = []
    while remaining:
        a, b = next(iter(remaining))
        rot_a = _rotate_c2(a)
        rot_b = _rotate_c2(b)
        orbit_entries = [(a, b), (b, a), (rot_a, rot_b), (rot_b, rot_a)]
        for entry in orbit_entries:
            remaining.discard(entry)
        pairs.append((a, b))
    return pairs

pairs = extract_generator_pairs(original_rule_dict)
rebuilt_rule_dict = _try_build_c2_rule(pairs)

lut_orig = rule_dict_to_lut(original_int)
lut_rebuilt = rule_dict_to_lut(rebuilt_rule_dict)

# Initialise grids
grid_orig = np.zeros((128, 128), dtype=np.uint8)
grid_rebuilt = np.zeros((128, 128), dtype=np.uint8)
for r, c in [(63, 63), (64, 63), (64, 64)]:
    grid_orig[r, c] = 1
    grid_rebuilt[r, c] = 1

def get_state_grid(grid: np.ndarray):
    e  = np.roll(grid, -1, axis=0)
    w  = np.roll(grid,  1, axis=0)
    ne = np.roll(grid, -1, axis=1)
    sw = np.roll(grid,  1, axis=1)
    se = np.roll(e,    1, axis=1)
    nw = np.roll(w,   -1, axis=1)
    return (
        (grid.astype(np.uint16) << 6)
        | (e.astype(np.uint16)  << 5)
        | (se.astype(np.uint16) << 4)
        | (sw.astype(np.uint16) << 3)
        | (w.astype(np.uint16)  << 2)
        | (nw.astype(np.uint16) << 1)
        |  ne.astype(np.uint16)
    ).astype(np.uint8)

# Step-by-step
for step in range(1, 10):
    states_orig = get_state_grid(grid_orig)
    states_rebuilt = get_state_grid(grid_rebuilt)
    
    grid_orig = lut_orig[states_orig]
    grid_rebuilt = lut_rebuilt[states_rebuilt]
    
    if not np.array_equal(grid_orig, grid_rebuilt):
        print(f"Mismatch at step {step}!")
        mismatches = np.where(grid_orig != grid_rebuilt)
        for r, c in zip(mismatches[0], mismatches[1]):
            s_orig = states_orig[r, c]
            val_orig = grid_orig[r, c]
            val_rebuilt = grid_rebuilt[r, c]
            print(f"  Cell ({r}, {c}): original state={s_orig} (lut={lut_orig[s_orig]}), rebuilt state={states_rebuilt[r, c]} (lut={lut_rebuilt[states_rebuilt[r, c]]})")
            print(f"    orig_val={val_orig}, rebuilt_val={val_rebuilt}")
        break
