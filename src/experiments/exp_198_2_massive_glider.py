"""
exp_198_2_massive_glider.py

Evolutionary search for a v<c glider using MassiveGliderFitness, which
penalises large/complex patterns to avoid the grid-filling and fizzler
exploits seen in previous iterations.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fitness import MassiveGliderFitness
from seeds import L_TROMINO_SEED

EXPERIMENT_CONFIG = {
    "name": "massive_glider_search",
    "notes": "Evolutionary search for a v<c glider using MassiveGliderFitness, which penalizes large/complex patterns.",
    "rule_space": "hex_1bit",
    "fitness_function": MassiveGliderFitness(steps=256, checkpoints=4),
    "seed": L_TROMINO_SEED,
    "population_size": 100,
    "generations": 10,
    "mutation_rate": 0.1,
    "cx_prob": 0.5,
    "num_elites": 2,
}
