#!/usr/bin/env python3
"""
Re-evaluate fitness scores from iter_150 using a new composite metric.
New metric: new_fitness = total_displacement / (1 + std_dev)
"""

import csv
import numpy as np
from pathlib import Path

# Get the project root directory (parent of src)
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Read the CSV file
csv_path = project_root / "archive" / "iter_150" / "results" / "fitness_scores.csv"

rows = []
with open(csv_path, "r", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append({
            "rule_id": row["rule_id"],
            "total_displacement": float(row["total_displacement"]),
            "std_dev": float(row["std_dev"]),
            "fitness": float(row["fitness"]),
        })

# Calculate new fitness metric
new_fitnesses = []
for r in rows:
    new_fit = r["total_displacement"] / (1.0 + r["std_dev"])
    r["new_fitness"] = new_fit
    new_fitnesses.append(new_fit)

new_fitnesses = np.array(new_fitnesses, dtype=np.float64)

# Compute statistics
mean_fitness = float(np.mean(new_fitnesses))
max_fitness = float(np.max(new_fitnesses))
median_fitness = float(np.median(new_fitnesses))
std_fitness = float(np.std(new_fitnesses))
min_fitness = float(np.min(new_fitnesses))

# Find rule_086 and its new_fitness
rule_086_row = None
for r in rows:
    if r["rule_id"] == "rule_086":
        rule_086_row = r
        break

if rule_086_row is not None:
    new_fitness_rule_086 = rule_086_row["new_fitness"]
    original_fitness_rule_086 = rule_086_row["fitness"]
    total_disp_rule_086 = rule_086_row["total_displacement"]
    std_dev_rule_086 = rule_086_row["std_dev"]
else:
    new_fitness_rule_086 = None
    original_fitness_rule_086 = None
    total_disp_rule_086 = None
    std_dev_rule_086 = None

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
    if total_disp_rule_086 is not None:
        f.write(f"Total Displacement:       {total_disp_rule_086:.8f}\n")
        f.write(f"Std Dev:                  {std_dev_rule_086:.8f}\n")
    else:
        f.write(f"Total Displacement:       n/a\n")
        f.write(f"Std Dev:                  n/a\n")
    if new_fitness_rule_086 is not None:
        f.write(f"New Fitness Score:        {new_fitness_rule_086:.8f}\n\n")
    else:
        f.write(f"New Fitness Score:        n/a\n\n")

    f.write("Summary:\n")
    f.write("-" * 60 + "\n")
    f.write(f"Total rules evaluated: {len(df) if 'df' in locals() else len(rows)}\n")
    f.write(f"Mean new fitness: {mean_fitness:.8f}\n")
    if new_fitness_rule_086 is not None:
        count_ge = sum(1 for r in rows if r["new_fitness"] >= new_fitness_rule_086)
        f.write(f"Rule 086 new fitness ranking: {count_ge} rules with >= new_fitness\n")
    else:
        f.write(f"Rule 086 new fitness ranking: n/a\n")

print(f"Summary written to {summary_path}")
print(f"\nStatistics:")
print(f"  Mean fitness:        {mean_fitness:.8f}")
print(f"  Max fitness:         {max_fitness:.8f}")
print(f"  Median fitness:      {median_fitness:.8f}")
print(f"  Std deviation:       {std_fitness:.8f}")
print(f"\nRule 086:")
if original_fitness_rule_086 is not None:
    print(f"  Original fitness:    {original_fitness_rule_086:.8f}")
if new_fitness_rule_086 is not None:
    print(f"  New fitness:         {new_fitness_rule_086:.8f}")
