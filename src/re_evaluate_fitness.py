#!/usr/bin/env python3
"""
Re-evaluate fitness scores from iter_150 using a new composite metric.
New metric: new_fitness = total_displacement / (1 + std_dev)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

# Get the project root directory (parent of src)
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Read the CSV file
csv_path = project_root / "archive" / "iter_150" / "results" / "fitness_scores.csv"
df = pd.read_csv(csv_path)

# Calculate new fitness metric
df['new_fitness'] = df['total_displacement'] / (1 + df['std_dev'])

# Compute statistics
mean_fitness = df['new_fitness'].mean()
max_fitness = df['new_fitness'].max()
median_fitness = df['new_fitness'].median()
std_fitness = df['new_fitness'].std()
min_fitness = df['new_fitness'].min()

# Find rule_086 and its new_fitness
rule_086 = df[df['rule_id'] == 'rule_086']
if not rule_086.empty:
    new_fitness_rule_086 = rule_086['new_fitness'].values[0]
    original_fitness_rule_086 = rule_086['fitness'].values[0]
else:
    new_fitness_rule_086 = None
    original_fitness_rule_086 = None

# Create output directory
output_dir = project_root / "archive" / "iter_151" / "results"
output_dir.mkdir(parents=True, exist_ok=True)

# Write summary to file
summary_path = output_dir / "re_evaluation.txt"
with open(summary_path, "w") as f:
    f.write("Re-Evaluation of Fitness Scores from iter_150\n")
    f.write("=" * 60 + "\n\n")
    f.write("New Fitness Metric: new_fitness = total_displacement / (1 + std_dev)\n\n")

    f.write("Statistics for New Fitness Scores:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Mean:              {mean_fitness:.8f}\n")
    f.write(f"Maximum:           {max_fitness:.8f}\n")
    f.write(f"Median:            {median_fitness:.8f}\n")
    f.write(f"Standard Deviation: {std_fitness:.8f}\n")
    f.write(f"Minimum:           {min_fitness:.8f}\n\n")

    f.write("Analysis of rule_086 (highest original fitness):\n")
    f.write("-" * 60 + "\n")
    f.write(f"Rule ID:                  rule_086\n")
    f.write(f"Original Fitness:         {original_fitness_rule_086:.8f}\n")
    f.write(f"Total Displacement:       {rule_086['total_displacement'].values[0]:.8f}\n")
    f.write(f"Std Dev:                  {rule_086['std_dev'].values[0]:.8f}\n")
    f.write(f"New Fitness Score:        {new_fitness_rule_086:.8f}\n\n")

    f.write("Summary:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Total rules evaluated: {len(df)}\n")
    f.write(f"Mean new fitness: {mean_fitness:.8f}\n")
    f.write(f"Rule 086 new fitness ranking: {(df['new_fitness'] >= new_fitness_rule_086).sum()} rules with >= new_fitness\n")

print(f"Summary written to {summary_path}")
print(f"\nStatistics:")
print(f"  Mean fitness:        {mean_fitness:.8f}")
print(f"  Max fitness:         {max_fitness:.8f}")
print(f"  Median fitness:      {median_fitness:.8f}")
print(f"  Std deviation:       {std_fitness:.8f}")
print(f"\nRule 086:")
print(f"  Original fitness:    {original_fitness_rule_086:.8f}")
print(f"  New fitness:         {new_fitness_rule_086:.8f}")
