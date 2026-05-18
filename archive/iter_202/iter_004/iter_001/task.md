
# Task: Evolve and Validate a v<c Glider

The goal is to run an evolutionary search using the new `RobustCumulativeDisplacementFitness` function to find a stable, sub-light speed glider.

## 1. Create and Execute an Orchestration Script

Create a new Python script named `src/run_evolution_202_4.py`. This script will perform all steps of the task. After creating the script, execute it using `python src/run_evolution_202_4.py`.

### Script Contents (`src/run_evolution_202_4.py`)

```python
import sys
import os
import json
import numpy as np
import yaml

# Add src to the python path to allow for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.main_v2 import L_TROMINO_3X3, run_evolution
    from src.fitness import RobustCumulativeDisplacementFitness
    from src.simulation import Simulation
    from src.visualization import render_visualization_gif
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure that 'src/main_v2.py', 'src/fitness.py', 'src/simulation.py', and 'src/visualization.py' exist and are in the python path.")
    sys.exit(1)


def evolve_and_validate():
    """
    Main function to run the evolution, identify the champion,
    validate it, and save all results.
    """
    # --- Configuration ---
    OUTPUT_DIR = "archive/iter_202/results"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    GENERATIONS = 20
    POPULATION_SIZE = 100
    GRID_SIZE = (128, 128)
    ELITE_SHARE = 0.1
    SEED_PARTICLE = L_TROMINO_3X3
    FITNESS_FUNCTION = RobustCumulativeDisplacementFitness()
    VALIDATION_STEPS = 512

    print("--- Starting Evolutionary Search ---")
    print(f"Generations: {GENERATIONS}, Population: {POPULATION_SIZE}")
    print(f"Fitness Function: {FITNESS_FUNCTION.__class__.__name__}")

    # --- 1. Run Evolution ---
    try:
        final_population = run_evolution(
            generations=GENERATIONS,
            population_size=POPULATION_SIZE,
            grid_size=GRID_SIZE,
            elite_share=ELITE_SHARE,
            seed_particle=SEED_PARTICLE,
            fitness_function=FITNESS_FUNCTION
        )
    except Exception as e:
        print(f"An error occurred during evolution: {e}")
        # Create a failure report
        report = {
            'status': 'experiment_failed',
            'artifacts': [],
            'metrics': {},
            'log_excerpt': f"Evolution failed with error: {e}",
            'experimenter_view': "The evolutionary search process failed unexpectedly. Check logs for details.",
            'notes': "Failed during run_evolution call."
        }
        with open('experiment_report.yaml', 'w') as f:
            yaml.dump(report, f)
        sys.exit(1)


    # --- 2. Identify Champion ---
    if not final_population:
        print("Evolution finished with an empty population.")
        report = {
            'status': 'experiment_failed',
            'artifacts': [],
            'metrics': {},
            'log_excerpt': "Final population was empty.",
            'experimenter_view': "Evolution completed but produced no individuals in the final population.",
            'notes': "Empty final_population."
        }
        with open('experiment_report.yaml', 'w') as f:
            yaml.dump(report, f)
        sys.exit(1)
        
    champion_rule = max(final_population, key=lambda r: r.fitness)
    print(f"Evolution complete. Champion initial fitness: {champion_rule.fitness}")

    # --- 3. Save Champion Rule ---
    champion_path = os.path.join(OUTPUT_DIR, "champion_rule.json")
    with open(champion_path, 'w') as f:
        json.dump(champion_rule.to_json(), f, indent=2)
    print(f"Champion rule saved to {champion_path}")

    # --- 4. Validate Champion ---
    print(f"--- Validating Champion Rule for {VALIDATION_STEPS} steps ---")
    sim = Simulation(grid_size=GRID_SIZE, rule=champion_rule, seed_particle=SEED_PARTICLE)
    history = sim.run(steps=VALIDATION_STEPS)

    final_fitness = FITNESS_FUNCTION.calculate(history)
    print(f"Validation run final fitness: {final_fitness}")

    # --- 5. Generate GIF ---
    gif_path = os.path.join(OUTPUT_DIR, "champion.gif")
    render_visualization_gif(history, gif_path, duration=100)
    print(f"Validation GIF saved to {gif_path}")

    # --- 6. Summarize Results ---
    summary_path = os.path.join(OUTPUT_DIR, "evolution_summary.txt")
    
    last_state = history[-1]
    initial_mass = np.sum(history[0]['grid'])
    final_mass = np.sum(last_state['grid'])
    
    com_initial = last_state['metadata']['com_history'][0]
    com_final = last_state['metadata']['com_history'][-1]
    displacement = np.linalg.norm(np.array(com_final) - np.array(com_initial))

    qualitative_desc = "Analysis of champion behavior:\n"
    if final_mass == 0:
        qualitative_desc += "- Annihilation: The pattern disappeared.\n"
    elif not np.isclose(final_mass, initial_mass):
        qualitative_desc += f"- Bit non-conserving: Mass changed from {initial_mass} to {final_mass}.\n"
    else:
        qualitative_desc += "- Bit-conserving: Mass remained stable.\n"

    if displacement > 2.0:
        qualitative_desc += f"- Movement: The pattern displaced by {displacement:.2f} units, indicating glider-like behavior."
    else:
        qualitative_desc += "- Static: The pattern did not show significant movement."

    summary_content = (
        f"Evolution Run Summary (iter 202.4)\n"
        f"========================================\n"
        f"Generations: {GENERATIONS}\n"
        f"Population Size: {POPULATION_SIZE}\n"
        f"Fitness Function: {FITNESS_FUNCTION.__class__.__name__}\n\n"
        f"Champion Final Fitness ({VALIDATION_STEPS} steps): {final_fitness}\n\n"
        f"{qualitative_desc}\n"
    )
    with open(summary_path, 'w') as f:
        f.write(summary_content)
    print(f"Summary written to {summary_path}")
    
    # --- 7. Final Report for Orchestrator ---
    report = {
        'status': 'ok',
        'artifacts': [champion_path, gif_path, summary_path],
        'metrics': {'final_fitness': float(final_fitness), 'displacement': float(displacement)},
        'log_excerpt': f"Champion validation fitness: {final_fitness}\nDisplacement: {displacement}",
        'experimenter_view': summary_content,
        'notes': "Evolution and validation process completed successfully."
    }
    with open('experiment_report.yaml', 'w') as f:
        yaml.dump(report, f)

    print("\n--- Task Complete ---")


if __name__ == "__main__":
    evolve_and_validate()
```

## 2. Final Output Specification

The script `src/run_evolution_202_4.py` will generate a file named `experiment_report.yaml`. The content of this file should be used as the final YAML output for this task. Ensure all specified artifacts are created and listed correctly.
