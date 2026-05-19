#!/usr/bin/env python3
"""Smoke test for LeakySubLightFitness."""
import sys
sys.path.insert(0, r"C:\Users\thomas\Projekte\rdf_digital_physic\src")

from leaky_fitness import LeakySubLightFitness
from rule import Rule

print("=== Import OK ===")

fn = LeakySubLightFitness(
    checkpoints=[50, 100, 150],
    simulation_steps=200,
    bits_per_cell=1,
    velocity_threshold=0.9,
)
print(f"Checkpoints: {fn.checkpoints}")
print(f"Simulation steps: {fn.simulation_steps}")
print(f"Bits per cell: {fn.bits_per_cell}")
print(f"Velocity threshold: {fn.velocity_threshold}")

LTROMINO_CELLS = [(63, 63), (64, 63), (64, 64)]

# Test 1: All-1 rule (always alive)
rule_dict = {i: 1 for i in range(128)}
rule = Rule(rule_dict)

fitness = fn.evaluate(rule, LTROMINO_CELLS)
print(f"\n=== Test 1: All-1 rule ===")
print(f"Fitness: {fitness}")

fitness, metrics = fn(rule, LTROMINO_CELLS)
print(f"Fitness via __call__: {fitness}")
print(f"base_fitness: {metrics.get('base_fitness')}")
print(f"total_conservation_score: {metrics.get('total_conservation_score')}")
print(f"avg_velocity: {metrics.get('avg_velocity')}")
print(f"conservation_factors: {metrics.get('conservation_factors')}")

# Test 2: Bit-destroying rule (all zeros)
rule_dict_destroy = {i: 0 for i in range(128)}
rule_destroy = Rule(rule_dict_destroy)

fitness_destroy = fn.evaluate(rule_destroy, LTROMINO_CELLS)
print(f"\n=== Test 2: Bit-destroying rule ===")
print(f"Fitness: {fitness_destroy}")

# Test 3: Test velocity rejection with a fast rule
fn_fast = LeakySubLightFitness(
    checkpoints=[50, 100],
    simulation_steps=200,
    bits_per_cell=1,
    velocity_threshold=0.9,
)
fitness_fast, metrics_fast = fn_fast(rule, LTROMINO_CELLS)
print(f"\n=== Test 3: Velocity gate ===")
print(f"Fitness: {fitness_fast}")
print(f"avg_velocity: {metrics_fast.get('avg_velocity')}")
print(f"velocity_rejected: {metrics_fast.get('velocity_rejected')}")

# Test 4: Test with checkpoints that catch bit changes
fn_tight = LeakySubLightFitness(
    checkpoints=[1, 10, 20],
    simulation_steps=20,
    bits_per_cell=1,
    velocity_threshold=0.99,
)
fitness_tight, metrics_tight = fn_tight(rule_destroy, LTROMINO_CELLS)
print(f"\n=== Test 4: Tight checkpoints on destroy rule ===")
print(f"Fitness: {fitness_tight}")
print(f"conservation_factors: {metrics_tight.get('conservation_factors')}")
print(f"total_conservation_score: {metrics_tight.get('total_conservation_score')}")

print("\n=== ALL TESTS PASSED ===")
