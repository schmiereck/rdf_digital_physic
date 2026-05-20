import json
import numpy as np
import sys
import math
from pathlib import Path

PROJECT_ROOT = Path(".").resolve()
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import rule_dict_to_lut, step_grid
from new_fitness import DisplacementConsistencyFitness

CHAMPION_JSON = PROJECT_ROOT / "archive" / "iter_220" / "results" / "champion_rule.json"

with open(CHAMPION_JSON) as f:
    champ = json.load(f)

rule_dict = {int(k): int(v) for k, v in champ["rule_dict"].items()}
lut = rule_dict_to_lut(rule_dict)

GRID_SIZE = 128
grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint8)
grid[63, 63] = 1
grid[64, 63] = 1
grid[64, 64] = 1

def com_and_bits(g):
    rows, cols = np.where(g > 0)
    if len(rows) == 0:
        return (0.0, 0.0), 0
    return (float(np.mean(rows)), float(np.mean(cols))), int(g.sum())

c0, b0 = com_and_bits(grid)
hist = [{"step": 0, "com": c0, "bit_count": b0}]
for t in range(1, 501):
    grid = step_grid(grid, lut)
    c, b = com_and_bits(grid)
    hist.append({"step": t, "com": c, "bit_count": b})

fitness_fn = DisplacementConsistencyFitness(num_windows=5)
score = fitness_fn(hist)

print(f"Total steps: {len(hist)-1}")
print(f"Final fitness: {score:.6f}")

# Re-run step-by-step math of the fitness function on this history
initial_step = hist[0]["step"]
final_step = hist[-1]["step"]
total_steps = final_step - initial_step
steps_per_window = total_steps / fitness_fn.num_windows

print("\n--- Window Analysis ---")
window_velocity_mags = []
window_velocity_vectors = []
for w in range(fitness_fn.num_windows):
    window_start = initial_step + w * steps_per_window
    window_end = window_start + steps_per_window
    first_entry = None
    last_entry = None
    for entry in hist:
        s = entry["step"]
        if s < window_start:
            continue
        effective_window_end = window_end
        if w == fitness_fn.num_windows - 1:
            effective_window_end = final_step
        if s > effective_window_end:
            break
        if first_entry is None:
            first_entry = entry
        last_entry = entry
    
    dx = last_entry["com"][0] - first_entry["com"][0]
    dy = last_entry["com"][1] - first_entry["com"][1]
    v_mag = math.sqrt(dx*dx + dy*dy)
    window_velocity_mags.append(v_mag)
    window_velocity_vectors.append((dx, dy))
    print(f"Window {w}: steps {window_start:.1f}-{window_end:.1f} | first CoM={first_entry['com']} | last CoM={last_entry['com']} | dCoM=({dx:.4f}, {dy:.4f}) | mag={v_mag:.4f}")

mean_dx = sum(v[0] for v in window_velocity_vectors) / fitness_fn.num_windows
mean_dy = sum(v[1] for v in window_velocity_vectors) / fitness_fn.num_windows
mean_velocity_magnitude = math.sqrt(mean_dx*mean_dx + mean_dy*mean_dy)
std_dev_velocity_magnitudes = float(np.std(window_velocity_mags))
base_fitness = mean_velocity_magnitude / (1.0 + std_dev_velocity_magnitudes)

print("\n--- Summary vectors ---")
print(f"Mean velocity vector: ({mean_dx:.4f}, {mean_dy:.4f})")
print(f"Mean velocity magnitude: {mean_velocity_magnitude:.6f}")
print(f"Std dev of magnitudes: {std_dev_velocity_magnitudes:.6f}")
print(f"Base fitness (mean / (1 + std_dev)): {base_fitness:.6f}")

# Conservation factor
conservation_factors = []
for entry in hist:
    bit_count = entry["bit_count"]
    if bit_count == b0:
        conservation_factors.append(1.0)
    else:
        conservation_factors.append(min(bit_count, b0) / max(bit_count, b0))
total_conservation_score = sum(conservation_factors) / len(conservation_factors)
print(f"\nMean conservation score: {total_conservation_score:.6f}")
print(f"Calculated final fitness: {base_fitness * total_conservation_score:.6f}")
