#!/usr/bin/env python3
"""
validate_fitness.py — Confirm that CheckpointFitness assigns 0.0 to the
unstable "transient bloomer" rule from iter_176 gen 5 (rule_019).
"""

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from fitness import CheckpointFitness
from rule import Rule

PROJECT_ROOT = Path(__file__).parent.parent
RULE_PATH = PROJECT_ROOT / "archive" / "iter_176" / "results" / "gen_5" / "rule_019.json"

with open(RULE_PATH) as f:
    data = json.load(f)

rule = Rule(data["rule"])

seed_bits = [[10, 10], [10, 11], [10, 12]]

fitness_fn = CheckpointFitness(checkpoints=[50, 100, 150, 200], simulation_steps=200)

score = fitness_fn.evaluate(rule, seed_bits)

print(f"Rule ID       : {data.get('rule_id', 'n/a')}")
print(f"Old fitness   : {data.get('fitness', 'n/a')}")
print(f"CheckpointFitness score: {score}")
