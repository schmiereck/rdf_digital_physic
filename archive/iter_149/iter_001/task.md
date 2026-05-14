## Task: Implement and Validate the Velocity Stability Fitness Metric

The goal is to implement the velocity stability metric proposed in iter_143/144 and validate it against `rule_016`, which is known to have decaying motion (as confirmed in iter_142).

### 1. Create `src/fitness.py`

Create a new file to house the fitness function.

```python
# src/fitness.py
import numpy as np
from ca_simulation import CASimulation  # Assuming this is the main simulation class

def calculate_velocity_stability(rule_string, initial_state, steps_per_window=400, num_windows=3):
    """
    Calculates fitness based on the stability of velocity over multiple time windows.

    A stable glider should have a constant velocity, meaning a very low standard deviation.
    Decaying motion will have a high standard deviation.

    Fitness is defined as 1 / (1 + stddev).
    """
    sim = CASimulation(initial_state.shape, rule_string)
    sim.grid = np.copy(initial_state)

    velocities = []
    
    total_steps = steps_per_window * num_windows
    com_history = []

    # Run the full simulation and record center of mass
    for i in range(total_steps + 1):
        if i % 10 == 0: # Sample COM periodically
             com = sim.get_center_of_mass()
             if com is None: # All cells died
                 com_history.append(com_history[-1] if com_history else (0,0))
             else:
                 com_history.append(com)
        sim.step()

    # Calculate velocity for each window
    # We need COM at the start and end of each window.
    # Window 1: steps 0 to 400
    # Window 2: steps 400 to 800
    # Window 3: steps 800 to 1200
    # Let's adjust the simulation to be more precise.
    
    sim.grid = np.copy(initial_state)
    com_checkpoints = []
    
    # Get COM at the start of each window
    com_checkpoints.append(sim.get_center_of_mass() or (0,0))

    for i in range(num_windows):
        sim.run(steps_per_window)
        com_checkpoints.append(sim.get_center_of_mass() or (0,0))

    for i in range(num_windows):
        start_com = np.array(com_checkpoints[i])
        end_com = np.array(com_checkpoints[i+1])
        displacement = np.linalg.norm(end_com - start_com)
        velocity = displacement / steps_per_window
        velocities.append(velocity)

    if len(velocities) < 2:
        return 0.0, velocities, 0.0

    std_dev = np.std(velocities)
    fitness = 1.0 / (1.0 + std_dev)

    return fitness, velocities, std_dev
```

### 2. Create `src/validate_metric.py`

This script will run the validation experiment.

- It needs to load `rule_016`. This rule was the "new champion" from the `fresh-local-start` campaign. The exact rule string should be retrieved from `archive/iter_135/results/rules/rule_016.txt`.
- It needs the initial state that `rule_016` acts upon. This was the `remnant.npy` from `iter_132`.
- It will use the new fitness function to calculate the score.

```python
# src/validate_metric.py
import json
import numpy as np
import os
from fitness import calculate_velocity_stability

def main():
    # --- Configuration ---
    # The rule to test: new champion from the fresh-local-start campaign
    rule_path = 'archive/iter_135/results/rules/rule_016.txt'
    # The initial state: the remnant from the end of the long-run-evaporation run
    initial_state_path = 'archive/iter_132/results/remnant.npy'
    
    output_dir = 'archive/iter_149/results'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'validation_results.json')

    # --- Load Artifacts ---
    print(f"Loading rule from {rule_path}")
    with open(rule_path, 'r') as f:
        rule_string = f.read().strip()

    print(f"Loading initial state from {initial_state_path}")
    initial_state = np.load(initial_state_path)

    # --- Run Experiment ---
    print("Calculating velocity stability...")
    # Use 4 windows of 400 steps (total 1600) to get 4 velocity measurements
    fitness, velocities, std_dev = calculate_velocity_stability(
        rule_string, 
        initial_state,
        steps_per_window=400,
        num_windows=4 
    )

    # --- Report Results ---
    results = {
        'rule_id': 'rule_016',
        'initial_state': 'remnant_iter_132',
        'num_windows': 4,
        'steps_per_window': 400,
        'velocities': velocities,
        'std_dev': std_dev,
        'fitness': fitness
    }
    
    print(f"Velocities: {velocities}")
    print(f"Standard Deviation: {std_dev}")
    print(f"Final Fitness Score: {fitness}")

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
        
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    # You will need to make sure that the CASimulation class and any dependencies
    # are available in the execution environment. Assume `ca_simulation.py` exists in `src/`.
    # You may need to create a placeholder `ca_simulation.py` if it doesn't exist from a previous step.
    # For now, let's assume it exists and has `step()`, `run()`, `get_center_of_mass()`.
    main()

```

*Self-correction:* The previous hypothesis mentioned three windows. Using four windows (total 1600 steps) will give a slightly more robust standard deviation calculation. I will update the implementation to use four windows.

### 3. Execution Command

Run the validation script.

```bash
python src/validate_metric.py
```

### 4. Success Criteria

The experiment is successful if the `fitness` value reported in `validation_results.json` is low, specifically `< 0.1`, confirming the hypothesis that the metric correctly identifies this rule's motion as unstable.

### Final YAML for Executor:
```yaml
status: ok
artifacts:
  - "archive/iter_149/results/validation_results.json"
metrics:
  fitness: <value_from_json>
  std_dev: <value_from_json>
log_excerpt: |
  <last 20 lines of stdout from `python src/validate_metric.py`>
experimenter_view: |
  The validation script ran successfully. The `calculate_velocity_stability` function was implemented and applied to `rule_016` acting on the `remnant.npy` initial state. The calculated velocities, standard deviation, and final fitness score are reported in the metrics and artifacts. The key result is whether the final fitness score is low, as predicted.
notes: "Validating the new velocity-stability fitness metric."
```
