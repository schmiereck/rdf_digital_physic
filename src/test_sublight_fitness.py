#!/usr/bin/env python3
"""
test_sublight_fitness.py

Instantiates SubLightFitness and evaluates:
  1. The champion rule from iter_220 (champion_rule.json).
  2. A random 7-bit rule (to see how a random rule scores).

Prints the fitness score and reason for each evaluation so we can
verify the fitness function behaves exactly as expected.
"""

from __future__ import annotations

import json
import random
import sys
import os

# Make sure src/ is on the path so we can import from the project modules.
sys.path.insert(0, os.path.dirname(__file__))

from fitness_functions import SubLightFitness

# ---------------------------------------------------------------------------
# Helper: print metrics for any rule evaluation
# ---------------------------------------------------------------------------

def print_metrics(label: str, fitness: float, m: dict) -> None:
    print(f"  {label}")
    print(f"    fitness   = {fitness}")
    print(f"    reason    = {m['reason']}")
    if m["reason"] == "ok":
        print(f"    displacement = {m['displacement']:.4f}")
        print(f"    avg_velocity  = {m['avg_velocity']:.6f}")
        print(f"    period        = {m['period']}")
        print(f"    period_bonus  = {m['period_bonus']:.4f}")
        print(f"    final_bb_area = {m['final_bb_area']}")
        print(f"    initial_bits  = {m['initial_bits']}")
        print(f"    final_bits    = {m['final_bits']}")
    elif m["reason"] == "bit_conservation_failed":
        print(f"    initial_bits = {m['initial_bits']}")
        print(f"    final_bits   = {m['final_bits']}")
        print(f"    expected_bits= {m['expected_bits']}")
        if "step_failed" in m:
            print(f"    step_failed  = {m['step_failed']}")
    elif m["reason"] == "velocity_at_or_above_threshold":
        print(f"    displacement = {m['displacement']:.4f}")
        print(f"    avg_velocity = {m['avg_velocity']:.6f}")
        print(f"    v_threshold  = {m['v_threshold']}")
    elif m["reason"] == "no_displacement":
        print(f"    displacement = 0.0")
    elif m["reason"] == "period_too_short":
        print(f"    displacement = {m['displacement']:.4f}")
        print(f"    avg_velocity = {m['avg_velocity']:.6f}")
        print(f"    period       = {m['period']}")
    print()


# ---------------------------------------------------------------------------
# 1. Load the champion rule from iter_220
# ---------------------------------------------------------------------------

CHAMPION_PATH = os.path.join(
    os.path.dirname(__file__), "..", "archive", "iter_220", "results", "champion_rule.json"
)

with open(CHAMPION_PATH) as f:
    champion_data = json.load(f)

champion_rule_dict = champion_data["rule_dict"]

print("=" * 70)
print("Evaluating CHAMPION RULE (iter_220)")
print("=" * 70)
print(f"  rule_dict: {champion_rule_dict}")
print()

# Use the SubLightFitness defaults
fitness_fn = SubLightFitness()

fitness, metrics = fitness_fn(champion_rule_dict)
print_metrics("champion_rule", fitness, metrics)

# ---------------------------------------------------------------------------
# 2. Evaluate several random 7-bit rules
#    Configs (neighbourhood states) are 7-bit: 0..127.
#    The LUT maps config → output (also 0..127, then upper bit used).
# ---------------------------------------------------------------------------

def make_random_rule(seed: int, density: float = 0.10) -> dict:
    """Create a random rule dict with configs in [0,127] and outputs in [1,127]."""
    rng = random.Random(seed)
    rule_dict = {}
    for config in range(128):  # 7-bit neighbourhood: 0..127
        if rng.random() < density:
            rule_dict[str(config)] = rng.randint(1, 127)
    if not rule_dict:
        rule_dict["1"] = rng.randint(1, 127)
    return rule_dict


print("=" * 70)
print("Evaluating RANDOM RULES (7-bit neighbourhood)")
print("=" * 70)
print()

for i in range(1, 6):
    rule = make_random_rule(seed=i * 1000)
    print(f"  Random rule #{i} ({len(rule)} entries): {rule}")
    fitness, metrics = fitness_fn(rule)
    print_metrics(f"random_rule_{i}", fitness, metrics)

# ---------------------------------------------------------------------------
# 3. Evaluate a very sparse rule (1 config on) — should be trivial
# ---------------------------------------------------------------------------

print("=" * 70)
print("Evaluating A VERY SPARSE RULE (single config)")
print("=" * 70)

sparse_rule = {"3": 1}  # only config 3 → output 1
print(f"  sparse_rule: {sparse_rule}")
fitness, metrics = fitness_fn(sparse_rule)
print_metrics("sparse_rule", fitness, metrics)

# ---------------------------------------------------------------------------
# 4. Evaluate an "all zero" rule — everything stays dead
# ---------------------------------------------------------------------------

print("=" * 70)
print("Evaluating an ALL-ZERO RULE")
print("=" * 70)

zero_rule = {}  # all configs → 0 (implicit via LUT default)
print(f"  zero_rule: {zero_rule}  ({len(zero_rule)} entries)")
fitness, metrics = fitness_fn(zero_rule)
print_metrics("zero_rule", fitness, metrics)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print()
print(f"  SubLightFitness defaults: grid=128, steps=1200,")
print(f"    displacement window=[600,1000], period window=[600,800],")
print(f"    max_period=64, v_threshold=0.9")
print()
print("  The champion from iter_220 (trained with DisplacementConsistencyFitness)")
print("  FAILS bit conservation under SubLightFitness — it produces 4 bits")
print("  instead of the expected 3 (L-tromino). This is expected because the two")
print("  fitness functions enforce different conservation criteria.")
print()
print("  Random rules mostly fail bit conservation (chaotic explosion).")
print("  Only rules that preserve exactly 3 bits AND show sub-light periodic")
print("  motion will score > 0 under SubLightFitness.")
print()
print("=" * 70)
print("Done.")
print("=" * 70)
