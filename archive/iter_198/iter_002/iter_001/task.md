
## Task: Implement MassiveGliderFitness and Experiment Configuration

This task has two parts:
1.  **Implement the `MassiveGliderFitness` class in `src/fitness.py`.**
2.  **Create a new experiment configuration file `src/experiments/exp_198_2_massive_glider.py` that uses this new fitness function.**

### Part 1: `MassiveGliderFitness` Implementation

Modify `src/fitness.py` to add the new `MassiveGliderFitness` class. This class should be designed to find `v<c` gliders while avoiding the "grid-filling" and "fizzler" exploits seen in previous iterations.

**Requirements:**
*   **Inherit from `fitness.Fitness`.**
*   **Checkpoints:** Use a system of checkpoints (e.g., every 64 steps for a total of 256 steps) to measure sustained motion.
*   **Velocity Constraint:** The fitness should be zero if the displacement between any two consecutive checkpoints is zero or is greater than or equal to the number of steps between them (i.e., `v=0` or `v>=c`).
*   **Compactness Penalty:** The final fitness score should be the total displacement, penalized by the pattern's size and complexity. The proposed formula is `total_displacement / (1 + final_bit_count * bounding_box_area)`.
*   **Fizzler/Chaos Penalty:** If the final bit count is more than 3 times the initial bit count, return a fitness of 0. This is a heuristic to quickly discard chaotic rules that just fill the grid.

Here is a template for the class:

```python
# In src/fitness.py

# ... (other imports)
import numpy as np
from ca_simulator import CASimulator
from utils import get_bounding_box, get_center_of_mass

class MassiveGliderFitness(Fitness):
    def __init__(self, target_ca_string=None, steps=256, checkpoints=4):
        super().__init__(target_ca_string)
        self.steps = steps
        self.num_checkpoints = checkpoints
        self.steps_per_checkpoint = steps // checkpoints

    def __call__(self, rule_string, seed):
        simulator = CASimulator(seed.shape[0], seed.shape[1])
        initial_bit_count = np.sum(seed)
        grid = seed.copy()

        centers_of_mass = []
        # Run simulation to first checkpoint
        grid = simulator.run(rule_string, grid, self.steps_per_checkpoint)
        if grid is None: # Error in simulation
            return 0.0
        centers_of_mass.append(get_center_of_mass(grid))

        # Run for remaining checkpoints
        for _ in range(self.num_checkpoints - 1):
            grid = simulator.run(rule_string, grid, self.steps_per_checkpoint)
            if grid is None:
                return 0.0
            centers_of_mass.append(get_center_of_mass(grid))

        # Check for fizzlers/chaos
        final_bit_count = np.sum(grid)
        if final_bit_count > initial_bit_count * 3 or final_bit_count == 0:
            return 0.0

        # Calculate displacements and total distance
        total_displacement = 0
        for i in range(self.num_checkpoints - 1):
            p1 = centers_of_mass[i]
            p2 = centers_of_mass[i+1]
            if p1 is None or p2 is None:
                return 0.0 # Pattern died
            
            displacement = np.linalg.norm(np.array(p2) - np.array(p1))

            # Velocity check: must be 0 < v < c
            if displacement == 0 or displacement >= self.steps_per_checkpoint:
                return 0.0
            
            total_displacement += displacement
            
        # If total displacement is zero, it's not a glider
        if total_displacement == 0:
            return 0.0

        # Calculate compactness penalty
        min_r, min_c, max_r, max_c = get_bounding_box(grid)
        bounding_box_area = (max_r - min_r + 1) * (max_c - min_c + 1)
        
        # Avoid division by zero, although bit count should be > 0 here
        if final_bit_count == 0 or bounding_box_area == 0:
            return 0.0

        penalty = 1 + (final_bit_count * bounding_box_area)
        fitness = total_displacement / penalty
        
        return fitness
```

### Part 2: Experiment Configuration

Create a new file `src/experiments/exp_198_2_massive_glider.py` to define the evolutionary search parameters.

**File Content:**

```python
# src/experiments/exp_198_2_massive_glider.py
from fitness import MassiveGliderFitness
from seeds import L_TROMINO_SEED

EXPERIMENT_CONFIG = {
    "name": "massive_glider_search",
    "notes": "Evolutionary search for a v<c glider using MassiveGliderFitness, which penalizes large/complex patterns.",
    "rule_space": "B3/S23", # A good starting point
    "fitness_function": MassiveGliderFitness(steps=256, checkpoints=4),
    "seed": L_TROMINO_SEED,
    "population_size": 100,
    "generations": 10,
    "mutation_rate": 0.1,
    "cx_prob": 0.5,
    "num_elites": 2,
}
```
This experiment is configured for 10 generations which is more than the minimum of 5.

### Final Output

The executor should confirm the creation/modification of `src/fitness.py` and the creation of `src/experiments/exp_198_2_massive_glider.py`.

The final YAML should be:
```yaml
status: ok
artifacts:
  - "src/fitness.py"
  - "src/experiments/exp_198_2_massive_glider.py"
metrics: {}
log_excerpt: |
  Successfully created MassiveGliderFitness in src/fitness.py.
  Successfully created experiment config src/experiments/exp_198_2_massive_glider.py.
experimenter_view: |
  The `MassiveGliderFitness` class and the corresponding experiment configuration have been successfully created. The fitness function correctly implements the logic for sustained motion, velocity constraints, and a compactness penalty to avoid known exploits. The experiment is ready to be executed.
notes: "Setup for the v<c glider search is complete."
```
