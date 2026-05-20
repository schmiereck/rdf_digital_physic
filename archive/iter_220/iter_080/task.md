Write the following Python script to `src/run_evolution_exp_220_sublight_final.py`.

```python
import os
import sys
import json
import csv
import math
import random
import time
from pathlib import Path
import numpy as np

# Set project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from evolution import generate_random_c2_rule, rule_dict_to_lut, step_grid, center_of_mass

class SubLightFitness:
    \"\"\"Fitness function for sub-light speed (v<c) glider discovery.\"\"\"
    def __init__(self, grid_size=128, simulation_steps=500, window_start=200, window_end=400, expected_bits=3):
        self.grid_size = grid_size
        self.simulation_steps = simulation_steps
        self.window_start = window_start
        self.window_end = window_end
        self.expected_bits = expected_bits

    @staticmethod
    def _detect_period(grid_history, start, end, max_k=64):
        configs = []
        for grid in grid_history[start:end]:
            positions = np.where(grid > 0)
            if len(positions[0]) == 0:
                configs.append(frozenset())
                continue
            r, c = positions[0], positions[1]
            com_r, com_c = np.mean(r), np.mean(c)
            norm = frozenset((int(curr_r - round(com_r)), int(curr_c - round(com_c))) for curr_r, curr_c in zip(r, c))
            configs.append(norm)
        for k in range(1, max_k + 1):
            if k >= len(configs):
                break
            if all(configs[i] == configs[i+k] for i in range(len(configs) - k)):
                return k
        return 0

    def evaluate(self, rule_dict):
        lut = rule_dict_to_lut(rule_dict)
        grid = np.zeros((self.grid_size, self.grid_size), dtype=np.uint8)
        # 3-bit L-tromino seed
        for r, c in [(63, 63), (64, 63), (64, 64)]:
            grid[r, c] = 1

        initial_bits = int(grid.sum())
        grid_history = [grid.copy()]
        com_history = [center_of_mass(grid)]

        cum_offset = np.array([0.0, 0.0])
        prev_raw_com = np.array(center_of_mass(grid))

        for _ in range(self.simulation_steps):
            grid = step_grid(grid, lut)
            raw_com = np.array(center_of_mass(grid))
            delta = raw_com - prev_raw_com
            delta -= np.round(delta / self.grid_size) * self.grid_size
            cum_offset += delta
            prev_raw_com = raw_com
            com_history.append(cum_offset.copy() + np.array(center_of_mass(grid)))
            grid_history.append(grid.copy())

        final_bits = int(grid.sum())
        if initial_bits != self.expected_bits or final_bits != self.expected_bits:
            return {"fitness": 0.0, "reason": "bit_conservation_failed", "final_bits": final_bits}

        com_start = com_history[self.window_start]
        com_end = com_history[self.window_end]
        displacement = math.sqrt((com_end[0] - com_start[0])**2 + (com_end[1] - com_start[1])**2)
        measured_velocity = displacement / (self.window_end - self.window_start)

        if displacement == 0.0:
            return {"fitness": 0.0, "reason": "no_displacement"}
        if measured_velocity >= 0.9:
            return {"fitness": 0.0, "reason": "velocity_at_c", "velocity": measured_velocity}

        period = self._detect_period(grid_history, self.window_start, self.window_end)
        if period <= 1:
            return {"fitness": 0.0, "reason": "period_too_short", "period": period}

        positions = np.where(grid > 0)
        if len(positions[0]) == 0:
            bb_area = 0
        else:
            bb_area = (np.max(positions[0]) - np.min(positions[0]) + 1) * (np.max(positions[1]) - np.min(positions[1]) + 1)

        period_bonus = 1.0 - 1.0 / period
        fitness = (displacement / (1.0 + bb_area)) * period_bonus

        return {
            "fitness": fitness,
            "reason": "ok",
            "displacement": displacement,
            "measured_velocity": measured_velocity,
            "period": period,
            "period_bonus": period_bonus,
            "bb_area": bb_area,
        }

    def __call__(self, rule_dict):
        res = self.evaluate(rule_dict)
        return res["fitness"], res

def main():
    _fitness_fn = SubLightFitness(grid_size=128, simulation_steps=500)
    # GA Setup
    POP_SIZE = 100
    GENERATIONS = 20
    ELITE_SIZE = 10
    MUTATION_RATE = 0.01

    print(f"=== Starting SubLight GA Search (pop={POP_SIZE}, gens={GENERATIONS}) ===")
    population = [generate_random_c2_rule() for _ in range(POP_SIZE)]
    
    # Evaluate generation 0
    scores = []
    for r in population:
        fit, _ = _fitness_fn(r)
        scores.append(fit)
    
    best_fit = max(scores)
    mean_fit = sum(scores) / len(scores)
    print(f"Gen  0: best={best_fit:.6f}  mean={mean_fit:.6f}")

    # Evolution Loop
    for gen in range(1, GENERATIONS + 1):
        # Elitism
        elites = [population[i] for i in np.argsort(scores)[-ELITE_SIZE:]]
        
        new_pop = list(elites)
        while len(new_pop) < POP_SIZE:
            # Recombination (Crossover)
            p1, p2 = random.sample(elites, 2)
            # Create a child by swapping chromosome entries
            child = {}
            for k in range(128):
                child[str(k)] = p1.get(str(k), 0) if random.random() < 0.5 else p2.get(str(k), 0)
            
            # Mutation
            for k in range(128):
                if random.random() < MUTATION_RATE:
                    child[str(k)] = random.randint(0, 127)
            new_pop.append(child)
            
        population = new_pop
        scores = []
        details = []
        for r in population:
            fit, d = _fitness_fn(r)
            scores.append(fit)
            details.append(d)
            
        best_fit = max(scores)
        mean_fit = sum(scores) / len(scores)
        print(f"Gen {gen:2d}: best={best_fit:.6f}  mean={mean_fit:.6f}")

        if best_fit > 0.0:
            best_idx = np.argmax(scores)
            print(f"  -> Found active rule! fitness={best_fit:.6f}, detail: {details[best_idx]}")

    best_idx = np.argmax(scores)
    champion = population[best_idx]
    champion_detail = details[best_idx]
    
    results_dir = PROJECT_ROOT / "archive" / "iter_220" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    with open(results_dir / "champion_rule.json", "w") as f:
        json.dump({
            "fitness": best_fit,
            "rule_dict": champion,
            "detail": champion_detail
        }, f, indent=2)
        
    print(f"=== Evolutionary Search Finished! Champion fitness: {best_fit:.6f} ===")

if __name__ == '__main__':
    main()
```

Run this script `python src/run_evolution_exp_220_sublight_final.py`.
Output the execution log and details of the champion rule. Ensure files under `archive/iter_220/results/` are correctly updated with the new champion!