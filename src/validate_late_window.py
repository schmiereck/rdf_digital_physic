#!/usr/bin/env python3
"""
Validate LateWindowDisplacementFitness against the champion rule that caused
the 'transient drift' exploit (from iter_213.10).

Steps:
1. Load champion rule from archive/iter_213.10/results/champion_rule.json
2. Use standard 3-bit L-Tromino seed
3. Run simulation (default 1001 steps so that window_end=1000 is captured)
4. Evaluate with LateWindowDisplacementFitness
5. Assert fitness == 0.0 (success criterion)
6. Write results to archive/iter_214/results/validation.txt
"""

import json
import sys
import os

# Ensure src is on the path
src_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, src_dir)

project_dir = os.path.dirname(src_dir)

from fitness_v_lessthan_c import LateWindowDisplacementFitness, LTROMINO

# ---- Step 1: Load champion rule ----
champion_path = os.path.join(
    project_dir, "archive", "iter_213.10", "results", "champion_rule.json"
)
with open(champion_path, "r") as f:
    champion = json.load(f)

rule_dict = champion["rule_dict"]
iteration_label = champion.get("iteration", "unknown")
print(f"Loaded champion rule from {iteration_label}")
print(f"  rule_dict keys: {sorted(rule_dict.keys())}")

# ---- Step 2: Use standard 3-bit L-Tromino seed ----
seed = LTROMINO
print(f"\nUsing seed (3-bit L-tromino): {seed}")

# ---- Step 3 & 4: Run simulation and evaluate with LateWindowDisplacementFitness ----
# The LateWindowDisplacementFitness uses simulation_steps=1001 by default,
# with window [500, 1000]. This ensures both window_start and window_end
# fall within the simulation range.
fitness_eval = LateWindowDisplacementFitness(
    grid_size=128,
    simulation_steps=1001,
    window_start=500,
    window_end=1000,
    particle=seed,
    expected_bits=3,
)

fitness_score, metrics = fitness_eval(rule_dict)

print(f"\nFitness evaluation result:")
print(f"  fitness:                    {fitness_score}")
print(f"  reason:                     {metrics.get('reason', 'N/A')}")
print(f"  window_start_com:           {metrics.get('window_start_com', 'N/A')}")
print(f"  window_end_com:             {metrics.get('window_end_com', 'N/A')}")
print(f"  late_window_displacement:   {metrics.get('late_window_displacement', 'N/A')}")
print(f"  final_bb_area:              {metrics.get('final_bb_area', 'N/A')}")
print(f"  initial_bits:               {metrics.get('initial_bits', 'N/A')}")
print(f"  final_bits:                 {metrics.get('final_bits', 'N/A')}")

# ---- Step 5: Check success criterion ----
print(f"\n--- SUCCESS CRITERION CHECK ---")
print(f"Expected fitness: 0.0")
print(f"Actual fitness:   {fitness_score}")

if fitness_score == 0.0:
    success = True
    msg = "SUCCESS: LateWindowDisplacementFitness returned fitness 0.0 for the transient drift exploit rule."
else:
    success = False
    msg = f"FAILURE: LateWindowDisplacementFitness returned fitness {fitness_score} (expected 0.0). The transient drift exploit was NOT neutralized!"

if not success:
    print(f"\n>>> VALIDATION FAILED <<<")
    sys.exit(1)
else:
    print(f"\n>>> VALIDATION PASSED <<<")

# ---- Step 6: Write results to archive/iter_214/results/validation.txt ----
output_dir = os.path.join(project_dir, "archive", "iter_214", "results")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "validation.txt")

report_lines = [
    f"Validation Report: LateWindowDisplacementFitness",
    f"{'='*55}",
    f"",
    f"Rule source:    archive/iter_213.10/results/champion_rule.json",
    f"Champion iter:  {iteration_label}",
    f"Seed:           3-bit L-tromino {seed}",
    f"Simulation:     {fitness_eval.simulation_steps} steps, grid_size={fitness_eval.grid_size}",
    f"Late window:    [{fitness_eval.window_start}, {fitness_eval.window_end}]",
    f"",
    f"Results:",
    f"  fitness:                    {fitness_score}",
    f"  reason:                     {metrics.get('reason', 'N/A')}",
    f"  window_start_com:           {metrics.get('window_start_com', 'N/A')}",
    f"  window_end_com:             {metrics.get('window_end_com', 'N/A')}",
    f"  late_window_displacement:   {metrics.get('late_window_displacement', 'N/A')}",
    f"  final_bb_area:              {metrics.get('final_bb_area', 'N/A')}",
    f"  initial_bits:               {metrics.get('initial_bits', 'N/A')}",
    f"  final_bits:                 {metrics.get('final_bits', 'N/A')}",
    f"",
    f"Verdict:",
]

if success:
    report_lines.append(f"  SUCCESS: fitness == 0.0")
    report_lines.append(f"  The LateWindowDisplacementFitness correctly suppresses the")
    report_lines.append(f"  'transient drift' exploit from iter_213.")
else:
    report_lines.append(f"  FAILURE: fitness == {fitness_score} (expected 0.0)")
    report_lines.append(f"  The exploit is NOT neutralized!")

report_lines.append(f"")

with open(output_path, "w") as f:
    f.write("\n".join(report_lines) + "\n")

print(f"\nResults written to: {output_path}")
print(f"\n{'='*55}")
print(msg)
print(f"{'='*55}")
